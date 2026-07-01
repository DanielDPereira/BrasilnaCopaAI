import datetime
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Definição do app FastAPI com metadados para o Swagger
app = FastAPI(
    title="BrasilnaCopaAI API",
    description="Backend API para o chatbot inteligente sobre a participação do Brasil na Copa do Mundo 2026.",
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

@app.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    tags=["Monitoramento"],
    summary="Verificar a saúde da API",
    description="Retorna o status atual de funcionamento do backend e suas conexões básicas.",
)
async def health_check():
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.datetime.utcnow(),
        version="0.1.0",
        database="not_connected",  # Será atualizado após configuração do ChromaDB
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
