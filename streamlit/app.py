import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Brasil na Copa AI 🇧🇷",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS personalizada para visual premium (Tema Copa do Brasil sofisticado)
st.markdown(
    """
    <style>
        /* Importação do Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        /* Reset de fonte global */
        html, body, [class*="css"], .stApp {
            font-family: 'Outfit', sans-serif;
            background-color: #0b100d;
            color: #f0f4f1;
        }

        /* Gradiente no título principal */
        .main-title {
            background: linear-gradient(135deg, #00DF89 0%, #FFDD00 50%, #0070FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.5rem;
            letter-spacing: -1px;
            animation: fadeIn 1s ease-out;
        }

        .subtitle {
            text-align: center;
            color: #8c9e90;
            font-size: 1.15rem;
            margin-bottom: 2rem;
            font-weight: 300;
        }

        /* Estilização dos Cards com Efeito de Vidro (Glassmorphism) */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
        }
        
        .glass-card:hover {
            border-color: rgba(0, 223, 137, 0.3);
            box-shadow: 0 8px 32px 0 rgba(0, 223, 137, 0.08);
            transform: translateY(-2px);
        }

        /* Indicador de Status */
        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }
        
        .status-online {
            background-color: rgba(0, 223, 137, 0.15);
            color: #00DF89;
            border: 1px solid rgba(0, 223, 137, 0.3);
        }
        
        .status-offline {
            background-color: rgba(255, 75, 75, 0.15);
            color: #FF4B4B;
            border: 1px solid rgba(255, 75, 75, 0.3);
        }

        /* Animações simples */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Botões customizados */
        div.stButton > button {
            background: linear-gradient(135deg, #00DF89 0%, #00A669 100%);
            color: #0b100d;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        div.stButton > button:hover {
            background: linear-gradient(135deg, #FFDD00 0%, #D4B800 100%);
            color: #0b100d;
            box-shadow: 0 0 15px rgba(255, 221, 0, 0.4);
            transform: scale(1.02);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar de Configurações e Sobre
with st.sidebar:
    st.markdown("<h2 style='color: #00DF89;'>Configurações</h2>", unsafe_allow_html=True)
    st.markdown("Ajustes da IA e monitoramento de conexão.")
    
    st.markdown("---")
    st.markdown("### Status da Conexão")
    
    # Função para testar conexão com o backend FastAPI
    def check_backend_health():
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=3)
            if response.status_code == 200:
                data = response.json()
                return True, data
        except Exception:
            pass
        return False, None

    is_online, health_data = check_backend_health()
    
    if is_online:
        st.markdown(
            f'<span class="status-badge status-online">● Backend Online</span>', 
            unsafe_allow_html=True
        )
        st.caption(f"Versão da API: {health_data.get('version', 'Desconhecida')}")
        st.caption(f"Banco de Dados: {health_data.get('database', 'Desconectado')}")
    else:
        st.markdown(
            f'<span class="status-badge status-offline">● Backend Offline</span>', 
            unsafe_allow_html=True
        )
        st.caption("Verifique se o backend em FastAPI está rodando.")

    st.markdown("---")
    st.markdown("### Sobre o Projeto")
    st.info(
        "**BrasilnaCopaAI** utiliza RAG (Retrieval-Augmented Generation) "
        "com dados da Wikipedia e a API do Gemini para responder "
        "com total precisão sobre a Seleção Brasileira na Copa de 2026."
    )

# Layout Principal da Página
st.markdown('<h1 class="main-title">Brasil na Copa AI 🇧🇷</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Seu assistente inteligente para a Copa do Mundo FIFA 2026</p>', unsafe_allow_html=True)

# Grid Layout com 2 colunas para dashboard inicial
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div class="glass-card">
            <h3 style="color: #00DF89; margin-top:0;">🤖 Assistente Virtual</h3>
            <p>O chatbot está pronto para responder perguntas de forma estruturada. Uma vez que o backend
               estiver ativo e a base de dados populada, as interações por chat estarão habilitadas nesta seção.</p>
            <p>Tente perguntar futuramente sobre:</p>
            <ul>
                <li><i>Grupo do Brasil e adversários</i></li>
                <li><i>Lista de convocados da seleção</i></li>
                <li><i>Estádios e calendário de jogos</i></li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="glass-card">
            <h3 style="color: #FFDD00; margin-top:0;">📊 Base de Conhecimento RAG</h3>
            <p>Este sistema não faz buscas abertas na web. As respostas são geradas com base estrita nos
               documentos ingeridos e vetorizados da Wikipedia, garantindo confiabilidade completa.</p>
            <p><b>Status da Base:</b></p>
            <ul>
                <li>Artigos mapeados da Wikipedia: <b>Pendente Ingestão</b></li>
                <li>Chunks indexados no ChromaDB: <b>0 chunks</b></li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Botão de Teste de Conectividade Interativo
st.markdown("<h3 style='text-align: center;'>Testar Conectividade</h3>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #8c9e90;'>Clique no botão abaixo para verificar a conectividade local direta com a API do FastAPI.</p>", 
    unsafe_allow_html=True
)

left_space, button_col, right_space = st.columns([2, 1, 2])
with button_col:
    if st.button("Ping Backend API", use_container_width=True):
        if is_online:
            st.success(f"Conexão bem-sucedida com {BACKEND_URL}!")
            st.json(health_data)
        else:
            st.error(f"Não foi possível conectar a {BACKEND_URL}. Certifique-se de que a API está rodando localmente.")
