from unittest.mock import MagicMock, patch
from app.rag.retriever import get_retriever, MultiQueryRAGRetriever

@patch("app.rag.retriever.get_llm")
@patch("app.rag.retriever.get_vectorstore")
def test_get_retriever(mock_get_vectorstore, mock_get_llm):
    mock_vectorstore = MagicMock()
    mock_llm = MagicMock()
    
    mock_get_vectorstore.return_value = mock_vectorstore
    mock_get_llm.return_value = mock_llm
    
    retriever = get_retriever(k=5)
    
    assert isinstance(retriever, MultiQueryRAGRetriever)
    assert retriever.vectorstore == mock_vectorstore
    assert retriever.llm == mock_llm
    assert retriever.k == 5
