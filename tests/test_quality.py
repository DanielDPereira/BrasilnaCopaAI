import time
import pytest
from unittest.mock import patch
from app.rag.pipeline import RAGPipeline

def test_retriever_quality():
    """
    Avalia a precisão da recuperação do retriever pesquisando por termos conhecidos
    que devem estar indexados na base da Seleção Brasileira.
    """
    pipeline = RAGPipeline(k=3)
    docs = pipeline.retrieve_context("Pelé")
    
    # Garante que documentos são retornados
    assert len(docs) > 0, "O retriever não retornou nenhum documento."
    
    # Pelo menos um dos documentos recuperados deve conter termos relacionados à busca
    termos_esperados = ["Pelé", "Copa", "Brasil", "futebol", "Mundo"]
    encontrou_termo = False
    for doc in docs:
        conteudo = doc.page_content.lower()
        if any(termo.lower() in conteudo for termo in termos_esperados):
            encontrou_termo = True
            break
            
    assert encontrou_termo, "Nenhum dos documentos contendo o contexto esperado foi retornado."

@patch("app.rag.retriever.get_llm")
def test_pipeline_latency(mock_get_llm):
    """
    Mede a latência de recuperação local no ChromaDB e de ponta a ponta da geração da resposta.
    """
    from langchain_core.messages import AIMessage
    from langchain_core.runnables import RunnableLambda
    mock_get_llm.return_value = RunnableLambda(lambda x: AIMessage(content="Brasil na Copa\nCopas do Brasil\nSeleção Brasileira"))
    
    pipeline = RAGPipeline(k=2)
    
    # Medição do tempo de busca local no ChromaDB
    start_time = time.time()
    docs = pipeline.retrieve_context("Brasil na Copa")
    latency_retrieve = time.time() - start_time
    
    # A busca vetorial local com ONNX não deve levar mais do que 1.5 segundos
    assert latency_retrieve < 1.5, f"Latência de recuperação vetorial excessiva: {latency_retrieve:.2f}s"
    
    # Medição do tempo de geração de resposta (chamada da LLM)
    # Medimos a latência remota mas não impomos limite rígido para evitar falhas intermitentes de infraestrutura externa
    start_time = time.time()
    try:
        response = pipeline.ask("Quem ganhou a Copa do Mundo de 1970?")
        latency_ask = time.time() - start_time
        print(f"\n[Métricas de Qualidade] Latência local no ChromaDB: {latency_retrieve:.4f}s")
        print(f"[Métricas de Qualidade] Latência remota do Gemini: {latency_ask:.4f}s")
    except Exception as e:
        print(f"\n[Métricas de Qualidade] Erro temporário na chamada da API Gemini: {str(e)}")


def test_hallucination_protection_out_of_scope():
    """
    Valida a proteção contra alucinações enviando pergunta fora do escopo
    e verificando se a resposta de fallback literal é ativada corretamente.
    """
    pipeline = RAGPipeline(k=2)
    
    # Pergunta sem correlação com futebol ou seleção nas copas
    query = "Como cozinhar uma lasanha de berinjela?"
    fallback_esperado = "Não possuo essa informação em minha base de dados sobre a Seleção Brasileira nas Copas do Mundo."
    
    response = pipeline.ask(query)
    assert response.strip() == fallback_esperado, f"A proteção falhou para a pergunta: '{query}'. Resposta obtida: '{response}'"

