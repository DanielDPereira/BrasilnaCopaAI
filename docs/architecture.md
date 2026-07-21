# 🏗️ Arquitetura Detalhada e Fluxos do Sistema

Este documento descreve detalhadamente a arquitetura do **BrasilnaCopaAI**, ilustrando a comunicação entre os componentes, os fluxos internos de dados e as estratégias aplicadas de processamento de texto e geração de respostas baseadas em **Retrieval-Augmented Generation (RAG)**.

---

# 🏗 Arquitetura da Solução

O projeto é estruturado de forma desacoplada em duas aplicações independentes que se comunicam via HTTP (JSON):
1. **Backend (API FastAPI)**: Responsável por gerenciar o pipeline de dados, a indexação semântica, a busca vetorial no ChromaDB e a orquestração do prompt enricher junto à API do Google Gemini.
2. **Frontend (Interface Streamlit)**: Camada focada exclusivamente na interface do usuário, encarregada de exibir a caixa de diálogo do chat e renderizar as respostas provenientes do backend.

```text
                 ┌──────────────────────────┐
                 │        Usuário           │
                 └─────────────┬────────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │       Streamlit UI       │
                 └─────────────┬────────────┘
                               │ HTTP
                               ▼
                 ┌──────────────────────────┐
                 │        FastAPI API       │
                 └─────────────┬────────────┘
                               │
                  ┌────────────┴─────────────┐
                  │                          │
                  ▼                          ▼
          LangChain Pipeline         Google Gemini API
                  │
                  ▼
             ChromaDB
                  │
                  ▼
     Documentos indexados da Wikipedia
```

---

# 🔄 Fluxo Geral da Aplicação

Sempre que o usuário interage enviando uma pergunta, a aplicação segue as seguintes etapas:

```text
[Usuário] ──(Pergunta)──> [Interface Streamlit] ──(HTTP request)──> [FastAPI Backend]
                                                                            │
                                                                            ▼
                                                                  [LangChain Pipeline]
                                                                            │
                                                                            ▼
                                                                  [Busca Vetorial]
                                                                            │
                                                                            ▼
                                                                  [ChromaDB (Persist)]
                                                                            │
                                                                            ▼
[Interface Streamlit] <──(HTTP response)── [FastAPI] <─── [Gemini API] <── Chunks
```

---

# 📚 Fluxo de Ingestão de Dados

Antes de disponibilizar o chatbot, é necessário coletar e organizar os dados na base de conhecimento. Esse processo ocorre offline nas seguintes etapas:

```text
[Wikipedia API] ──> [Coleta] ──> [Limpeza] ──> [Normalização] ──> [Chunking] ──> [Embeddings] ──> [ChromaDB]
```

1. **Coleta**: Busca os artigos recomendados da Wikipedia por meio da API de busca.
2. **Limpeza**: Remoção de links quebrados, tags HTML, caracteres indesejados e seções desnecessárias.
3. **Normalização**: Estruturação dos metadados e correção de acentuação.
4. **Chunking**: Divisão dos textos em partes menores (chunks) com sobreposição controlada (overlap) para manter a coesão semântica.
5. **Embeddings**: Conversão do texto em representações vetoriais de alta dimensão.
6. **ChromaDB**: Armazenamento persistente local dos vetores.

---

# 🔎 Fluxo de Consulta (RAG)

Quando a pergunta chega ao backend, ela passa por uma etapa de **Query Expansion** (expansão de consultas) para assegurar o maior índice de cobertura (recall) semântica. O fluxo de orquestração detalhado do pipeline é ilustrado a seguir:

```text
                                              ┌───> [Busca Vetorial (Variação 1)] ──┐
                                              ├───> [Busca Vetorial (Variação 2)] ──┼─> [Unificar & Desduplicar] ──> [Prompt Contexto] ──> [Gemini] ──> [Resposta]
[Pergunta] ──> [Query Expansion via LLM] ────┼───> [Busca Vetorial (Variação 3)] ──┤
                                              └───> [Busca Vetorial (Original)] ───┘
```

Os embeddings de busca são gerados localmente utilizando um modelo ONNX em CPU (ou via chamadas ao Gemini, de acordo com as configurações do `.env`).

---

# 🧩 Componentes da Aplicação

### FastAPI (Backend)
Responsável por conter e aplicar as regras de negócio da aplicação. Suas obrigações incluem:
- Receber e validar as requisições HTTP (pergunta do usuário).
- Executar a expansão de consultas em 3 perguntas alternativas para cobrir tópicos relacionados.
- Converter as consultas em vetores de alta dimensionalidade (utilizando embeddings locais ONNX ou rotacionando chaves na API do Gemini).
- Consultar a base vetorial local do ChromaDB.
- Extrair, unificar e desduplicar os trechos de texto mais semelhantes.
- Injetar os trechos de contexto dentro do prompt.
- Fazer a chamada à API do Gemini e retornar o payload estruturado de resposta.

### Streamlit (Presentation Layer)
- Renderizar a interface gráfica e o fluxo de mensagens estilo chat.
- Controlar o estado de carregamento e exibição de erros.
- Não possui lógica de IA, conexões com banco vetorial ou chaves de API carregadas.

### Pipeline de Ingestão
Script utilitário executado sob demanda para atualizar a base vetorial. Ele extrai de forma limpa os artigos da Wikipedia do Brasil de 1930 a 2026, fatiando os arquivos de maneira estruturada e populando a coleção no ChromaDB.

### Pipeline RAG
Componente core desenvolvido em Python utilizando **LangChain** que orquestra:
1. **Query Expansion** (Expansão dinâmica via LLM em `MultiQueryRAGRetriever`).
2. **Retrieval** (Busca semântica avançada).
3. **Augmentation** (Formatação e injeção do prompt de contexto).
4. **Generation** (Chamada e tratamento de resposta do Gemini).

---

# 📦 Base de Conhecimento

A base de dados de conhecimento é construída com foco no escopo da Seleção Brasileira nas Copas do Mundo FIFA. A coleta abrange artigos como:
- **Copa do Mundo FIFA de 2026** (Artigo Geral).
- **Seleção Brasileira de Futebol** (História e Elenco).
- Detalhes de eliminatórias, grupos da competição, estatísticas e comissões técnicas oficiais.

> [!NOTE]
> O projeto funciona de forma estritamente fechada. Não são feitas buscas em tempo real na web durante a execução do chat, forçando o modelo a responder com base no que está contido no banco ChromaDB.

---

# 🧠 Estratégia de Recuperação e Engenharia de Prompt

### Recuperação Semântica
Para evitar alucinações e respostas incorretas, utilizamos busca semântica em base local:
1. A pergunta do usuário é convertida em um vetor usando o mesmo modelo de embeddings usado na ingestão de dados.
2. É feita uma busca de vizinhos mais próximos no ChromaDB.
3. Apenas os **K** chunks mais relevantes são retornados.

### Prompt de Instrução do Sistema (System Prompt)
O modelo de linguagem recebe instruções rígidas de comportamento:
- Responder **apenas** utilizando as informações fornecidas nos documentos de contexto.
- Se o contexto não contiver informações suficientes, o modelo deve responder expressamente: *"Não possuo essa informação em minha base de dados sobre a Seleção Brasileira nas Copas do Mundo."*
- Proibido inventar fatos ou utilizar conhecimentos externos que divirjam do contexto.
- O idioma de resposta será exclusivamente português do Brasil.

---

## 🔗 Veja Também

* 📋 **[Roadmap e Backlog](backlog.md)**
* ⚙️ **[Desenvolvimento e Convenções](development.md)**
* 🏠 **[Voltar ao README](../README.md)**
