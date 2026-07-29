import sys
import os
from unittest.mock import patch, MagicMock

# Remove diretório local do sys.path temporariamente para evitar conflito com a pasta 'streamlit/' do projeto
original_path = sys.path.copy()
sys.path = [p for p in sys.path if p not in ("", os.getcwd(), os.path.abspath("."))]

try:
    from streamlit.testing.v1 import AppTest
finally:
    sys.path = original_path

@patch("requests.get")
def test_streamlit_app_compiles_and_renders(mock_get):
    # Simula resposta bem sucedida da API FastAPI (/health)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "healthy",
        "version": "0.1.0",
        "database": "connected (500 chunks)"
    }
    mock_get.return_value = mock_resp

    # Inicializa o AppTest a partir do arquivo de entrada do Streamlit
    at = AppTest.from_file("streamlit/app.py")
    
    # Executa a renderização com timeout estendido de segurança
    at.run(timeout=10)
    
    # Garante que não houve exceções durante a compilação e renderização
    assert not at.exception
    
    # Valida a presença dos elementos fundamentais do layout sidebar
    assert len(at.slider) == 2
    slider_k = at.slider[0]
    assert slider_k.label == "Quantidade de Contexto (Top-K)"
    assert slider_k.value == 6
    
    slider_temp = at.slider[1]
    assert slider_temp.label == "Criatividade (Temperatura)"
    assert slider_temp.value == 0.0
    
    # Valida a presença do botão de limpeza de histórico no sidebar
    assert len(at.button) == 2
    assert at.button[0].label == "⚙️ Editar Prompt do Sistema"
    assert at.button[1].label == "🗑️ Limpar Histórico do Chat"
