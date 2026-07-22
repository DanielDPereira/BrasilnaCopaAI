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

# Estilização CSS personalizada para visual premium
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"], .stApp {
            font-family: 'Outfit', sans-serif;
            background-color: #0b100d;
            color: #f0f4f1;
        }

        .main-title {
            background: linear-gradient(135deg, #00DF89 0%, #FFDD00 50%, #0070FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.8rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.2rem;
            letter-spacing: -1px;
        }

        .subtitle {
            text-align: center;
            color: #8c9e90;
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
            font-weight: 300;
        }

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

        .source-container {
            margin-top: 8px;
            padding: 8px 12px;
            background-color: rgba(255, 255, 255, 0.02);
            border-left: 3px solid #00DF89;
            border-radius: 4px;
        }

        .source-link {
            color: #FFDD00 !important;
            text-decoration: none;
            font-weight: 600;
            margin-right: 15px;
        }

        .source-link:hover {
            color: #00DF89 !important;
            text-decoration: underline;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

DEFAULT_SYSTEM_PROMPT = """Você é um assistente de IA especialista na história e participação da Seleção Brasileira nas Copas do Mundo FIFA.
Sua base de conhecimento inclui a trajetória do Brasil em todas as edições de Copas do Mundo, detalhes de partidas históricas (como o Maracanaço de 1950 e o Mineiraço de 2014), conquistas, estatísticas e o desempenho de grandes lendas e jogadores notórios (como Pelé, Garrincha, Neymar, Ronaldo Nazário, Romário, Zico, Rivaldo, Cafu, Ronaldinho Gaúcho, Jairzinho, Bebeto, Roberto Carlos, Kaká e Zagallo), bem como treinadores históricos (como Luiz Felipe Scolari e Carlos Alberto Parreira).

Responda às perguntas dos usuários de forma educada, precisa, detalhada e rica, utilizando estritamente e exclusivamente as informações fornecidas no contexto abaixo.

Diretrizes importantes:
1. Responda apenas com base nas informações fornecidas no contexto. Não utilize conhecimento prévio ou externo ao contexto sob nenhuma circunstância.
2. Se as informações fornecidas no contexto não contiverem a resposta para a pergunta, responda obrigatoriamente e de forma literal: "Não possuo essa informação em minha base de dados sobre a Seleção Brasileira nas Copas do Mundo."
3. Não alucine, não invente fatos, elencos, datas, placares ou estatísticas que não estejam explicitamente no contexto.
4. Responda sempre em português do Brasil.
5. **Seja detalhado e contextualize suas respostas:** Em vez de dar respostas extremamente curtas de uma única frase, elabore explicações completas contendo detalhes adicionais e fatos históricos relevantes presentes no contexto (como o número de jogos disputados, gols marcados, adversários enfrentados, atuações marcantes e curiosidades relacionadas), enriquecendo a resposta.
6. **Formatação Premium:** Organize a resposta de forma clara e profissional, utilizando marcações em negrito, tópicos (bullet points) ou parágrafos bem definidos para estruturar a informação de forma elegante e legível.

Contexto de referência:
{context}"""

# Inicialização de histórico do chat e configurações em session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "custom_prompt" not in st.session_state:
    st.session_state.custom_prompt = DEFAULT_SYSTEM_PROMPT
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.0

# Decorator de diálogo para edição de prompt de sistema
@st.dialog("⚙️ Prompt de Sistema do RAG", width="large")
def show_prompt_editor():
    st.markdown("Ajuste as diretrizes e instruções do assistente para testar e brincar com o RAG.")
    
    edited_prompt = st.text_area(
        "Instrução do Sistema (System Prompt)",
        value=st.session_state.custom_prompt,
        height=380,
        help="Mantenha a marcação {context} no final do prompt para que o ChromaDB possa injetar os chunks de contexto."
    )
    
    # Validação simples de segurança
    if "{context}" not in edited_prompt:
        st.warning("⚠️ Atenção: O prompt não contém a variável '{context}'. O banco vetorial não poderá injetar as informações recuperadas.")
        
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Salvar Prompt", use_container_width=True):
            st.session_state.custom_prompt = edited_prompt
            st.toast("Prompt de sistema personalizado salvo!", icon="💾")
            st.rerun()
    with col2:
        if st.button("Restaurar Padrão", use_container_width=True):
            st.session_state.custom_prompt = DEFAULT_SYSTEM_PROMPT
            st.toast("Prompt padrão restaurado!", icon="🔄")
            st.rerun()

# Sidebar de Configurações e Sobre
with st.sidebar:
    st.markdown("<h2 style='color: #00DF89; margin-bottom: 0.5rem;'>Configurações</h2>", unsafe_allow_html=True)
    st.markdown("Ajustes do pipeline RAG e monitoramento.")
    st.markdown("---")
    
    # Controle de Top-K (k)
    k_value = st.slider(
        "Quantidade de Contexto (Top-K)",
        min_value=1,
        max_value=12,
        value=6,
        help="Controla o número de fragmentos de documentos (chunks) recuperados para embasar a resposta."
    )
    
    # Controle de Temperatura
    temp_value = st.slider(
        "Criatividade (Temperatura)",
        min_value=0.0,
        max_value=1.5,
        value=st.session_state.temperature,
        step=0.1,
        help="Valores mais baixos (ex: 0.0) garantem respostas precisas e determinísticas baseadas no contexto. Valores altos trazem mais expressividade."
    )
    st.session_state.temperature = temp_value
    
    # Botão para editar prompt (dialog)
    if st.button("⚙️ Editar Prompt do Sistema", use_container_width=True):
        show_prompt_editor()
        
    # Botão para limpar histórico de conversa
    if st.button("🗑️ Limpar Histórico do Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("### Status da Conexão")
    
    # Função para testar conexão com o backend FastAPI
    def check_backend_health():
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=2)
            if response.status_code == 200:
                return True, response.json()
        except Exception:
            pass
        return False, None

    is_online, health_data = check_backend_health()
    
    if is_online:
        st.markdown(
            '<span class="status-badge status-online">● Backend Online</span>', 
            unsafe_allow_html=True
        )
        st.caption(f"Versão da API: {health_data.get('version', 'Desconhecida')}")
        st.caption(f"Banco de Dados: {health_data.get('database', 'Desconectado')}")
    else:
        st.markdown(
            '<span class="status-badge status-offline">● Backend Offline</span>', 
            unsafe_allow_html=True
        )
        st.caption("Verifique se o backend em FastAPI está rodando na porta 8000.")

    st.markdown("---")
    st.markdown("### Sobre o Projeto")
    st.info(
        "**BrasilnaCopaAI** utiliza RAG (Retrieval-Augmented Generation) "
        "com dados da Wikipedia e a API do Gemini para responder "
        "com precisão histórica sobre a Seleção Brasileira nas Copas do Mundo."
    )

# Layout Principal da Página
st.markdown('<h1 class="main-title">Brasil na Copa AI 🇧🇷</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Seu assistente inteligente sobre a história da Seleção Brasileira nas Copas do Mundo</p>', unsafe_allow_html=True)

# Container para as mensagens do chat
chat_placeholder = st.container()

with chat_placeholder:
    # Exibe histórico do chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Se for do assistente e possuir fontes, exibe-as formatadas
            if message["role"] == "assistant":
                if message.get("sources"):
                    st.markdown('<div class="source-container"><b>Fontes utilizadas:</b><br>', unsafe_allow_html=True)
                    sources_html = ""
                    for src in message["sources"]:
                        title = src.get("title", "Artigo")
                        url = src.get("url", "")
                        if url and url != "Sem link de origem":
                            sources_html += f'<a class="source-link" href="{url}" target="_blank">📄 {title}</a> '
                        else:
                            sources_html += f'<span style="color:#8c9e90; margin-right:15px;">📄 {title} (Sem Link)</span>'
                    st.markdown(sources_html + '</div>', unsafe_allow_html=True)
                
                # Exibe chunks de contexto recuperados se disponíveis
                if message.get("context_chunks"):
                    with st.expander("🔍 Visualizar Chunks do ChromaDB (Contexto Recuperado)"):
                        for idx, chunk in enumerate(message["context_chunks"]):
                            st.markdown(f"**Trecho {idx + 1} — {chunk['title']}**")
                            st.caption(f"Origem: {chunk['url']}")
                            st.code(chunk["content"], language="text")

# Entrada do chat
if user_input := st.chat_input("Pergunte algo sobre a Seleção nas Copas (ex: Quem foi o artilheiro em 1958?)"):
    # Exibe a pergunta imediatamente na tela
    with chat_placeholder:
        with st.chat_message("user"):
            st.markdown(user_input)
            
    # Adiciona a mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Chama o backend e aguarda resposta
    with chat_placeholder:
        with st.chat_message("assistant"):
            with st.spinner("Buscando no banco de conhecimento e gerando resposta..."):
                if not is_online:
                    error_msg = "Erro de conexão: Não foi possível conectar ao servidor backend em FastAPI. Certifique-se de que ele está rodando."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                else:
                    try:
                        # Envia prompt de sistema personalizado e temperatura configurados no frontend
                        payload = {
                            "message": user_input,
                            "k": k_value,
                            "custom_system_prompt": st.session_state.custom_prompt,
                            "temperature": st.session_state.temperature
                        }
                        response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
                        
                        if response.status_code == 200:
                            data = response.json()
                            answer = data.get("response", "")
                            sources = data.get("sources", [])
                            context_chunks = data.get("context_chunks", [])
                            
                            # Exibe a resposta
                            st.markdown(answer)
                            
                            # Exibe as fontes
                            if sources:
                                st.markdown('<div class="source-container"><b>Fontes utilizadas:</b><br>', unsafe_allow_html=True)
                                sources_html = ""
                                for src in sources:
                                    title = src.get("title", "Artigo")
                                    url = src.get("url", "")
                                    if url and url != "Sem link de origem":
                                        sources_html += f'<a class="source-link" href="{url}" target="_blank">📄 {title}</a> '
                                    else:
                                        sources_html += f'<span style="color:#8c9e90; margin-right:15px;">📄 {title} (Sem Link)</span>'
                                st.markdown(sources_html + '</div>', unsafe_allow_html=True)
                            
                            # Exibe os chunks recuperados
                            if context_chunks:
                                with st.expander("🔍 Visualizar Chunks do ChromaDB (Contexto Recuperado)"):
                                    for idx, chunk in enumerate(context_chunks):
                                        st.markdown(f"**Trecho {idx + 1} — {chunk['title']}**")
                                        st.caption(f"Origem: {chunk['url']}")
                                        st.code(chunk["content"], language="text")
                                
                            # Salva no histórico com todas as informações enriquecidas
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": answer,
                                "sources": sources,
                                "context_chunks": context_chunks
                            })
                        elif response.status_code == 503:
                            err_detail = response.json().get("detail", "Limite de quota temporariamente excedido.")
                            st.warning(err_detail)
                            st.session_state.messages.append({"role": "assistant", "content": f"Aviso: {err_detail}"})
                        else:
                            err_detail = response.json().get("detail", "Erro desconhecido no servidor.")
                            st.error(f"Erro {response.status_code}: {err_detail}")
                            st.session_state.messages.append({"role": "assistant", "content": f"Erro {response.status_code}: {err_detail}"})
                    except Exception as e:
                        err_msg = f"Falha ao processar requisição: {str(e)}"
                        st.error(err_msg)
                        st.session_state.messages.append({"role": "assistant", "content": err_msg})
