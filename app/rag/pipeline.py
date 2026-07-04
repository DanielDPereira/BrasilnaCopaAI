from typing import List
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from app.rag.retriever import get_retriever
from app.rag.prompts import get_prompt_template
from app.rag.llm import get_llm

class RAGPipeline:
    """
    Orquestrador RAG (Retrieval-Augmented Generation) do BrasilnaCopaAI.
    Responsável por gerenciar a busca semântica no banco vetorial local (ChromaDB)
    e estruturar a cadeia que se conecta ao Google Gemini para obter respostas.
    """
    def __init__(self, k: int = 4):
        """
        Inicializa o pipeline RAG.
        
        Args:
            k: Número de documentos (chunks) a serem retornados na busca semântica.
        """
        self.retriever = get_retriever(k=k)
        self.prompt_template = get_prompt_template()
        self.llm = get_llm()
        self.prompt_chain = self._build_prompt_chain()
        self.chain = self._build_chain()

    def _build_prompt_chain(self):
        """
        Monta a cadeia LCEL até a geração do prompt formatado com contexto.
        """
        return (
            {
                "context": self.retriever | self.format_docs,
                "question": RunnablePassthrough()
            }
            | self.prompt_template
        )

    def _build_chain(self):
        """
        Monta a cadeia RAG final de ponta a ponta (Prompt -> LLM -> Parser).
        """
        return self.prompt_chain | self.llm | StrOutputParser()

    @staticmethod
    def format_docs(docs: List[Document]) -> str:
        """
        Formata uma lista de documentos retornados pelo retriever em uma única string
        estruturada com os metadados de título e link de origem de cada trecho.
        
        Args:
            docs: Lista de objetos Document do LangChain.
            
        Returns:
            String contendo o contexto completo formatado.
        """
        formatted = []
        for doc in docs:
            # Tenta ler o título e a url dos metadados originais
            title = doc.metadata.get("title", "Documento Sem Título")
            url = doc.metadata.get("url", "Sem link de origem")
            content = doc.page_content.strip()
            
            formatted.append(
                f"--- Artigo: {title} ---\n"
                f"Fonte: {url}\n"
                f"Conteúdo:\n{content}\n"
            )
        return "\n".join(formatted)

    def retrieve_context(self, query: str) -> List[Document]:
        """
        Executa apenas a busca semântica e retorna os chunks mais similares no ChromaDB.
        
        Args:
            query: Pergunta do usuário.
            
        Returns:
            Lista de Documents recuperados.
        """
        return self.retriever.invoke(query)

    def generate_prompt(self, query: str):
        """
        Executa a cadeia RAG gerando as mensagens (System + Human)
        com o prompt final contendo as diretrizes e o contexto.
        
        Args:
            query: Pergunta do usuário.
            
        Returns:
            ChatPromptValue contendo as mensagens formatadas.
        """
        return self.prompt_chain.invoke(query)

    def ask(self, query: str) -> str:
        """
        Executa a cadeia RAG de ponta a ponta, enviando o prompt ao Gemini
        e retornando a resposta final em formato textual (string).
        
        Args:
            query: Pergunta do usuário.
            
        Returns:
            Resposta textual gerada pela LLM.
        """
        return self.chain.invoke(query)
