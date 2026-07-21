import os
import json
import glob
import sys
from typing import List
from dotenv import load_dotenv
from app.vectorstore.chunker import DocumentChunker
from app.vectorstore.database import get_vectorstore

load_dotenv()

def populate_database() -> None:
    # Garante suporte a UTF-8/Emojis em consoles Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        
    print("====================================================")
    print("🇧🇷  INICIALIZANDO INDEXAÇÃO NO CHROMADB - BRASILNACOPAAI  🇧🇷")
    print("====================================================")
    
    # 1. Conecta ao banco vetorial
    print("🔌 Conectando ao ChromaDB...")
    vectorstore = get_vectorstore()
    
    # 2. Limpa coleção anterior para evitar duplicações
    print("🧹 Limpando dados antigos da coleção...")
    try:
        # Chroma do LangChain não tem um método direto 'clear' de alto nível,
        # mas podemos deletar por ids ou usar a API do client interno para deletar
        # a coleção e criá-la novamente.
        # Uma forma limpa usando a API do LangChain Chroma é:
        # obter todos os documentos e deletar por IDs.
        all_docs = vectorstore.get()
        if all_docs and "ids" in all_docs and all_docs["ids"]:
            print(f"🗑️ Removendo {len(all_docs['ids'])} registros existentes...")
            vectorstore.delete(ids=all_docs["ids"])
            print("✅ Coleção limpa com sucesso.")
        else:
            print("ℹ️ Coleção já estava vazia.")
    except Exception as e:
        print(f"⚠️ Erro ao limpar a coleção (pode ser a primeira execução): {str(e)}")
        
    # 3. Inicializa o Chunker
    chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)
    
    # 4. Busca todos os arquivos processados
    processed_dir = "data/processed"
    search_path = os.path.join(processed_dir, "*.json")
    files = glob.glob(search_path)
    
    if not files:
        print(f"❌ Nenhum arquivo processado encontrado em '{processed_dir}'.")
        print("Certifique-se de executar o pipeline de ingestão primeiro:")
        print("python -m app.ingestion.run")
        sys.exit(1)
        
    print(f"📂 Encontrados {len(files)} arquivos para indexação.")
    print("----------------------------------------------------")
    
    total_chunks = 0
    all_documents = []
    
    for filepath in files:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                processed_doc = json.load(f)
                
            title = processed_doc.get("title", filename)
            # Divide o documento em chunks
            chunks = chunker.split_document(processed_doc)
            
            if chunks:
                all_documents.extend(chunks)
                total_chunks += len(chunks)
                print(f"📝 Artigo '{title}': fatiado em {len(chunks)} chunks.")
            else:
                print(f"⚠️ Artigo '{title}': nenhum texto relevante para fatiar.")
                
        except Exception as e:
            print(f"❌ Erro ao fatiar o arquivo {filename}: {str(e)}")
            
    print("----------------------------------------------------")
    if not all_documents:
        print("❌ Nenhum chunk foi gerado. Abortando indexação.")
        sys.exit(1)
        
    print(f"🚀 Enviando {total_chunks} chunks para o ChromaDB e gerando embeddings...")
    print("Isso pode levar alguns instantes (consumindo API Gemini)...")
    
    try:
        # Insere no ChromaDB em lotes (batches) menores e com sleep para não exceder limites de requisições
        batch_size = 20
        print(f"🚀 Enviando {total_chunks} chunks para o ChromaDB em lotes de {batch_size}...")
        
        import time
        for i in range(0, len(all_documents), batch_size):
            batch = all_documents[i:i + batch_size]
            print(f"📦 Indexando lote {i // batch_size + 1} / {(len(all_documents) - 1) // batch_size + 1} ({len(batch)} chunks)...")
            
            retries = 5
            success = False
            while retries > 0 and not success:
                try:
                    vectorstore.add_documents(batch)
                    success = True
                    # Intervalo de 4 segundos para evitar limite de requisições por minuto (RPM)
                    time.sleep(4)
                except Exception as e:
                    err_msg = str(e)
                    if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
                        retries -= 1
                        print(f"⏳ Limite de requisições excedido. Aguardando 40 segundos para recuperar cota... (Tentativas restantes: {retries})")
                        time.sleep(40)
                    else:
                        raise e
            if not success:
                raise Exception("Lote falhou após esgotar tentativas de reenvio devido a limites de taxa.")

        print("====================================================")
        print(f"✨ Sucesso! {total_chunks} chunks foram indexados com sucesso!")
        print(f"💾 Banco vetorial persistido em: {os.getenv('CHROMA_DB_PATH', 'data/db')}")
        print("====================================================")
    except Exception as e:
        import traceback
        print("💥 Erro crítico ao indexar documentos no ChromaDB:", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    populate_database()
