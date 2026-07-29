# 🇧🇷 BrasilnaCopaAI

> Um chatbot inteligente baseado em **Retrieval-Augmented Generation (RAG)** capaz de responder perguntas sobre a história e participação da **Seleção Brasileira nas Copas do Mundo FIFA** (geral de todas as edições), utilizando documentos da Wikipedia como base de conhecimento e o Google Gemini para geração de respostas contextualizadas.

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/status-conclu%C3%ADdo-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/tests-29%20passed-brightgreen" alt="Tests">
  <img src="https://img.shields.io/badge/Python-3.12%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.115%2B-009688" alt="FastAPI">
  <img src="https://img.shields.io/badge/Streamlit-1.x-FF4B4B" alt="Streamlit">
  <img src="https://img.shields.io/badge/LangChain-RAG-blueviolet" alt="LangChain">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

---

## 📖 Sobre o Projeto

O **BrasilnaCopaAI** é um projeto de portfólio desenvolvido com foco em Inteligência Artificial Generativa e Engenharia de Dados. 

Ao invés de depender do conhecimento padrão (e estático) de um modelo de linguagem, o sistema realiza buscas semânticas em um banco vetorial local contendo documentos extraídos da Wikipedia sobre a Seleção Brasileira nas Copas do Mundo. Apenas os trechos mais relevantes são enviados ao modelo generativo (**Google Gemini**), garantindo respostas confiáveis, contextualizadas e sem alucinações.

---

## 🎯 Escopo do MVP

O chatbot responderá perguntas exclusivamente sobre:
* **Seleção Brasileira**: Jogadores convocados, comissão técnica e histórico.
* **Partidas & Desempenho**: Grupos, fases da competição, adversários e estatísticas presentes nos documentos.

> [!IMPORTANT]
> Toda resposta gerada deve ter embasamento nos documentos indexados. Caso a informação não conste na base, o chatbot informará que não possui tal conhecimento, evitando inventar fatos.

---

## 🏗️ Arquitetura Simplificada

O projeto é dividido em dois serviços independentes que se comunicam via HTTP/JSON:
```text
[Usuário] ──> [Interface Streamlit] ──(HTTP)──> [Backend FastAPI]
                                                      │
                                    ┌─────────────────┴─────────────────┐
                                    ▼                                   ▼
                          [LangChain + ChromaDB]              [Google Gemini API]
```

Para mais detalhes sobre os fluxos de ingestão de dados e execução do pipeline RAG, consulte a [Documentação de Arquitetura](docs/architecture.md).

---

## 🛠️ Stack Tecnológica

* **Core**: Python 3.12+
* **Backend**: FastAPI, Uvicorn, Pydantic
* **Frontend**: Streamlit
* **IA & Orquestração**: LangChain e Google Gemini API
* **Banco Vetorial**: ChromaDB
* **Processamento de Dados**: Wikipedia API, Beautiful Soup, Pandas

---

## 📁 Estrutura de Pastas

```text
BrasilnaCopaAI/
├── app/                  # Código fonte do Backend (FastAPI)
│   ├── api/              # Rotas e controladores de endpoints
│   ├── ingestion/        # Coleta e processamento dos textos
│   ├── models/           # Esquemas de dados (Pydantic)
│   ├── rag/              # Orquestração RAG (LangChain)
│   ├── services/         # Integrações externas (Gemini/Wiki)
│   └── vectorstore/      # Configuração do banco vetorial
├── streamlit/            # Código fonte da Interface Web
├── data/                 # Bases de dados locais (raw, processed, db)
├── docs/                 # Documentação detalhada do projeto
├── tests/                # Testes automatizados (pytest)
└── requirements.txt      # Dependências do projeto
```

---

## 🚀 Como Executar o Projeto

Você pode executar o projeto de duas maneiras: utilizando o **Docker Compose** (método recomendado, automatizado e multiplataforma) ou **manualmente** (configurando o ambiente virtual Python local).

---

### Método A: Via Docker Compose (Recomendado 🐳)

Este é o método mais simples e rápido. O Docker se encarrega de instalar todas as dependências, baixar o modelo local de embeddings (se configurado) e rodar o pipeline de ingestão e indexação do ChromaDB de forma **100% automatizada** no primeiro boot.

#### Pré-requisitos:
* **Docker** e **Docker Compose** instalados na máquina.
* Chave de API do Google Gemini.

#### 1. Criar o arquivo `.env`
Crie um arquivo `.env` na raiz do projeto com as chaves necessárias (baseando-se no `.env.example`):
```env
GEMINI_API_KEY=sua_chave_aqui
USE_LOCAL_EMBEDDINGS=true
```

#### 2. Executar o Compose
Na raiz do repositório, execute:
```bash
docker compose up --build
```
Aguarde a inicialização. O frontend Streamlit estará disponível em **[http://localhost:8501](http://localhost:8501)** e o backend FastAPI Swagger em **[http://localhost:8000/docs](http://localhost:8000/docs)**.

Para mais detalhes sobre comandos e persistência de dados, consulte o [Guia de Execução com Docker](docs/docker.md).

---

### Método B: Execução Manual / Local 🐍

#### Pré-requisitos:
* **Python 3.12** ou superior instalado localmente.
* Chave de API do Google Gemini.

#### 1. Clonar o Repositório e Acessar a Pasta
```bash
git clone https://github.com/DanielDPereira/BrasilnaCopaAI.git
cd BrasilnaCopaAI
```

#### 2. Configurar o Ambiente Virtual
**No Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```
**No Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

#### 4. Configurar Variáveis de Ambiente e Modelo de Embeddings
Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:
```env
# Chave da API do Google Gemini
GEMINI_API_KEY=sua_chave_aqui

# (Opcional) Múltiplas chaves separadas por vírgula para tolerância a falhas
GEMINI_API_KEYS=chave_1,chave_2,chave_3

# Configuração para rodar offline / economizar cota da API (true/false)
USE_LOCAL_EMBEDDINGS=true

# Caminho do banco vetorial
CHROMA_DB_PATH=data/db
```

##### Se optar por utilizar Embeddings Locais (`USE_LOCAL_EMBEDDINGS=true`):
Para rodar sem depender das quotas de API do Gemini para embeddings, você deve baixar o modelo local executando:
```bash
python scripts/download_local_model.py
```
Isso baixará automaticamente os arquivos `model.onnx` e `tokenizer.json` do Hugging Face para a pasta `data/models/`.

#### 5. Ingestão e Indexação da Base de Conhecimento (Carga Inicial)
Para que o RAG funcione, você precisa coletar e popular o banco de dados vetorial local:

1. **Executar a Coleta e Limpeza (Wikipedia):**
   ```bash
   python -m app.ingestion.run
   ```
2. **Executar a Carga no Banco Vetorial (ChromaDB):**
   ```bash
   python -m app.vectorstore.populate
   ```

#### 6. Executar o Backend (FastAPI)
```bash
uvicorn app.main:app --reload --reload-dir app
```
* O backend rodará em `http://localhost:8000`.
* Acesse a documentação Swagger interativa em `http://localhost:8000/docs`.

#### 7. Executar o Frontend (Streamlit)
Em um novo terminal com o ambiente virtual ativado:
```bash
streamlit run streamlit/app.py
```
A interface do chat abrirá automaticamente no seu navegador padrão (em `http://localhost:8501`).

---

## 📚 Documentação Detalhada

Para aprofundar-se no projeto, consulte os guias disponíveis na pasta `docs/`:

1. 🏗️ **[Arquitetura Detalhada](docs/architecture.md)**: Entenda os fluxos detalhados de ingestão de dados, busca vetorial e prompt engineering.
2. 🐳 **[Execução com Docker](docs/docker.md)**: Detalhes sobre o empacotamento, volumes e comando docker compose.
3. ⚙️ **[Guia de Desenvolvimento e Convenções](docs/development.md)**: Padrões de código, Conventional Commits, branches (Git Flow) e como rodar a suíte de testes.
4. 🧪 **[Testes e Refinamentos (Épico 8)](docs/tests_refinement.md)**: Detalhes das métricas de qualidade, suíte de 29 testes unitários/integrados e resiliência de chaves.
5. 📋 **[Planejamento, Roadmap e Backlog](docs/backlog.md)**: Acompanhe o roadmap das 8 fases do projeto, as listas de tarefas (Tasks) por épicos e as definições de pronto (DoD).

---

## 📄 Licença e Autor

* **Autor**: Daniel Dias Pereira
* **Licença**: Distribuído sob a licença **MIT**. Veja o arquivo `LICENSE` para mais detalhes.
