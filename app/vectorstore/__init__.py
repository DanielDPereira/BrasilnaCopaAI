# Pacote de configuracao do banco vetorial ChromaDB do BrasilnaCopaAI
from app.vectorstore.chunker import DocumentChunker
from app.vectorstore.database import (
    GeminiAPIKeyManager,
    FallbackGeminiEmbeddings,
    get_key_manager,
    get_embedding_model,
    get_vectorstore
)

__all__ = [
    "DocumentChunker",
    "GeminiAPIKeyManager",
    "FallbackGeminiEmbeddings",
    "get_key_manager",
    "get_embedding_model",
    "get_vectorstore"
]
