from typing import Any, List
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from app.vectorstore.database import get_vectorstore
from app.rag.llm import get_llm

class MultiQueryRAGRetriever(BaseRetriever):
    """
    Retriever customizado que realiza expansão de consultas utilizando o LLM.
    Para cada pergunta recebida, gera 3 variações de busca adicionais para
    maximizar a cobertura (recall) do contexto retornado do ChromaDB.
    """
    vectorstore: Any
    llm: Any
    k: int = 4

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        # Prompt para expansão das consultas em português
        prompt = (
            f"Você é um assistente especialista na história da Seleção Brasileira nas Copas do Mundo.\n"
            f"Gere exatamente 3 termos de busca ou perguntas curtas alternativas no banco de dados para responder a: '{query}'.\n"
            f"Gere apenas as 3 consultas alternativas, uma por linha, sem comentários, números, hifens ou explicações adicionais.\n"
        )
        
        try:
            response = self.llm.invoke(prompt)
            queries = [query]
            content = response.content
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, str):
                        text_parts.append(part)
                    elif isinstance(part, dict) and "text" in part:
                        text_parts.append(part["text"])
                content = "".join(text_parts)
            
            for line in content.split("\n"):
                line = line.strip().strip("-").strip("*").strip("123456789. ")
                if line:
                    queries.append(line)
        except Exception:
            # Em caso de falha de conexão ou rate-limit no LLM durante a expansão,
            # faz fallback seguro usando apenas a query original.
            queries = [query]
            
        all_docs = []
        seen_contents = set()
        
        for q in queries:
            docs = self.vectorstore.similarity_search(q, k=self.k)
            for doc in docs:
                content_hash = doc.page_content
                if content_hash not in seen_contents:
                    seen_contents.add(content_hash)
                    all_docs.append(doc)
                    
        # Retorna um número de documentos expandido para dar maior amplitude de contexto
        # ao Gemini na etapa de geração
        return all_docs[:self.k * 3]

def get_retriever(k: int = 4) -> BaseRetriever:
    """
    Retorna a instância configurada do MultiQueryRAGRetriever.
    
    Args:
        k: Número básico de documentos similares (chunks) a serem recuperados por variação.
        
    Returns:
        BaseRetriever configurado para expansão de busca.
    """
    vectorstore = get_vectorstore()
    llm = get_llm()
    return MultiQueryRAGRetriever(vectorstore=vectorstore, llm=llm, k=k)
