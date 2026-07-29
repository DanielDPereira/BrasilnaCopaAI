import os
import subprocess
import sys

def main():
    # Garante suporte a UTF-8/Emojis no console
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    print("====================================================")
    print("🇧🇷   INICIALIZAÇÃO DO BACKEND NO CONTAINER DOCKER   🇧🇷")
    print("====================================================")
    
    # 1. Download do modelo local se ativado e não existente
    use_local = os.getenv("USE_LOCAL_EMBEDDINGS", "").lower() == "true"
    if use_local:
        print("Embeddings locais ativados (USE_LOCAL_EMBEDDINGS=true).")
        # Caminhos padrão do modelo local
        model_path = "data/models/paraphrase-multilingual-MiniLM-L12-v2/model.onnx"
        tokenizer_path = "data/models/paraphrase-multilingual-MiniLM-L12-v2/tokenizer.json"
        
        if not os.path.exists(model_path) or not os.path.exists(tokenizer_path):
            print("Modelo ONNX local não encontrado em data/models/. Iniciando download...")
            subprocess.run([sys.executable, "scripts/download_local_model.py"], check=True)
        else:
            print("Modelo ONNX local já existe. Pulando download.")
    else:
        print("Embeddings locais desativados. Usando API remota do Gemini.")
        
    # 2. Carga inicial do banco se vazio ou inexistente
    db_path = os.getenv("CHROMA_DB_PATH", "data/db")
    db_exists_and_not_empty = os.path.exists(db_path) and os.listdir(db_path)
    
    if not db_exists_and_not_empty:
        print("Banco vetorial ChromaDB não encontrado ou vazio. Iniciando carga inicial da base de conhecimento...")
        
        print("Passo 1: Coleta e processamento de artigos da Wikipedia...")
        subprocess.run([sys.executable, "-m", "app.ingestion.run"], check=True)
        
        print("Passo 2: Fatiamento e indexação no banco vetorial ChromaDB...")
        subprocess.run([sys.executable, "-m", "app.vectorstore.populate"], check=True)
        
        print("Carga inicial concluída com sucesso!")
    else:
        print(f"Banco vetorial ChromaDB existente detectado em '{db_path}'. Pulando carga inicial.")
        
    print("====================================================")
    print("🚀 Iniciando API Backend FastAPI com Uvicorn...")
    print("====================================================")
    
    # Executa o uvicorn substituindo o processo atual do Python
    os.execvp("uvicorn", ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"])

if __name__ == "__main__":
    main()
