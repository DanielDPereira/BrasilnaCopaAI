# 🚀 Backend API com FastAPI

Este documento detalha o design, a implementação e as decisões da etapa de **Backend API FastAPI (Epic 6)** do projeto **BrasilnaCopaAI**.

---

## 🏗️ O que foi feito

Nesta etapa, expusemos a funcionalidade de chat com busca e respostas baseadas em Inteligência Artificial através de endpoints HTTP utilizando o **FastAPI**. Os endpoints possuem esquemas de entrada e saída fortemente tipados e validados, além de documentação automática e interativa fornecida pelo Swagger UI.

---

## 🛠️ Como foi feito

A lógica do servidor API foi concentrada no arquivo [main.py](../app/main.py) e estruturada da seguinte forma:

### 1. Esquemas de Dados Pydantic
* **`ChatRequest`**:
  * `message: str` (Obrigatório, tamanho mínimo de 1 caractere).
  * `k: int` (Opcional, com padrão `4`, limitado entre `1` e `10` via validações do Pydantic).
* **`ChatSource`**:
  * `title: str` (Título do artigo retornado da base de conhecimento).
  * `url: str` (Link direto para o artigo correspondente na Wikipedia).
* **`ChatResponse`**:
  * `response: str` (A resposta final gerada pelo Gemini).
  * `sources: List[ChatSource]` (Coleção das fontes exclusivas e sem repetições que serviram como embasamento).

### 2. Endpoints HTTP expostos
* **`GET /health`**:
  * Usado para monitorar a saúde da aplicação.
  * Além do status geral, ele realiza uma conexão à coleção ativa do ChromaDB em tempo real e reporta a quantidade de chunks indexados no banco vetorial.
* **`POST /chat`**:
  * Ponto de entrada para a interface interagir com o pipeline RAG.
  * Instancia a cadeia RAG, consulta o banco vetorial pelas fontes semânticas, chama o modelo Gemini (configurado no Epic 5) para gerar a resposta, realiza o filtro para eliminar fontes com URLs duplicadas e retorna a resposta estruturada.

### 3. Tratamento de Erros e Logs
* Estrutura de logging integrada para registrar no terminal qualquer falha ocorrida em tempo de execução.
* Captura graciável de exceções do Gemini: Se as chamadas ao modelo falharem devido a quota esgotada da API (`RESOURCE_EXHAUSTED` / `429`), o backend responde ao cliente com `503 Service Unavailable` com uma mensagem amigável explicativa, em vez de retornar um erro silencioso 500.

---

## 🧠 Por que foi feito assim

1. **Desduplicação de Fontes**: É comum que chunks diferentes pertençam ao mesmo artigo e, consequentemente, compartilhem o mesmo link URL de origem. Implementamos um filtro no backend para consolidar as fontes exibidas e evitar poluir a interface do usuário com links repetidos.
2. **FastAPI Swagger**: Configurando classes e metadados no FastAPI, a API se auto-documenta no padrão OpenAPI. A documentação interativa pode ser acessada em `/docs` no navegador, permitindo testar requisições diretamente.

---

## 🚀 Como testar e executar

### 1. Executar os testes automatizados
```bash
pytest tests/test_api.py
```
* Valida o monitoramento em `/health`, as respostas corretas e checagem de fontes duplicadas em `/chat`, validação de erros Pydantic (mensagens vazias) e tratamento do erro de limite de quota (503).

### 2. Rodar a API localmente
```bash
python -m app.main
# ou
uvicorn app.main:app --reload
```
A API iniciará no endereço `http://127.0.0.1:8000`. Você pode testar os endpoints de duas maneiras:
* **Interativo (Swagger UI)**: Acesse [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) e use a aba "Try it out" na rota `/chat`.
* **Via cURL (terminal)**:
  ```bash
  curl -X 'POST' \
    'http://127.0.0.1:8000/chat' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "message": "Quais países vão sediar a Copa de 2026?",
    "k": 4
  }'
  ```
