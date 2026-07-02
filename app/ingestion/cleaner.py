import re

class TextCleaner:
    """
    Classe responsavel por limpar e normalizar o texto dos artigos extraidos da Wikipedia.
    Remove secoes de metadados irrelevantes do final da pagina e normaliza espacamento.
    """
    
    # Secoes comumente encontradas no final de artigos da Wikipedia que nao sao uteis para o RAG
    BLACKLISTED_SECTIONS = [
        "referências",
        "ligações externas",
        "ver também",
        "notas",
        "bibliografia",
        "leitura adicional",
        "outros projetos"
    ]

    def __init__(self):
        # Compila a regex para encontrar as secoes indesejadas (linhas com '== Nome da Secao ==', '=== Subsecao ===', etc.)
        # Captura a secao e tudo o que vier depois dela ate o fim do texto
        sections_pattern = "|".join(self.BLACKLISTED_SECTIONS)
        self.blacklist_regex = re.compile(
            rf"\n={{2,4}}\s*[^=]*({sections_pattern})[^=]*={{2,4}}.*", 
            re.IGNORECASE | re.DOTALL
        )

    def remove_blacklisted_sections(self, text: str) -> str:
        """
        Remove as secoes de referencias, ligacoes externas, etc., localizadas
        geralmente no final do artigo.
        """
        if not text:
            return ""
        # Substitui a primeira ocorrencia de uma secao da blacklist (e tudo apos ela) por vazio
        cleaned_text = self.blacklist_regex.sub("", text)
        return cleaned_text.strip()

    def normalize_whitespace(self, text: str) -> str:
        """
        Normaliza o espacamento no texto:
        - Remove espacos duplos
        - Remove linhas vazias em excesso (mantem no maximo uma linha em branco para separar paragrafos)
        - Remove espacos no inicio e fim de cada linha
        """
        if not text:
            return ""
        
        # Limpa espacos no fim/inicio de cada linha
        lines = [line.strip() for line in text.splitlines()]
        
        # Remove linhas em branco consecutivas
        normalized_lines = []
        previous_was_empty = False
        
        for line in lines:
            if line == "":
                if not previous_was_empty:
                    normalized_lines.append("")
                    previous_was_empty = True
            else:
                normalized_lines.append(line)
                previous_was_empty = False
                
        # Junta as linhas novamente
        text = "\n".join(normalized_lines)
        
        # Substitui tabulacoes e multiplos espacos horizontais por um espaco simples
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()

    def clean(self, text: str) -> str:
        """
        Executa todo o fluxo de limpeza no texto.
        
        Args:
            text: O texto bruto obtido da Wikipedia.
            
        Returns:
            O texto limpo e normalizado.
        """
        if not text:
            return ""
            
        # 1. Remove as secoes do final da pagina (referencias, etc.)
        cleaned = self.remove_blacklisted_sections(text)
        
        # 2. Normaliza os espacos e quebras de linha
        cleaned = self.normalize_whitespace(cleaned)
        
        return cleaned
