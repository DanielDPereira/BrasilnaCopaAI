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
    prefix_len = len("[Contexto: Copa 2026]\n\n")
    for i, chunk in enumerate(chunks):
        assert chunk.metadata["source_title"] == "Copa 2026"
        assert chunk.metadata["chunk_index"] == i
        assert chunk.metadata["total_chunks"] == len(chunks)
        assert chunk.metadata["source"] == "test"
        assert len(chunk.page_content) <= 50 + prefix_len
        assert chunk.page_content.startswith("[Contexto: Copa 2026]\n\n")

def test_document_chunker_markdown():
    doc = {
        "title": "Pelé",
        "source_url": "https://example.com/pele",
        "cleaned_text": "# Pelé\nResumo sobre Pelé.\n\n## Carreira na Seleção\n=== Copa de 1958 ===\nEle marcou seis gols em 58.",
        "metadata": {
            "source": "test"
        }
    }
    
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=10)
    chunks = chunker.split_document(doc)
    
    assert len(chunks) > 0
    # Verificamos se os chunks possuem o contexto correto com base em sua seção
    first_chunk = chunks[0]
    assert "Contexto: Pelé" in first_chunk.page_content
    assert first_chunk.metadata["section_path"] == "Pelé"
    
    # O segundo chunk deve estar na seção "Carreira na Seleção"
    second_chunk = chunks[1]
    assert "Contexto: Pelé > Carreira na Seleção" in second_chunk.page_content
    assert second_chunk.metadata["section_path"] == "Pelé > Carreira na Seleção"

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
