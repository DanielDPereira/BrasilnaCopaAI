import os
import logging
from typing import List, Optional
from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

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
        self._cooldowns = {} # key -> float (timestamp em segundos quando o cooldown termina)
        if not self._api_keys:
            logger.warning("Nenhuma chave de API do Gemini foi configurada no sistema.")

    def mark_exhausted(self, key: str, duration: float = 3600) -> None:
        """Marca uma chave como esgotada/inativa por um determinado período em segundos (default 1h)."""
        import time
        self._cooldowns[key] = time.time() + duration
        logger.warning(f"Chave de API {key[:10]}... marcada como temporariamente inativa/esgotada por {duration}s.")

    def is_active(self, key: str) -> bool:
        """Retorna True se a chave não está em período de cooldown."""
        import time
        cooldown_end = self._cooldowns.get(key, 0.0)
        return time.time() > cooldown_end

    @property
    def active_keys(self) -> List[str]:
        """Retorna a lista de chaves atualmente ativas (fora do cooldown)."""
        active = [k for k in self._api_keys if self.is_active(k)]
        if not active:
            # Se todas as chaves estão sob cooldown, retorna todas como fallback
            # para evitar travamento total caso alguma chave recupere a quota mais cedo
            return self._api_keys
        return active

    @property
    def current_key(self) -> str:
        """Retorna a chave de API atualmente selecionada, ajustando para uma chave ativa se necessário."""
        if not self._api_keys:
            raise ValueError("Não há chaves de API configuradas no GeminiAPIKeyManager.")
            
        active = self.active_keys
        current = self._api_keys[self._current_index]
        if current not in active:
            # Seleciona a primeira chave ativa disponível
            for i, key in enumerate(self._api_keys):
                if key in active:
                    self._current_index = i
                    break
        return self._api_keys[self._current_index]

    def rotate_key(self) -> str:
        """
        Rotaciona para a próxima chave de API ativa disponível na lista.
        
        Returns:
            A nova chave de API selecionada.
        """
        if not self._api_keys:
            raise ValueError("Não há chaves de API disponíveis para rotacionar.")
            
        active = self.active_keys
        if len(active) <= 1:
            # Se só há uma chave ativa, seleciona ela e retorna
            if active:
                for i, key in enumerate(self._api_keys):
                    if key == active[0]:
                        self._current_index = i
                        break
            return self.current_key
            
        # Busca a próxima chave ativa a partir da atual
        next_index = self._current_index
        for _ in range(len(self._api_keys)):
            next_index = (next_index + 1) % len(self._api_keys)
            if self._api_keys[next_index] in active:
                self._current_index = next_index
                logger.info(f"Chave de API rotacionada para ativa. Novo índice: {self._current_index}")
                return self.current_key
                
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
    def __init__(self, key_manager: GeminiAPIKeyManager, model_name: str = "models/gemini-embedding-2"):
        """
        Inicializa o gerador de embeddings.
        
        Args:
            key_manager: Gerenciador de chaves de API.
            model_name: Nome do modelo de embeddings do Gemini.
        """
        self.key_manager = key_manager
        self.primary_model = model_name
        self.fallback_model = "models/gemini-embedding-001" if model_name == "models/gemini-embedding-2" else None
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
                    last_error = e
                    # Se for limite de cota/autorização e temos outras chaves, marca como esgotada e rotaciona
                    if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "403" in err_str:
                        logger.warning(f"DEBUG: Catching rate limit error: {err_str}")
                        is_daily = any(x in err_str.lower() for x in ["limit: 1000", "requestsperday", "perday"])
                        cooldown = 3600 if is_daily else 10
                        self.key_manager.mark_exhausted(self.key_manager.current_key, duration=cooldown)
                        if self.key_manager.count > 1:
                            break
                        
                    local_retries -= 1
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
                
        # Se esgotamos as chaves para o modelo principal, tenta o modelo de fallback
        if self.model_name == self.primary_model and self.fallback_model:
            logger.warning(
                f"Todos os limites atingidos para o modelo {self.primary_model}. "
                f"Ativando modelo de fallback: {self.fallback_model}"
            )
            self.model_name = self.fallback_model
            # Limpa os cooldowns das chaves para permitir usá-las com o novo modelo
            self.key_manager._cooldowns.clear()
            self._init_embeddings()
            return self.embed_documents(texts)
            
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
                    last_error = e
                    if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "403" in err_str:
                        is_daily = any(x in err_str.lower() for x in ["limit: 1000", "requestsperday", "perday"])
                        cooldown = 3600 if is_daily else 10
                        self.key_manager.mark_exhausted(self.key_manager.current_key, duration=cooldown)
                        if self.key_manager.count > 1:
                            break
                        
                    local_retries -= 1
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
                
        # Se esgotamos as chaves para o modelo principal, tenta o modelo de fallback
        if self.model_name == self.primary_model and self.fallback_model:
            logger.warning(
                f"Todos os limites atingidos para o modelo {self.primary_model}. "
                f"Ativando modelo de fallback: {self.fallback_model}"
            )
            self.model_name = self.fallback_model
            # Limpa os cooldowns das chaves para permitir usá-las com o novo modelo
            self.key_manager._cooldowns.clear()
            self._init_embeddings()
            return self.embed_query(text)
            
        raise last_error


# Singleton/Instância compartilhada do gerenciador de chaves
_key_manager_instance: Optional[GeminiAPIKeyManager] = None

def get_key_manager() -> GeminiAPIKeyManager:
    """Retorna a instância compartilhada do gerenciador de chaves."""
    global _key_manager_instance
    if _key_manager_instance is None:
        _key_manager_instance = GeminiAPIKeyManager()
    return _key_manager_instance

class LocalONNXEmbeddings(Embeddings):
    """
    Implementação dos Embeddings usando o modelo local paraphrase-multilingual-MiniLM-L12-v2 em formato ONNX.
    Não requer internet, chaves de API ou possui limites de quota.
    """
    def __init__(self):
        import onnxruntime as ort
        from tokenizers import Tokenizer
        import numpy as np
        
        # Caminhos padrão para o modelo local
        self.model_path = os.path.abspath("data/models/paraphrase-multilingual-MiniLM-L12-v2/model.onnx")
        self.tokenizer_path = os.path.abspath("data/models/paraphrase-multilingual-MiniLM-L12-v2/tokenizer.json")
        
        if not os.path.exists(self.model_path) or not os.path.exists(self.tokenizer_path):
            raise FileNotFoundError(
                "Modelo local ONNX paraphrase-multilingual-MiniLM-L12-v2 não encontrado. "
                "Execute o script de download em 'scratch/download_local_model.py' primeiro."
            )
            
        self.tokenizer = Tokenizer.from_file(self.tokenizer_path)
        # Configura as opções do session para silenciar logs do ONNX Runtime
        opts = ort.SessionOptions()
        opts.log_severity_level = 3
        self.session = ort.InferenceSession(self.model_path, sess_options=opts)

    def _embed(self, texts: List[str]) -> List[List[float]]:
        import numpy as np
        # Tokeniza os textos
        encoded = [self.tokenizer.encode(t) for t in texts]
        
        # Padding para tamanho máximo da sequência no lote
        max_len = max(len(e.ids) for e in encoded)
        
        input_ids = []
        attention_mask = []
        token_type_ids = []
        
        for e in encoded:
            padding_len = max_len - len(e.ids)
            input_ids.append(e.ids + [0] * padding_len)
            attention_mask.append(e.attention_mask + [0] * padding_len)
            token_type_ids.append(e.type_ids + [0] * padding_len)
            
        input_ids = np.array(input_ids, dtype=np.int64)
        attention_mask = np.array(attention_mask, dtype=np.int64)
        token_type_ids = np.array(token_type_ids, dtype=np.int64)
        
        # Executa a inferência ONNX
        ort_inputs = {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'token_type_ids': token_type_ids
        }
        
        outputs = self.session.run(None, ort_inputs)
        token_embeddings = outputs[0]  # last_hidden_state de shape [batch_size, seq_len, 384]
        
        # Mean pooling
        input_mask_expanded = np.expand_dims(attention_mask, axis=-1)
        sum_embeddings = np.sum(token_embeddings * input_mask_expanded, axis=1)
        sum_mask = np.clip(np.sum(input_mask_expanded, axis=1), a_min=1e-9, a_max=None)
        embeddings = sum_embeddings / sum_mask
        
        # Normalização L2
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms
        
        return embeddings.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Processa em lotes pequenos para evitar alto consumo de memória se a lista for gigante
        batch_size = 64
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            all_embeddings.extend(self._embed(batch))
        return all_embeddings

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text])[0]


_embedding_model_instance: Optional[Embeddings] = None
_vectorstore_instance: Optional[Chroma] = None

def get_embedding_model() -> Embeddings:
    """
    Cria e retorna a instância de embeddings configurada (Local ONNX ou Gemini Fallback).
    """
    global _embedding_model_instance
    if _embedding_model_instance is None:
        if os.getenv("USE_LOCAL_EMBEDDINGS", "").lower() == "true":
            logger.info("Usando embeddings locais (paraphrase-multilingual-MiniLM-L12-v2 ONNX)")
            _embedding_model_instance = LocalONNXEmbeddings()
        else:
            key_manager = get_key_manager()
            _embedding_model_instance = FallbackGeminiEmbeddings(key_manager=key_manager)
    return _embedding_model_instance

def get_vectorstore() -> Chroma:
    """
    Retorna a instância do ChromaDB configurada com os embeddings suportados por fallback.
    """
    global _vectorstore_instance
    if _vectorstore_instance is None:
        chroma_db_path = os.getenv("CHROMA_DB_PATH", "data/db")
        embeddings = get_embedding_model()
        _vectorstore_instance = Chroma(
            collection_name="brasil_copa_2026",
            embedding_function=embeddings,
            persist_directory=chroma_db_path
        )
    return _vectorstore_instance
