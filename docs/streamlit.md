# 🎨 Interface Frontend com Streamlit

Este documento detalha o design, a implementação e as decisões da etapa de **Interface Streamlit (Epic 7)** do projeto **BrasilnaCopaAI**.

---

## 🏗️ O que foi feito

Nesta etapa, implementamos a interface visual (UI/UX) do chatbot utilizando o **Streamlit**. O aplicativo web permite interagir diretamente com a API FastAPI, configurando parâmetros do RAG (como número de fontes `k`), visualizando o status de conectividade em tempo real, limpando o histórico das mensagens e exibindo as fontes originais utilizadas para cada resposta com links clicáveis.

---

## 🛠️ Como foi feito

A interface visual foi concentrada no arquivo [app.py](../streamlit/app.py) e estruturada nas seguintes áreas:

### 1. Configurações na Barra Lateral (Sidebar)
* **Slider de Top-K**: Controle dinâmico permitindo ao usuário selecionar de 1 a 12 chunks para a recuperação semântica no ChromaDB.
* **Slider de Temperatura (Criatividade)**: Ajusta o nível de temperatura da LLM (de `0.0` a `1.5`) para regular o determinismo ou inventividade das respostas geradas.
* **Botão "Editar Prompt do Sistema"**: Aciona uma janela de diálogo (`st.dialog`) onde desenvolvedores e usuários podem inspecionar, customizar ou restaurar o System Prompt utilizado na cadeia RAG.
* **Monitor de Conexão com API**:
  * Realiza uma chamada de ping em `/health` e exibe em tempo real o status online/offline da API.
  * Se online, exibe a versão do backend e a saúde da base vetorial (chunks cadastrados).
* **Botão "Limpar Histórico"**: Remove todas as mensagens salvas na memória local da sessão (`st.session_state.messages`) e reinicia a página.
* **Sobre o Projeto**: Explica detalhadamente o escopo do RAG focado nas Copas do Mundo da Seleção Brasileira.

### 2. Painel de Conversação (Main Layout)
* **Design Premium**: Customização com CSS embutido utilizando o tema sofisticado verde e amarelo (cores da Seleção em gradientes escuros elegantes) e fonte moderna **Outfit**.
* **Visualização de Mensagens**: Mensagens do chat diferenciadas entre Usuário e Assistente de forma nativa e limpa (`st.chat_message`).
* **Indicadores de Carregamento**: Spinner animado ativo enquanto o backend FastAPI e a API Gemini processam a busca e a resposta.

### 3. Exibição de Fontes, Chunks e Resiliência
* Cada mensagem gerada pelo RAG apresenta uma caixa estilizada na base do balão (`source-container`) listando os links das fontes da Wikipedia consultadas.
* **Explorador de Chunks**: Cada resposta do assistente conta com um painel colapsável (`st.expander`) que revela os chunks textuais brutos retornados pelo ChromaDB que compuseram o prompt do Gemini, permitindo auditoria da resposta.
* Se a conexão falhar ou o Gemini estourar limites de cota (erros 429/503), o frontend captura a falha e avisa graciosamente na tela com mensagens compreensíveis (por exemplo, avisando para tentar novamente em instantes) sem quebrar o fluxo.

---

## 🧠 Por que foi feito assim

1. **Session State do Streamlit**: A persistência de mensagens e conversação em memória permite que o usuário navegue no chat de forma fluida sem perder o histórico ao alterar opções do slider de Top-K.
2. **Desduplicação de Fontes Clicáveis**: No backend filtramos as URLs únicas e no Streamlit as exibimos de forma elegante. Cada fonte é um link real apontando para a página exata da Wikipedia, permitindo ao usuário auditar a resposta da IA.

---

## 🚀 Como executar e testar

Para rodar a interface web, certifique-se de que o backend FastAPI está rodando na porta 8000.

### 1. Rodar o Backend API (FastAPI)
```bash
# Executando pelo interpretador do ambiente virtual (Recomendado)
.venv\Scripts\python -m app.main
# ou usando o uvicorn do ambiente virtual diretamente
.venv\Scripts\uvicorn app.main:app --reload --reload-dir app
```

### 2. Rodar o Frontend Web (Streamlit)
```bash
# Executando o streamlit do ambiente virtual
.venv\Scripts\streamlit run streamlit/app.py
```
A interface Streamlit abrirá automaticamente no seu navegador padrão em `http://localhost:8501`.
Você verá a barra lateral informando **● Backend Online** e poderá iniciar a conversa!
