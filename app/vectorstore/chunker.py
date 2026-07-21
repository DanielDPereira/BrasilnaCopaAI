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
        Utiliza uma estratégia de fatiamento orientada por seções (Markdown)
        e adiciona prefixos contextuais em cada chunk para preservar a semântica hierárquica.
        
        Args:
            processed_doc: Dicionário contendo as chaves 'title', 'source_url',
                           'cleaned_text' e 'metadata'.
                           
        Returns:
            Lista de objetos langchain_core.documents.Document correspondentes aos chunks.
        """
        import re
        text = processed_doc.get("cleaned_text", "")
        doc_metadata = processed_doc.get("metadata", {})
        title = processed_doc.get("title", "")
        
        if not text.strip():
            return []
            
        header_regex = re.compile(r'^(#{1,6})\s+(.+)$')
        lines = text.split('\n')
        
        sections = []
        current_section_text = []
        current_section_path = []
        current_path = []
        
        has_headers = False
        
        for line in lines:
            match = header_regex.match(line.strip())
            if match:
                has_headers = True
                if current_section_text:
                    sections.append({
                        "path": current_section_path.copy(),
                        "text": "\n".join(current_section_text).strip()
                    })
                    current_section_text = []
                
                level = len(match.group(1))
                header_title = match.group(2).strip()
                
                current_path = current_path[:level-1]
                while len(current_path) < level - 1:
                    current_path.append("")
                current_path.append(header_title)
                current_section_path = current_path.copy()
            else:
                current_section_text.append(line)
                
        if current_section_text:
            sections.append({
                "path": current_section_path.copy(),
                "text": "\n".join(current_section_text).strip()
            })
            
        # Fallback se o documento não possuir nenhum cabeçalho Markdown
        if not has_headers:
            raw_chunks = self.text_splitter.split_text(text)
            documents = []
            context_prefix = f"[Contexto: {title}]\n\n"
            for i, chunk in enumerate(raw_chunks):
                metadata = doc_metadata.copy()
                metadata.update({
                    "chunk_index": i,
                    "total_chunks": len(raw_chunks),
                    "source_title": title,
                    "section_path": title
                })
                doc = Document(page_content=context_prefix + chunk, metadata=metadata)
                documents.append(doc)
            return documents

        # Para documentos com cabeçalhos estruturados
        raw_chunks_data = []
        for sec in sections:
            sec_text = sec["text"]
            if not sec_text:
                continue
                
            # Cria a trilha de navegação (breadcrumb) do cabeçalho
            # Deduplica o título se o primeiro nível do cabeçalho for igual ao título do artigo
            path_parts = []
            for p in [title] + sec["path"]:
                if p and (not path_parts or path_parts[-1] != p):
                    path_parts.append(p)
                    
            breadcrumb = " > ".join(path_parts)
            context_prefix = f"[Contexto: {breadcrumb}]\n\n"
            
            sec_chunks = self.text_splitter.split_text(sec_text)
            for chunk in sec_chunks:
                raw_chunks_data.append({
                    "text": context_prefix + chunk,
                    "section_path": breadcrumb
                })
                
        documents = []
        for i, chunk_data in enumerate(raw_chunks_data):
            metadata = doc_metadata.copy()
            metadata.update({
                "chunk_index": i,
                "total_chunks": len(raw_chunks_data),
                "source_title": title,
                "section_path": chunk_data["section_path"]
            })
            doc = Document(page_content=chunk_data["text"], metadata=metadata)
            documents.append(doc)
            
        return documents
