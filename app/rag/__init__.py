# Pacote de orquestracao RAG (LangChain) do BrasilnaCopaAI
from app.rag.retriever import get_retriever
from app.rag.prompts import SYSTEM_PROMPT, get_prompt_template
from app.rag.pipeline import RAGPipeline
from app.rag.llm import FallbackChatGemini, get_llm

__all__ = [
    "get_retriever",
    "SYSTEM_PROMPT",
    "get_prompt_template",
    "RAGPipeline",
    "FallbackChatGemini",
    "get_llm"
]
