import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.ingestion.collector import WikipediaCollector
from app.ingestion.cleaner import TextCleaner

class WikipediaProcessor:
    """
    Classe orquestradora responsavel por integrar a coleta e a limpeza de dados,
    e por salvar os arquivos prontos para indexacao semantica em data/processed/.
    """
    def __init__(
        self, 
        raw_dir: str = "data/raw", 
        processed_dir: str = "data/processed",
        user_agent: str = "BrasilnaCopaAI/1.0 (daniel@exemplo.com)"
    ):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        
        # Inicializa as dependencias
        self.collector = WikipediaCollector(raw_dir=self.raw_dir, user_agent=user_agent)
        self.cleaner = TextCleaner()
        
        # Garante a existencia do diretorio de dados processados
        os.makedirs(self.processed_dir, exist_ok=True)

    def process_article(self, raw_filepath: str) -> str:
        """
        Le um arquivo de dados brutos (JSON), limpa seu conteudo textual
        e salva a versao estruturada final em data/processed/.
        
        Args:
            raw_filepath: Caminho do arquivo JSON bruto.
            
        Returns:
            Caminho do arquivo processado gerado.
        """
        # Le o arquivo bruto
        with open(raw_filepath, "r", encoding="utf-8") as f:
            raw_data: Dict[str, Any] = json.load(f)
            
        title = raw_data["title"]
        url = raw_data["url"]
        text = raw_data["text"]
        
        print(f"🧹 Limpando e estruturando o artigo '{title}'...")
        
        # Executa a limpeza do texto
        clean_text = self.cleaner.clean(text)
        
        # Calcula algumas metricas para compor os metadados
        char_count = len(clean_text)
        word_count = len(clean_text.split())
        
        # Estrutura final com metadados para indexacao no banco vetorial
        processed_data: Dict[str, Any] = {
            "title": title,
            "source_url": url,
            "cleaned_text": clean_text,
            "metadata": {
                "source": "wikipedia",
                "title": title,
                "url": url,
                "word_count": word_count,
                "char_count": char_count,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
        # O nome do arquivo processado segue a mesma chave do bruto
        filename = os.path.basename(raw_filepath)
        processed_filepath = os.path.join(self.processed_dir, filename)
        
        # Salva o arquivo JSON processado
        with open(processed_filepath, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=4)
            
        print(f"✅ Artigo '{title}' processado e salvo em: {processed_filepath}")
        return processed_filepath

    def run_pipeline(self, page_titles: List[str], force_update: bool = False) -> List[str]:
        """
        Orquestra a coleta e o processamento de uma lista de paginas da Wikipedia.
        
        Args:
            page_titles: Lista de titulos de paginas para processar.
            force_update: Se True, forca a atualizacao (coleta da internet) dos artigos.
            
        Returns:
            Lista de caminhos dos arquivos processados finais.
        """
        processed_files = []
        
        # Passo 1: Coleta
        print(f"🚀 Iniciando pipeline de ingestao para {len(page_titles)} paginas...")
        raw_files = self.collector.fetch_multiple_pages(page_titles, force_update=force_update)
        
        # Passo 2: Processamento e Limpeza
        for raw_file in raw_files:
            try:
                processed_file = self.process_article(raw_file)
                processed_files.append(processed_file)
            except Exception as e:
                print(f"❌ Falha ao processar arquivo {raw_file}: {str(e)}")
                
        print(f"🎉 Pipeline concluido! {len(processed_files)} artigos salvos em '{self.processed_dir}'.")
        return processed_files
