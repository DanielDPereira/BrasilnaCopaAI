import os
import shutil
import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma

# Classe Mock de Embeddings para testes sem precisar chamar a API externa do Gemini
class SimpleMockEmbeddings(Embeddings):
    def embed_documents(self, texts):
        # Retorna vetores fictícios simples (ex: baseados no tamanho do texto)
        return [[len(t) * 0.01] * 768 for t in texts]

    def embed_query(self, text):
        return [len(text) * 0.01] * 768

@pytest.fixture
def temp_chroma_db(tmp_path):
    # Cria uma pasta temporária para o banco vetorial do teste
    db_dir = tmp_path / "test_db"
    embeddings = SimpleMockEmbeddings()
    
    # Inicializa o banco na pasta temporária
    db = Chroma(
        collection_name="test_collection",
        embedding_function=embeddings,
        persist_directory=str(db_dir)
    )
    yield db
    # O pytest se encarrega de limpar os diretórios temporários no final.

def test_chromadb_insertion_and_search(temp_chroma_db):
    docs = [
        Document(
            page_content="O Brasil é pentacampeão mundial de futebol.",
            metadata={"source": "copa", "id": 1}
        ),
        Document(
            page_content="A Copa do Mundo de 2026 será sediada por EUA, Canadá e México.",
            metadata={"source": "copa", "id": 2}
        ),
        Document(
            page_content="A Copa do Mundo de 1970 foi vencida pela Seleção Brasileira liderada por Pelé.",
            metadata={"source": "historico", "id": 3}
        )
    ]
    
    # Adiciona documentos
    temp_chroma_db.add_documents(docs)
    
    # Realiza uma busca por similaridade
    query = "Onde vai ser a Copa de 2026?"
    results = temp_chroma_db.similarity_search(query, k=2)
    
    assert len(results) == 2
    # Verifica se os resultados contêm os documentos corretos
    # Como usamos um mock de embeddings simples baseado no tamanho,
    # verificamos a presença dos dados e metadados
    for res in results:
        assert "source" in res.metadata
        assert res.metadata["id"] in [1, 2, 3]

def test_chromadb_similarity_search_with_score(temp_chroma_db):
    doc = Document(
        page_content="A Seleção do Brasil é coordenada pela CBF.",
        metadata={"source": "cbf"}
    )
    temp_chroma_db.add_documents([doc])
    
    # Busca com score (proximidade)
    results = temp_chroma_db.similarity_search_with_score("Quem coordena a Seleção?", k=1)
    
    assert len(results) == 1
    retrieved_doc, score = results[0]
    assert retrieved_doc.page_content == "A Seleção do Brasil é coordenada pela CBF."
    assert retrieved_doc.metadata["source"] == "cbf"
    assert isinstance(score, float)
