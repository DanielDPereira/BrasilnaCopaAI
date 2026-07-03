from langchain_core.vectorstores import VectorStoreRetriever
from app.vectorstore.database import get_vectorstore

def get_retriever(k: int = 4) -> VectorStoreRetriever:
    """
    Retorna uma instância do retriever do ChromaDB configurada com o parâmetro Top-K.
    
    Args:
        k: Número de documentos semilares (chunks) a serem recuperados. Padrão: 4.
        
    Returns:
        VectorStoreRetriever do LangChain.
    """
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )
