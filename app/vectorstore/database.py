import os
import logging
from typing import List, Optional
from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# Configura logger básico
logger = logging.getLogger(__name__)

load_dotenv()

class GeminiAPIKeyManager:
    """
    Gerencia uma lista de chaves de API do Gemini para permitir fallback e rotação automática
    caso ocorram limites de taxa (Rate Limit) ou quotas excedidas.
    """
    def __init__(self, api_keys: Optional[List[str]] = None):
        """
        Inicializa o gerenciador com uma lista de chaves de API ou lê do ambiente.
        
        Args:
            api_keys: Opcional. Lista explícita de chaves. Se omitida, tentará ler
                      do ambiente através de GEMINI_API_KEYS ou GEMINI_API_KEY.
        """
        if api_keys:
            self._api_keys = [k.strip() for k in api_keys if k.strip()]
        else:
            self._api_keys = []
            
            # Tenta carregar do env GEMINI_API_KEYS (lista separada por vírgulas)
            env_keys = os.getenv("GEMINI_API_KEYS")
            if env_keys:
                self._api_keys = [k.strip() for k in env_keys.split(",") if k.strip()]
                
            # Fallback para a chave única tradicional GEMINI_API_KEY se a lista estiver vazia
            if not self._api_keys:
                single_key = os.getenv("GEMINI_API_KEY")
                if single_key:
                    # Permite que a chave GEMINI_API_KEY também seja informada como lista separada por vírgula
                    self._api_keys = [k.strip() for k in single_key.split(",") if k.strip()]
                    
        self._current_index = 0
        if not self._api_keys:
            logger.warning("Nenhuma chave de API do Gemini foi configurada no sistema.")

    @property
    def current_key(self) -> str:
        """Retorna a chave de API atualmente selecionada."""
        if not self._api_keys:
            raise ValueError("Não há chaves de API configuradas no GeminiAPIKeyManager.")
        return self._api_keys[self._current_index]

    def rotate_key(self) -> str:
        """
        Rotaciona para a próxima chave de API disponível na lista.
        
        Returns:
            A nova chave de API selecionada.
        """
        if not self._api_keys:
            raise ValueError("Não há chaves de API disponíveis para rotacionar.")
            
        if len(self._api_keys) <= 1:
            logger.info("Apenas uma chave de API está disponível. Nenhuma rotação ocorreu.")
            return self.current_key
            
        self._current_index = (self._current_index + 1) % len(self._api_keys)
        logger.info(f"Chave de API rotacionada com sucesso. Nova chave de índice: {self._current_index}")
        return self.current_key

    @property
    def has_keys(self) -> bool:
        """Retorna True se houver pelo menos uma chave configurada."""
        return len(self._api_keys) > 0

    @property
    def count(self) -> int:
        """Retorna a quantidade total de chaves registradas."""
        return len(self._api_keys)


class FallbackGeminiEmbeddings(Embeddings):
    """
    Implementação da interface de Embeddings do LangChain com suporte integrado a fallback
    e rotação automática de chaves do Gemini caso ocorram falhas durante a chamada.
    """
    def __init__(self, key_manager: GeminiAPIKeyManager, model_name: str = "models/gemini-embedding-001"):
        """
        Inicializa o gerador de embeddings.
        
        Args:
            key_manager: Gerenciador de chaves de API.
            model_name: Nome do modelo de embeddings do Gemini.
        """
        self.key_manager = key_manager
        self.model_name = model_name
        self.embeddings = None
        self._init_embeddings()

    def _init_embeddings(self) -> None:
        """Inicializa ou atualiza o objeto interno do LangChain com a chave ativa."""
        if not self.key_manager.has_keys:
            raise ValueError("Incapaz de inicializar embeddings: nenhuma chave de API do Gemini disponível.")
            
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=self.model_name,
            google_api_key=self.key_manager.current_key
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings para uma lista de textos, aplicando retentativas e rotação se falhar.
        """
        import time
        attempts = 0
        max_attempts = max(self.key_manager.count, 1)
        last_error = None
        
        while attempts < max_attempts:
            if not self.embeddings:
                self._init_embeddings()
                
            local_retries = 3
            backoff_delay = 2.0
            
            while local_retries > 0:
                try:
                    return self.embeddings.embed_documents(texts)
                except Exception as e:
                    err_str = str(e)
                    # Se for limite de cota/autorização e temos outras chaves, rotacionamos sem gastar retentativas locais
                    if ("RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "403" in err_str) and self.key_manager.count > 1:
                        break
                        
                    local_retries -= 1
                    last_error = e
                    if local_retries > 0:
                        logger.warning(
                            f"Falha temporária nos embeddings (Tentativas locais restantes: {local_retries}). "
                            f"Aguardando {backoff_delay}s antes de tentar novamente. Erro: {err_str}"
                        )
                        time.sleep(backoff_delay)
                        backoff_delay *= 2
                    else:
                        logger.warning(f"Esgotadas as retentativas locais para a chave atual. Erro: {err_str}")
            
            attempts += 1
            if attempts < max_attempts:
                self.key_manager.rotate_key()
                self._init_embeddings()
                
        raise last_error

    def embed_query(self, text: str) -> List[float]:
        """
        Gera embeddings para uma única string de consulta (query), aplicando retentativas e rotação se falhar.
        """
        import time
        attempts = 0
        max_attempts = max(self.key_manager.count, 1)
        last_error = None
        
        while attempts < max_attempts:
            if not self.embeddings:
                self._init_embeddings()
                
            local_retries = 3
            backoff_delay = 2.0
            
            while local_retries > 0:
                try:
                    return self.embeddings.embed_query(text)
                except Exception as e:
                    err_str = str(e)
                    if ("RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "403" in err_str) and self.key_manager.count > 1:
                        break
                        
                    local_retries -= 1
                    last_error = e
                    if local_retries > 0:
                        logger.warning(
                            f"Falha temporária no embedding da query (Tentativas locais restantes: {local_retries}). "
                            f"Aguardando {backoff_delay}s antes de tentar novamente. Erro: {err_str}"
                        )
                        time.sleep(backoff_delay)
                        backoff_delay *= 2
                    else:
                        logger.warning(f"Esgotadas as retentativas locais para a chave atual. Erro: {err_str}")
            
            attempts += 1
            if attempts < max_attempts:
                self.key_manager.rotate_key()
                self._init_embeddings()
                
        raise last_error


# Singleton/Instância compartilhada do gerenciador de chaves
_key_manager_instance: Optional[GeminiAPIKeyManager] = None

def get_key_manager() -> GeminiAPIKeyManager:
    """Retorna a instância compartilhada do gerenciador de chaves."""
    global _key_manager_instance
    if _key_manager_instance is None:
        _key_manager_instance = GeminiAPIKeyManager()
    return _key_manager_instance

def get_embedding_model() -> FallbackGeminiEmbeddings:
    """
    Cria e retorna a instância de embeddings configurada com suporte a fallback.
    """
    key_manager = get_key_manager()
    return FallbackGeminiEmbeddings(key_manager=key_manager)

def get_vectorstore() -> Chroma:
    """
    Retorna a instância do ChromaDB configurada com os embeddings suportados por fallback.
    """
    chroma_db_path = os.getenv("CHROMA_DB_PATH", "data/db")
    embeddings = get_embedding_model()
    
    return Chroma(
        collection_name="brasil_copa_2026",
        embedding_function=embeddings,
        persist_directory=chroma_db_path
    )
