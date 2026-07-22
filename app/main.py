import datetime
import logging
from typing import List
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.rag.pipeline import RAGPipeline

# Configuração do logger básico da API
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Definição do app FastAPI com metadados para o Swagger
app = FastAPI(
    title="BrasilnaCopaAI API",
    description="Backend API para o chatbot inteligente sobre a história e participação da Seleção Brasileira nas Copas do Mundo.",
    version="0.1.0",
)

# Configuração de CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir às origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de resposta para o endpoint de saúde
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime.datetime
    version: str
    database: str

# Modelos de requisição e resposta do Chat RAG
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Pergunta a ser enviada ao RAG")
    k: int = Field(default=4, ge=1, le=10, description="Número de chunks de contexto a serem recuperados")
    custom_system_prompt: str | None = Field(default=None, description="Prompt de sistema personalizado")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0, description="Temperatura do modelo de linguagem")

class ChatSource(BaseModel):
    title: str = Field(..., description="Título do artigo de origem")
    url: str = Field(..., description="URL de origem do artigo na Wikipedia")

class ContextChunk(BaseModel):
    title: str = Field(..., description="Título do artigo de origem")
    content: str = Field(..., description="Conteúdo do chunk de texto recuperado")
    url: str = Field(..., description="Link do artigo original")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Resposta textual gerada pelo assistente")
    sources: List[ChatSource] = Field(..., description="Lista de fontes exclusivas de onde as informações foram recuperadas")
    context_chunks: List[ContextChunk] = Field(default=[], description="Lista com os trechos de texto originais e completos recuperados no ChromaDB")

@app.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    tags=["Monitoramento"],
    summary="Verificar a saúde da API",
    description="Retorna o status atual de funcionamento do backend e da conexão com o banco vetorial ChromaDB.",
)
async def health_check():
    db_status = "not_connected"
    try:
        from app.vectorstore.database import get_vectorstore
        db = get_vectorstore()
        count = db._collection.count()
        db_status = f"connected ({count} chunks)"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        version="0.1.0",
        database=db_status,
    )

@app.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    tags=["Chat RAG"],
    summary="Interagir com o assistente inteligente",
    description="Recebe a pergunta do usuário, faz busca por similaridade no banco vetorial ChromaDB, constrói o prompt estruturado e gera a resposta contextualizada com o Gemini.",
)
async def chat(request: ChatRequest):
    try:
        pipeline = RAGPipeline(k=request.k, custom_system_prompt=request.custom_system_prompt, temperature=request.temperature)
        
        # 1. Busca documentos relevantes no ChromaDB
        docs = pipeline.retrieve_context(request.message)
        
        # 2. Executa a geração de resposta via cadeia RAG
        answer = pipeline.ask(request.message)
        
        # 3. Extrai as fontes exclusivas eliminando duplicidades
        seen_urls = set()
        sources = []
        context_chunks = []
        for doc in docs:
            title = doc.metadata.get("title", "Documento Sem Título")
            url = doc.metadata.get("url", "")
            url_str = url if url else "Sem link de origem"
            
            # Adiciona ao context_chunks
            context_chunks.append(ContextChunk(title=title, content=doc.page_content, url=url_str))
            
            # Adiciona apenas se for URL válida e não duplicada para as fontes sintéticas
            if url and url not in seen_urls:
                seen_urls.add(url)
                sources.append(ChatSource(title=title, url=url))
            elif not url and title not in [s.title for s in sources]:
                sources.append(ChatSource(title=title, url="Sem link de origem"))
                
        return ChatResponse(
            response=answer,
            sources=sources,
            context_chunks=context_chunks
        )
    except Exception as e:
        err_str = str(e)
        logger.error(f"Erro no processamento do endpoint /chat: {err_str}", exc_info=True)
        
        # Trata erros de quota ou indisponibilidade do Gemini
        if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="O limite de quota do serviço Gemini foi temporariamente excedido. Por favor, tente novamente em alguns instantes."
            )
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no processamento do RAG: {err_str}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
