import pytest
from unittest.mock import MagicMock, patch
from app.rag.llm import FallbackChatGemini
from app.vectorstore.database import GeminiAPIKeyManager

@patch("app.rag.llm.ChatGoogleGenerativeAI")
def test_fallback_chat_gemini_success(mock_chat_class):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = "Resposta fictícia"
    mock_chat_class.return_value = mock_llm
    
    key_manager = GeminiAPIKeyManager(api_keys=["key1", "key2"])
    fallback_chat = FallbackChatGemini(key_manager=key_manager, model="gemini-1.5-flash")
    
    res = fallback_chat.invoke("Olá")
    
    assert res == "Resposta fictícia"
    assert key_manager.current_key == "key1"
    mock_llm.invoke.assert_called_once()

@patch("app.rag.llm.ChatGoogleGenerativeAI")
def test_fallback_chat_gemini_rotation(mock_chat_class):
    mock_llm_fail = MagicMock()
    mock_llm_fail.invoke.side_effect = Exception("RESOURCE_EXHAUSTED: Quota exceeded")
    
    mock_llm_success = MagicMock()
    mock_llm_success.invoke.return_value = "Resposta de sucesso"
    
    # Retorna o LLM falho na primeira inicialização, e o de sucesso na segunda (após rotação)
    mock_chat_class.side_effect = [mock_llm_fail, mock_llm_success]
    
    key_manager = GeminiAPIKeyManager(api_keys=["key1", "key2"])
    fallback_chat = FallbackChatGemini(key_manager=key_manager, model="gemini-1.5-flash")
    
    res = fallback_chat.invoke("Olá")
    
    assert res == "Resposta de sucesso"
    # A chave foi rotacionada para a segunda chave disponível
    assert key_manager.current_key == "key2"

@patch("app.rag.llm.ChatGoogleGenerativeAI")
@patch("time.sleep", return_value=None)  # Evita atrasar a execução do teste
def test_fallback_chat_gemini_local_retry(mock_sleep, mock_chat_class):
    mock_llm = MagicMock()
    # Duas falhas temporárias (ex: timeout de rede) seguidas de um retorno bem sucedido
    mock_llm.invoke.side_effect = [
        Exception("Timeout connecting to server"),
        Exception("Timeout connecting to server"),
        "Sucesso local"
    ]
    mock_chat_class.return_value = mock_llm
    
    key_manager = GeminiAPIKeyManager(api_keys=["key1", "key2"])
    fallback_chat = FallbackChatGemini(key_manager=key_manager, model="gemini-1.5-flash")
    
    res = fallback_chat.invoke("Olá")
    
    assert res == "Sucesso local"
    # Não rotacionou, pois o erro temporário foi resolvido localmente na primeira chave
    assert key_manager.current_key == "key1"
    assert mock_llm.invoke.call_count == 3
