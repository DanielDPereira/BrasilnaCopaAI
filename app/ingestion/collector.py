import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import wikipediaapi

class WikipediaCollector:
    """
    Classe responsavel por coletar artigos da Wikipedia de forma automatica
    e salva-los em formato bruto (.json) para processamento posterior.
    """
    def __init__(self, raw_dir: str = "data/raw", user_agent: str = "BrasilnaCopaAI/1.0 (daniel@exemplo.com)"):
        self.raw_dir = raw_dir
        self.user_agent = user_agent
        
        # Inicializa o cliente da Wikipedia em português
        self.wiki = wikipediaapi.Wikipedia(
            user_agent=self.user_agent,
            language="pt"
        )
        
        # Garante que o diretorio de dados brutos existe
        os.makedirs(self.raw_dir, exist_ok=True)

    def _sanitize_filename(self, title: str) -> str:
        """Sanitiza o titulo do artigo para ser usado como nome de arquivo."""
        # Remove caracteres nao alfanumericos ou espacos
        sanitized = re.sub(r'[^\w\s-]', '', title)
        # Substitui espacos e hifens por underscores
        sanitized = re.sub(r'[\s-]+', '_', sanitized)
        return sanitized.lower().strip()

    def _build_markdown_text(self, page) -> str:
        """
        Gera uma string formatada em Markdown preservando a hierarquia de cabeçalhos
        a partir das seções estruturadas da página da Wikipedia.
        """
        blacklisted_sections = [
            "referências",
            "ligações externas",
            "ver também",
            "notas",
            "bibliografia",
            "leitura adicional",
            "outros projetos"
        ]

        def build_sections_markdown(sections, level=2) -> str:
            md = []
            for section in sections:
                if section.title.lower() in blacklisted_sections:
                    continue
                md.append(f"{'#' * level} {section.title}")
                if section.text.strip():
                    md.append(section.text.strip())
                if section.sections:
                    md.append(build_sections_markdown(section.sections, level + 1))
            return "\n\n".join(md)

        content_parts = []
        content_parts.append(f"# {page.title}")
        if page.summary.strip():
            content_parts.append(page.summary.strip())
            
        if page.sections:
            content_parts.append(build_sections_markdown(page.sections))
            
        return "\n\n".join(content_parts)

    def fetch_page(self, page_title: str, force_update: bool = False) -> Optional[str]:
        """
        Coleta um artigo da Wikipedia pelo titulo e salva em JSON na pasta de dados brutos.
        
        Args:
            page_title: O titulo do artigo na Wikipedia.
            force_update: Se True, sobrescreve o arquivo bruto se ja existir.
            
        Returns:
            O caminho do arquivo salvo se bem-sucedido, None caso contrario.
        """
        filename = f"{self._sanitize_filename(page_title)}.json"
        filepath = os.path.join(self.raw_dir, filename)
        
        # Verifica se o arquivo ja existe e nao requer atualizacao forcada
        if os.path.exists(filepath) and not force_update:
            print(f"ℹ️ Artigo '{page_title}' ja existe localmente em {filepath}. Pulando coleta.")
            return filepath

        print(f"📥 Coletando artigo '{page_title}' da Wikipedia...")
        try:
            page = self.wiki.page(page_title)
            
            if not page.exists():
                print(f"❌ Erro: Artigo '{page_title}' nao existe na Wikipedia em portugues.")
                return None
            
            # Constrói o texto formatado em Markdown preservando as seções
            markdown_text = self._build_markdown_text(page)
            
            # Estrutura os dados brutos obtidos
            raw_data: Dict[str, Any] = {
                "title": page.title,
                "url": page.fullurl,
                "text": markdown_text,
                "summary": page.summary,
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Salva o arquivo JSON
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(raw_data, f, ensure_ascii=False, indent=4)
                
            print(f"✅ Artigo '{page_title}' salvo com sucesso em: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Erro inesperado ao coletar '{page_title}': {str(e)}")
            return None

    def fetch_multiple_pages(self, page_titles: List[str], force_update: bool = False) -> List[str]:
        """
        Coleta multiplos artigos da Wikipedia.
        
        Args:
            page_titles: Lista com titulos de artigos.
            force_update: Se True, atualiza todos os artigos sobrescrevendo os existentes.
            
        Returns:
            Lista de caminhos de arquivos salvos com sucesso.
        """
        saved_paths = []
        for title in page_titles:
            path = self.fetch_page(title, force_update=force_update)
            if path:
                saved_paths.append(path)
        return saved_paths
