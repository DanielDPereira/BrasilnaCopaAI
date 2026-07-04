import pytest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from app.rag.pipeline import RAGPipeline

def test_format_docs():
    docs = [
        Document(
            page_content="O Brasil venceu a Copa de 1970.",
            metadata={"title": "História da Seleção", "url": "https://example.com/historia"}
        ),
        Document(
            page_content="A Copa de 2026 será na América do Norte.",
            metadata={"title": "Copa 2026", "url": "https://example.com/copa"}
        )
    ]
    
    formatted = RAGPipeline.format_docs(docs)
    
    assert "--- Artigo: História da Seleção ---" in formatted
    assert "Fonte: https://example.com/historia" in formatted
    assert "O Brasil venceu a Copa de 1970." in formatted
    assert "--- Artigo: Copa 2026 ---" in formatted
    assert "Fonte: https://example.com/copa" in formatted
    assert "A Copa de 2026 será na América do Norte." in formatted

@patch("app.rag.pipeline.get_retriever")
@patch("app.rag.pipeline.get_llm")
def test_rag_pipeline_chain_mock(mock_get_llm, mock_get_retriever):
    # Mock do retriever e do LLM para evitar dependências externas
    mock_get_llm.return_value = MagicMock()
    mock_retriever = RunnableLambda(lambda x: [
        Document(
            page_content="Pelé jogou na Copa de 1958.",
            metadata={"title": "Pelé", "url": "https://example.com/pele"}
        )
    ])
    mock_get_retriever.return_value = mock_retriever
    
    pipeline = RAGPipeline(k=1)
    
    # Executa a geração do prompt
    prompt_value = pipeline.generate_prompt("Quem foi Pelé?")
    messages = prompt_value.to_messages()
    
    assert len(messages) == 2
    
    # Verifica o System Prompt com o contexto injetado
    sys_msg = messages[0].content
    assert "Pelé jogou na Copa de 1958." in sys_msg
    assert "Você é um assistente de IA especialista" in sys_msg
    
    # Verifica a pergunta do usuário
    human_msg = messages[1].content
    assert human_msg == "Quem foi Pelé?"

@patch("app.rag.pipeline.get_retriever")
@patch("app.rag.pipeline.get_llm")
def test_rag_pipeline_ask_mock(mock_get_llm, mock_get_retriever):
    # Mock do retriever
    mock_retriever = RunnableLambda(lambda x: [
        Document(
            page_content="O Brasil é pentacampeão.",
            metadata={"title": "Títulos", "url": "https://example.com/titulos"}
        )
    ])
    mock_get_retriever.return_value = mock_retriever
    
    # Mock do LLM retornar objeto compatível (ex: AIMessage)
    from langchain_core.messages import AIMessage
    mock_llm = RunnableLambda(lambda x: AIMessage(content="O Brasil possui 5 títulos da Copa do Mundo."))
    mock_get_llm.return_value = mock_llm
    
    pipeline = RAGPipeline(k=1)
    response = pipeline.ask("Quantos títulos o Brasil tem?")
    
    assert response == "O Brasil possui 5 títulos da Copa do Mundo."

@pytest.mark.integration
def test_rag_pipeline_real_db_search():
    # Teste de integração real contra o banco ChromaDB local
    try:
        pipeline = RAGPipeline(k=2)
        
        # Realiza a busca no banco vetorial persistido
        query = "cidades sedes da Copa do Mundo de 2026"
        docs = pipeline.retrieve_context(query)
        
        assert len(docs) <= 2
        if docs:
            # Garante que recuperou algum conteúdo textual
            assert len(docs[0].page_content) > 0
            assert "url" in docs[0].metadata
            
            # Gera o prompt enriquecido
            prompt_value = pipeline.generate_prompt(query)
            sys_msg = prompt_value.to_messages()[0].content
            
            # O prompt deve conter as fontes e dados reais do banco
            assert "Artigo:" in sys_msg
            assert "Fonte:" in sys_msg
    except Exception as e:
        pytest.fail(f"Falha de integração com o ChromaDB real: {str(e)}")

@pytest.mark.integration
def test_rag_pipeline_real_ask():
    # Executa uma pergunta real apenas se houver chave de API configurada no ambiente
    import os
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GEMINI_API_KEYS"):
        pytest.skip("Chave de API do Gemini não configurada para teste de integração real.")
        
    try:
        pipeline = RAGPipeline(k=1)
        # Pergunta sobre algo que está nos documentos, ex: sedes da Copa 2026 ou Seleção
        response = pipeline.ask("Quais países vão sediar a Copa do Mundo de 2026?")
        
        assert len(response) > 0
        assert "Não possuo essa informação" not in response  # Deve encontrar pois está no banco!
    except Exception as e:
        pytest.fail(f"Falha na integração real com Gemini: {str(e)}")
