import os
import pytest
from unittest.mock import MagicMock, patch
from app.vectorstore.database import GeminiAPIKeyManager, FallbackGeminiEmbeddings

def test_key_manager_initialization_list():
    keys = ["key1", "key2", "   key3   "]
    manager = GeminiAPIKeyManager(api_keys=keys)
    assert manager.count == 3
    assert manager.current_key == "key1"
    
    assert manager.rotate_key() == "key2"
    assert manager.current_key == "key2"
    
    assert manager.rotate_key() == "key3"
    assert manager.current_key == "key3"
    
    assert manager.rotate_key() == "key1"
    assert manager.current_key == "key1"

def test_key_manager_initialization_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEYS", "env_key1, env_key2")
    manager = GeminiAPIKeyManager()
    assert manager.count == 2
    assert manager.current_key == "env_key1"
    assert manager.rotate_key() == "env_key2"

def test_key_manager_single_fallback_env(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEYS", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "single_key")
    manager = GeminiAPIKeyManager()
    assert manager.count == 1
    assert manager.current_key == "single_key"
    # A rotação em chave única deve manter a mesma chave
    assert manager.rotate_key() == "single_key"

@patch("app.vectorstore.database.GoogleGenerativeAIEmbeddings")
def test_fallback_embeddings_rotation(mock_google_embeddings):
    # Configura chaves no manager
    keys = ["bad_key1", "bad_key2", "good_key"]
    manager = GeminiAPIKeyManager(api_keys=keys)
    
    # Criamos instâncias mocks correspondentes para cada chamada de inicialização
    mock_instance1 = MagicMock()
    mock_instance1.embed_query.side_effect = Exception("Auth Error 1")
    
    mock_instance2 = MagicMock()
    mock_instance2.embed_query.side_effect = Exception("Auth Error 2")
    
    mock_instance3 = MagicMock()
    mock_instance3.embed_query.return_value = [0.1, 0.2, 0.3]
    
    # Configura o construtor mockado do GoogleGenerativeAIEmbeddings
    # para retornar os mocks sequencialmente
    mock_google_embeddings.side_effect = [mock_instance1, mock_instance2, mock_instance3]
    
    # Inicializa o FallbackGeminiEmbeddings
    fallback_emb = FallbackGeminiEmbeddings(key_manager=manager)
    
    # Verifica a chave inicial
    assert manager.current_key == "bad_key1"
    
    # Executa a chamada. Ela deve falhar 2 vezes, rodar as chaves, e ter sucesso na 3ª vez
    result = fallback_emb.embed_query("teste")
    
    assert result == [0.1, 0.2, 0.3]
    assert manager.current_key == "good_key"
    assert mock_google_embeddings.call_count == 3

@patch("app.vectorstore.database.GoogleGenerativeAIEmbeddings")
def test_fallback_embeddings_exhaustion(mock_google_embeddings):
    keys = ["bad_key1", "bad_key2"]
    manager = GeminiAPIKeyManager(api_keys=keys)
    
    mock_instance = MagicMock()
    mock_instance.embed_query.side_effect = Exception("API quota exceeded")
    
    mock_google_embeddings.return_value = mock_instance
    
    fallback_emb = FallbackGeminiEmbeddings(key_manager=manager)
    
    # Executa a chamada e garante que lança o erro final quando esgotadas as chaves
    with pytest.raises(Exception) as excinfo:
        fallback_emb.embed_query("teste")
        
    assert "API quota exceeded" in str(excinfo.value)
    # Deve tentar 2 vezes (número de chaves)
    assert manager.current_key == "bad_key2"
