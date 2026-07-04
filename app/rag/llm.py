import time
import logging
from typing import Any, List, Optional
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from app.vectorstore.database import GeminiAPIKeyManager

logger = logging.getLogger(__name__)

class FallbackChatGemini(Runnable):
    """
    Classe wrapper para ChatGoogleGenerativeAI que adiciona suporte a fallback/rotação de chaves
    de API e retentativas automáticas com backoff exponencial.
    """
    def __init__(self, key_manager: GeminiAPIKeyManager, model: str = "gemini-2.5-flash", **kwargs):
        """
        Inicializa o chat wrapper.
        
        Args:
            key_manager: Gerenciador de chaves de API.
            model: Nome do modelo de linguagem (LLM) do Gemini. Padrão: gemini-2.5-flash.
            kwargs: Argumentos extras passados para a instanciação do ChatGoogleGenerativeAI (ex: temperature).
        """
        self.key_manager = key_manager
        self.model = model
        self.kwargs = kwargs
        self.llm = None
        self._init_llm()

    def _init_llm(self) -> None:
        """Inicializa ou re-inicializa o modelo do LangChain com a chave ativa atual."""
        if not self.key_manager.has_keys:
            raise ValueError("Incapaz de inicializar LLM: nenhuma chave de API do Gemini disponível.")
            
        self.llm = ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.key_manager.current_key,
            **self.kwargs
        )

    def invoke(self, input: Any, config: Optional[RunnableConfig] = None) -> Any:
        """
        Invoca o modelo do Gemini, aplicando retentativas e rotação se falhar.
        """
        attempts = 0
        max_attempts = max(self.key_manager.count, 1)
        last_error = None
        
        while attempts < max_attempts:
            if not self.llm:
                self._init_llm()
                
            local_retries = 3
            backoff_delay = 2.0
            
            while local_retries > 0:
                try:
                    return self.llm.invoke(input, config)
                except Exception as e:
                    err_str = str(e)
                    # Se for erro de cota (429/RESOURCE_EXHAUSTED) ou acesso (403), rotacionamos chave imediatamente se tivermos outras
                    if ("RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "403" in err_str) and self.key_manager.count > 1:
                        break
                        
                    local_retries -= 1
                    last_error = e
                    if local_retries > 0:
                        logger.warning(
                            f"Falha temporária na chamada de Chat LLM (Tentativas locais restantes: {local_retries}). "
                            f"Erro: {err_str}. Retentando em {backoff_delay}s..."
                        )
                        time.sleep(backoff_delay)
                        backoff_delay *= 2.0
            
            # Se estourou retentativas locais ou caiu no break de cota, tentamos a próxima chave
            if self.key_manager.count > 1:
                old_key_prefix = self.key_manager.current_key[:8] if self.key_manager.current_key else "None"
                self.key_manager.rotate_key()
                new_key_prefix = self.key_manager.current_key[:8] if self.key_manager.current_key else "None"
                logger.warning(
                    f"Rotacionando chave de API do Gemini devido a erro persistente. "
                    f"Chave anterior: {old_key_prefix}... -> Nova chave: {new_key_prefix}..."
                )
                self._init_llm()
            else:
                # Se só temos 1 chave e falhou localmente, encerra
                break
                
            attempts += 1
            
        raise last_error

def get_llm(temperature: float = 0.0, model: str = "gemini-2.5-flash") -> FallbackChatGemini:
    """
    Retorna a instância da LLM resiliente pré-configurada.
    """
    key_manager = GeminiAPIKeyManager()
    return FallbackChatGemini(
        key_manager=key_manager,
        model=model,
        temperature=temperature,
        top_p=0.95
    )
