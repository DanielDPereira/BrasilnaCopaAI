from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from langchain_core.documents import Document
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    # Mock do database para evitar chamadas reais durante o teste
    with patch("app.vectorstore.database.get_vectorstore") as mock_get_db:
        mock_db = MagicMock()
        mock_db._collection.count.return_value = 502
        mock_get_db.return_value = mock_db
        
        response = client.get("/health")
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["status"] == "healthy"
        assert "connected (502 chunks)" in json_data["database"]

def test_chat_endpoint_success():
    with patch("app.main.RAGPipeline") as mock_pipeline_class:
        mock_pipeline = MagicMock()
        # Mock do retriever e do gerador de respostas
        mock_pipeline.retrieve_context.return_value = [
            Document(
                page_content="O Brasil venceu a Copa de 1958.",
                metadata={"title": "Copa de 1958", "url": "https://example.com/1958"}
            ),
            Document(
                page_content="Pelé brilhou em 1958.",
                metadata={"title": "Copa de 1958", "url": "https://example.com/1958"}  # URL duplicada para testar filtro
            )
        ]
        mock_pipeline.ask.return_value = "O Brasil venceu em 1958 com Pelé."
        mock_pipeline_class.return_value = mock_pipeline
        
        response = client.post("/chat", json={"message": "Como o Brasil venceu a Copa de 1958?", "k": 4})
        
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["response"] == "O Brasil venceu em 1958 com Pelé."
        
        # Deve conter apenas 1 fonte na lista, eliminando a duplicidade da URL
        assert len(json_data["sources"]) == 1
        assert json_data["sources"][0]["title"] == "Copa de 1958"
        assert json_data["sources"][0]["url"] == "https://example.com/1958"

def test_chat_endpoint_validation_error():
    # Mensagem vazia deve estourar validação de min_length=1 do Pydantic
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 422

def test_chat_endpoint_quota_error():
    with patch("app.main.RAGPipeline") as mock_pipeline_class:
        mock_pipeline = MagicMock()
        mock_pipeline.retrieve_context.side_effect = Exception("RESOURCE_EXHAUSTED: Quota exceeded")
        mock_pipeline_class.return_value = mock_pipeline
        
        response = client.post("/chat", json={"message": "Pergunta teste"})
        
        assert response.status_code == 503
        assert "Gemini foi temporariamente excedido" in response.json()["detail"]
