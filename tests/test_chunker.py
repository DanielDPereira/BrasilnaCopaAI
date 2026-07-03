import pytest
from app.vectorstore.chunker import DocumentChunker

def test_document_chunker_basic():
    doc = {
        "title": "Copa 2026",
        "source_url": "https://example.com/copa",
        "cleaned_text": "O Brasil participará da Copa do Mundo FIFA de 2026. A equipe está motivada e focada em vencer o torneio.",
        "metadata": {
            "source": "test",
            "url": "https://example.com/copa"
        }
    }
    
    # Usar um tamanho pequeno para forçar múltiplos chunks
    chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
    chunks = chunker.split_document(doc)
    
    assert len(chunks) > 1
    for i, chunk in enumerate(chunks):
        assert chunk.metadata["source_title"] == "Copa 2026"
        assert chunk.metadata["chunk_index"] == i
        assert chunk.metadata["total_chunks"] == len(chunks)
        assert chunk.metadata["source"] == "test"
        assert len(chunk.page_content) <= 50

def test_document_chunker_empty():
    doc = {
        "title": "Vazio",
        "source_url": "https://example.com",
        "cleaned_text": "",
        "metadata": {}
    }
    chunker = DocumentChunker()
    chunks = chunker.split_document(doc)
    assert len(chunks) == 0
