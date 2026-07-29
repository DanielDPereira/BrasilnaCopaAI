import os
import sys
from huggingface_hub import hf_hub_download

def download_model():
    # Garante suporte a UTF-8/Emojis em consoles Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    print("====================================================")
    print("📥 DOWNLOAD DO MODELO DE EMBEDDINGS LOCAL (ONNX) 📥")
    print("====================================================")
    
    # Define o diretório de destino
    model_dir = os.path.abspath("data/models/paraphrase-multilingual-MiniLM-L12-v2")
    os.makedirs(model_dir, exist_ok=True)
    
    repo_id = "onnx-models/paraphrase-multilingual-MiniLM-L12-v2-onnx"
    files = ["model.onnx", "tokenizer.json"]
    
    for filename in files:
        target_path = os.path.join(model_dir, filename)
        if os.path.exists(target_path):
            print(f"✅ Arquivo já existe: {filename} ({target_path})")
            continue
            
        print(f"⬇️ Baixando {filename} do repositório {repo_id}...")
        try:
            # Realiza o download do arquivo a partir do Hugging Face Hub
            downloaded_file = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=model_dir
            )
            print(f"✨ Concluído! Salvo em: {downloaded_file}")
        except Exception as e:
            print(f"💥 Erro ao baixar o arquivo {filename}: {e}", file=sys.stderr)
            sys.exit(1)
            
    print("====================================================")
    print("🎉 Modelo local pronto para uso em data/models/! 🎉")
    print("====================================================")

if __name__ == "__main__":
    download_model()
