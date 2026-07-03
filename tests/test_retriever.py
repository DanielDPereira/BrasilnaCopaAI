from unittest.mock import MagicMock, patch
from langchain_core.vectorstores import VectorStoreRetriever
from app.rag.retriever import get_retriever

@patch("app.rag.retriever.get_vectorstore")
def test_get_retriever(mock_get_vectorstore):
    mock_vectorstore = MagicMock()
    mock_retriever = MagicMock(spec=VectorStoreRetriever)
    mock_vectorstore.as_retriever.return_value = mock_retriever
    mock_get_vectorstore.return_value = mock_vectorstore
    
    retriever = get_retriever(k=5)
    
    assert retriever == mock_retriever
    mock_vectorstore.as_retriever.assert_called_once_with(
        search_type="similarity",
        search_kwargs={"k": 5}
    )
