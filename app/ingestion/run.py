import argparse
import sys
from typing import List
from app.ingestion.processor import WikipediaProcessor

# Lista padrao de paginas a serem coletadas sobre a Copa e Selecao Brasileira
DEFAULT_PAGES = [
    "Seleção Brasileira de Futebol",
    "Confederação Brasileira de Futebol",
    "Copa do Mundo FIFA",
    "História da Seleção Brasileira de Futebol",
    "Títulos da Seleção Brasileira de Futebol",
    "Brasil na Copa do Mundo FIFA",
    "Copa do Mundo FIFA de 2026",
    "Brasil na Copa do Mundo FIFA de 1930",
    "Brasil na Copa do Mundo FIFA de 1934",
    "Brasil na Copa do Mundo FIFA de 1938",
    "Brasil na Copa do Mundo FIFA de 1950",
    "Brasil na Copa do Mundo FIFA de 1954",
    "Brasil na Copa do Mundo FIFA de 1958",
    "Brasil na Copa do Mundo FIFA de 1962",
    "Brasil na Copa do Mundo FIFA de 1966",
    "Brasil na Copa do Mundo FIFA de 1970",
    "Brasil na Copa do Mundo FIFA de 1974",
    "Brasil na Copa do Mundo FIFA de 1978",
    "Brasil na Copa do Mundo FIFA de 1982",
    "Brasil na Copa do Mundo FIFA de 1986",
    "Brasil na Copa do Mundo FIFA de 1990",
    "Brasil na Copa do Mundo FIFA de 1994",
    "Brasil na Copa do Mundo FIFA de 1998",
    "Brasil na Copa do Mundo FIFA de 2002",
    "Brasil na Copa do Mundo FIFA de 2006",
    "Brasil na Copa do Mundo FIFA de 2010",
    "Brasil na Copa do Mundo FIFA de 2014",
    "Brasil na Copa do Mundo FIFA de 2018",
    "Brasil na Copa do Mundo FIFA de 2022",
    "Brasil na Copa do Mundo FIFA de 2026"
]

def main():
    # Garante suporte a UTF-8/Emojis em consoles Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Pipeline de Ingestao de Dados para o BrasilnaCopaAI. "
                    "Coleta, limpa e estruturaliza artigos da Wikipedia localmente."
    )
    
    parser.add_argument(
        "--pages", "-p",
        nargs="+",
        help="Lista de titulos de paginas da Wikipedia para ingerir. "
             "Se omitido, utilizara a lista de artigos padrao.",
        default=None
    )
    
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Forca a atualizacao de todos os arquivos coletados, "
             "baixando as versoes mais recentes diretamente da Wikipedia."
    )
    
    parser.add_argument(
        "--user-agent", "-u",
        type=str,
        default="BrasilnaCopaAI/1.0 (daniel@exemplo.com)",
        help="User-agent customizado para fazer as requisicoes a API da Wikipedia."
    )

    args = parser.parse_args()

    # Define quais paginas processar
    pages_to_process = args.pages if args.pages is not None else DEFAULT_PAGES

    print("====================================================")
    print("🇧🇷  INICIALIZANDO PIPELINE DE INGESTÃO - BRASILNACOPAAI  🇧🇷")
    print("====================================================")
    print(f"📄 Artigos a processar: {pages_to_process}")
    print(f"🔄 Forçar re-importação da web: {'Sim' if args.force else 'Não'}")
    print(f"👤 User-Agent: {args.user_agent}")
    print("----------------------------------------------------")

    try:
        # Inicializa o processador orquestrador
        processor = WikipediaProcessor(
            raw_dir="data/raw",
            processed_dir="data/processed",
            user_agent=args.user_agent
        )
        
        # Executa o pipeline completo
        processed_files = processor.run_pipeline(
            page_titles=pages_to_process,
            force_update=args.force
        )
        
        print("----------------------------------------------------")
        print(f"✨ Sucesso! {len(processed_files)} de {len(pages_to_process)} artigos processados.")
        print("====================================================")
        
    except Exception as e:
        print(f"💥 Erro critico ao executar o pipeline: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
