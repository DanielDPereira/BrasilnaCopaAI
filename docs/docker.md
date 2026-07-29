# 🐳 Execução e Empacotamento com Docker

Este documento detalha o empacotamento em containers e a orquestração utilizando o **Docker** e **Docker Compose** para o projeto **BrasilnaCopaAI**. Esta abordagem permite que o projeto seja executado de forma idêntica em qualquer sistema operacional (Linux, Windows, macOS), encapsulando dependências e isolando a execução de forma profissional.

---

## 🏗️ Arquitetura dos Containers

O projeto é dividido em dois containers principais mapeados em uma rede isolada do Docker Compose:

```text
[Usuário] ──> [Porta 8501] ──> [brasil-copa-frontend (Streamlit)]
                                           │
                                           │ (Rede Interna Docker)
                                           ▼
                              [Porta 8000] ──> [brasil-copa-backend (FastAPI)]
```

### 1. Backend (`Dockerfile.backend`)
* **Imagem Base**: `python:3.12-slim`.
* **Healthcheck**: Configurado para verificar periodicamente a integridade do endpoint `/health` via `curl`.
* **Inicialização Inteligente**: Utiliza um script de entrypoint Python (`docker/entrypoint.py`) que gerencia a preparação do ambiente no container de forma automática.
* **Volumes de Persistência**:
  * `chroma-data`: Persiste a base de dados vetorial ChromaDB.
  * `model-data`: Persiste os modelos de embeddings locais (se ativados).
  * `raw-data` e `processed-data`: Persiste os arquivos JSON brutos e higienizados.

### 2. Frontend (`Dockerfile.frontend`)
* **Imagem Base**: `python:3.12-slim`.
* **Comunicação**: Conecta-se diretamente ao container do backend utilizando o DNS interno do Docker (`http://backend:8000`).

---

## 🚀 Como Executar com Docker Compose

A grande vantagem da dockerização do projeto é que o pipeline de inicialização (download de modelos, coleta de dados da Wikipedia e indexação do ChromaDB) é executado de forma **100% autônoma** no primeiro boot!

### Passo 1: Pré-requisitos
* Ter o **Docker** e o **Docker Compose** instalados em sua máquina.
* Ter a chave de API do Gemini em mãos.

### Passo 2: Criar e Configurar o arquivo `.env`
Crie um arquivo `.env` na raiz do projeto contendo suas chaves. Exemplo:
```env
GEMINI_API_KEY=sua_chave_aqui
USE_LOCAL_EMBEDDINGS=true
```

### Passo 3: Iniciar o Docker Compose
Execute o comando a seguir na raiz do projeto:
```bash
docker compose up --build
```

#### O que acontecerá automaticamente no primeiro boot:
1. O Docker compilará as imagens do backend e frontend.
2. O backend iniciará e o script `docker/entrypoint.py` entrará em ação.
3. Se `USE_LOCAL_EMBEDDINGS=true`, ele baixará o modelo ONNX e tokenizer do Hugging Face.
4. Se o banco vetorial estiver vazio, ele iniciará a coleta da Wikipédia e fará a indexação no ChromaDB.
5. O backend FastAPI subirá.
6. O frontend Streamlit detectará que o backend está saudável (via healthcheck) e iniciará.

O chatbot estará acessível em: **[http://localhost:8501](http://localhost:8501)**.

---

## 🎛️ Comandos Úteis do Docker

* **Subir em segundo plano (detached mode):**
  ```bash
  docker compose up -d
  ```
* **Visualizar logs em tempo real:**
  ```bash
  docker compose logs -f
  ```
* **Visualizar logs apenas do backend ou do frontend:**
  ```bash
  docker compose logs -f backend
  docker compose logs -f frontend
  ```
* **Parar e remover os containers mantendo os dados persistidos:**
  ```bash
  docker compose down
  ```
* **Limpar os dados indexados e reiniciar do zero (deletando volumes):**
  ```bash
  docker compose down -v
  docker compose up --build
  ```

---

## 🔒 Considerações de Segurança e Isolamento

1. **Variáveis de Ambiente**: Nenhuma chave de API está embutida nas imagens Docker. Elas são injetadas dinamicamente via arquivo `.env` (que está no `.gitignore`).
2. **Execução sem Root**: Em ambientes de produção reais, recomenda-se configurar usuários não-root nos Dockerfiles para limitar os privilégios dentro do container.
3. **Isolamento de Portas**: Apenas as portas de rede necessárias (`8000` para a API Swagger e `8501` para o Streamlit) são expostas para o host externo. A comunicação interna ocorre em uma rede bridge segura e privada criada pelo compose.
