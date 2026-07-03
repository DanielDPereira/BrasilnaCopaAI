from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentChunker:
    """
    Classe responsável por realizar o fatiamento (chunking) de documentos processados.
    Utiliza a estratégia de divisão recursiva de caracteres com sobreposição controlada.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Inicializa o fatiador de documentos.
        
        Args:
            chunk_size: Tamanho máximo de cada chunk em caracteres.
            chunk_overlap: Tamanho da sobreposição de caracteres entre chunks adjacentes.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
            separators=["\n\n", "\n", " ", ""]
        )

    def split_document(self, processed_doc: Dict[str, Any]) -> List[Document]:
        """
        Divide o texto limpo de um documento processado em chunks estruturados,
        propagando e estendendo os metadados para cada um dos fragmentos gerados.
        
        Args:
            processed_doc: Dicionário contendo as chaves 'title', 'source_url',
                           'cleaned_text' e 'metadata'.
                           
        Returns:
            Lista de objetos langchain_core.documents.Document correspondentes aos chunks.
        """
        text = processed_doc.get("cleaned_text", "")
        doc_metadata = processed_doc.get("metadata", {})
        title = processed_doc.get("title", "")
        
        if not text.strip():
            return []
            
        # Divide o texto limpo
        chunks = self.text_splitter.split_text(text)
        
        documents = []
        for i, chunk in enumerate(chunks):
            # Cria uma cópia profunda/estendida dos metadados originais
            metadata = doc_metadata.copy()
            metadata.update({
                "chunk_index": i,
                "total_chunks": len(chunks),
                "source_title": title
            })
            
            doc = Document(page_content=chunk, metadata=metadata)
            documents.append(doc)
            
        return documents
