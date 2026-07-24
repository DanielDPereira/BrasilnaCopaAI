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
    def __init__(self, k: int = 4, custom_system_prompt: str | None = None, temperature: float = 0.0):
        """
        Inicializa o pipeline RAG.
        
        Args:
            k: Número de documentos (chunks) a serem retornados na busca semântica.
            custom_system_prompt: Prompt de sistema personalizado opcional.
            temperature: Temperatura do modelo LLM.
        """
        self.retriever = get_retriever(k=k)
        self.prompt_template = get_prompt_template(custom_prompt=custom_system_prompt)
        self.llm = get_llm(temperature=temperature)
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

    def reformulate_question(self, question: str, history: List[dict] = None) -> str:
        """
        Usa o LLM para reformular a pergunta de acompanhamento do usuário com base no histórico
        da conversa para que ela seja uma pergunta autossuficiente e independente (self-contained).
        
        Args:
            question: A pergunta atual do usuário.
            history: Lista de mensagens anteriores do histórico.
            
        Returns:
            A pergunta reformulada se houver histórico, ou a pergunta original.
        """
        if not history:
            return question
            
        # Formata o histórico como string legível
        formatted_history = []
        for msg in history:
            role = "Usuário" if msg.get("role") == "user" else "Assistente"
            content = msg.get("content", "").strip()
            formatted_history.append(f"{role}: {content}")
        history_str = "\n".join(formatted_history)
        
        prompt = (
            "Dada a conversa a seguir e uma pergunta de acompanhamento, reformule a pergunta de acompanhamento "
            "para que ela seja uma pergunta autossuficiente e independente (self-contained), em português do Brasil.\n"
            "Não responda à pergunta, apenas retorne a pergunta reformulada. Se a pergunta já for independente, "
            "retorne-a exatamente idêntica.\n\n"
            f"Histórico da conversa:\n{history_str}\n\n"
            f"Pergunta de acompanhamento: {question}\n"
            "Pergunta independente reformulada:"
        )
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, str):
                        text_parts.append(part)
                    elif isinstance(part, dict) and "text" in part:
                        text_parts.append(part["text"])
                content = "".join(text_parts)
                
            reformulated = content.strip().strip('"').strip("'").strip()
            if reformulated:
                return reformulated
        except Exception as e:
            # Em caso de falha, faz fallback seguro usando a query original
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Erro ao reformular a pergunta: {e}. Usando pergunta original.")
            
        return question

    def retrieve_context(self, query: str, history: List[dict] = None) -> List[Document]:
        """
        Executa apenas a busca semântica e retorna os chunks mais similares no ChromaDB.
        
        Args:
            query: Pergunta do usuário.
            history: Histórico de mensagens anteriores da conversa.
            
        Returns:
            Lista de Documents recuperados.
        """
        target_query = self.reformulate_question(query, history)
        return self.retriever.invoke(target_query)

    def generate_prompt(self, query: str, history: List[dict] = None):
        """
        Executa a cadeia RAG gerando as mensagens (System + Human)
        com o prompt final contendo as diretrizes e o contexto.
        
        Args:
            query: Pergunta do usuário.
            history: Histórico de mensagens anteriores da conversa.
            
        Returns:
            ChatPromptValue contendo as mensagens formatadas.
        """
        target_query = self.reformulate_question(query, history)
        return self.prompt_chain.invoke(target_query)

    def ask(self, query: str, history: List[dict] = None) -> str:
        """
        Executa a cadeia RAG de ponta a ponta, enviando o prompt ao Gemini
        e retornando a resposta final em formato textual (string).
        
        Args:
            query: Pergunta do usuário.
            history: Histórico de mensagens anteriores da conversa.
            
        Returns:
            Resposta textual gerada pela LLM.
        """
        target_query = self.reformulate_question(query, history)
        return self.chain.invoke(target_query)
