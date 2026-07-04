# 📋 Planejamento, Roadmap e Backlog do Projeto

Este documento detalha o planejamento do desenvolvimento do **BrasilnaCopaAI**, incluindo o Roadmap de entregas, o Backlog de tarefas organizado por Épicos, as regras de Definition of Done (DoD) e os critérios de conclusão do MVP.

---

# 🗺️ Roadmap de Desenvolvimento

O desenvolvimento do projeto é dividido em 8 fases principais, cada uma contendo objetivos claros e entregáveis tangíveis.

## Fase 1 — Planejamento
* **Objetivos**: Definir o escopo do projeto, arquitetura geral, stack tecnológica, estruturação do repositório e elaboração da documentação inicial.
* **Entregáveis**: README completo, estrutura inicial do projeto e preparação do ambiente.

## Fase 2 — Configuração do Ambiente
* **Objetivos**: Configuração do ambiente virtual Python, instalação de dependências, configuração base do FastAPI e do Streamlit, e parametrização das variáveis de ambiente.
* **Entregáveis**: API backend respondendo, interface inicial streamlit no ar e estrutura pronta para desenvolvimento.

## Fase 3 — Pipeline de Ingestão
* **Objetivos**: Coletar páginas e documentos de referência da Wikipedia, aplicar regras de limpeza nos textos coletados, normalizar documentos e estruturar o chunking com overlap.
* **Entregáveis**: Documentos limpos, processados e prontos para indexação semântica.

## Fase 4 — Banco Vetorial
* **Objetivos**: Configurar o banco de dados vetorial ChromaDB, definir a coleção adequada, armazenar os embeddings dos chunks gerados e validar consultas por proximidade.
* **Entregáveis**: Base de dados vetorial funcional e populada com os dados do MVP.

## Fase 5 — Implementação do Pipeline RAG
* **Objetivos**: Integrar o LangChain ao projeto, configurar e estruturar o retriever semântico, construir o contexto e formatar o System Prompt.
* **Entregáveis**: Mecanismo de recuperação de documentos funcional.

## Fase 6 — Integração com o Google Gemini
* **Objetivos**: Autenticar o cliente na API do Google Gemini, criar a lógica de envio do prompt enriquecido com o contexto recuperado e processar as respostas geradas.
* **Entregáveis**: Chatbot gerando respostas baseadas estritamente no contexto via API.

## Fase 7 — Interface Streamlit
* **Objetivos**: Criar a interface visual do chat, implementar campo de perguntas e exibição de respostas, exibir histórico de conversas e integrar as chamadas HTTP com o FastAPI.
* **Entregáveis**: Chatbot interativo e usável através de uma interface web.

## Fase 8 — Testes e Refinamento
* **Objetivos**: Validar o pipeline RAG de ponta a ponta, escrever testes unitários, realizar ajustes finos na engenharia de prompt, corrigir bugs e refatorar o código.
* **Entregáveis**: Versão 1.0.0 estável do BrasilnaCopaAI.

---

# 📋 Backlog de Desenvolvimento

O desenvolvimento é conduzido por meio de tarefas organizadas em Épicos e Features.

## Epic 1 — Infraestrutura e Configuração
Responsável pela preparação do ambiente de desenvolvimento e organização inicial do projeto.

### Feature 1.1 — Configuração do Repositório
- [ ] Criar repositório no GitHub
- [x] Configurar licença MIT
- [x] Adicionar README inicial
- [x] Configurar `.gitignore`
- [x] Definir estrutura inicial das pastas

### Feature 1.2 — Ambiente Python
- [x] Criar ambiente virtual
- [x] Criar `requirements.txt`
- [x] Instalar dependências iniciais
- [x] Configurar variáveis de ambiente
- [x] Criar arquivo `.env.example`

### Feature 1.3 — Backend
- [x] Configurar FastAPI
- [x] Criar endpoint de teste (`/health`)
- [x] Configurar documentação automática (Swagger)
- [x] Estruturar rotas da aplicação

### Feature 1.4 — Frontend
- [x] Configurar Streamlit
- [x] Criar tela inicial
- [x] Validar comunicação com a API

> **✅ Definition of Done (Epic 1)**:
> - Ambiente virtual e dependências configurados.
> - API e interface Streamlit rodando e se comunicando com sucesso.
> - Projeto organizado de acordo com a arquitetura definida.

---

## Epic 2 — Ingestão de Dados
Responsável pela criação da base documental a partir da Wikipedia.

### Feature 2.1 — Coleta dos Dados
- [x] Estudar Wikipedia API
- [x] Selecionar páginas relevantes para o escopo da Seleção Brasileira nas Copas do Mundo
- [x] Implementar script de coleta automática
- [x] Salvar documentos brutos na pasta `data/raw/`

### Feature 2.2 — Limpeza dos Dados
- [x] Remover marcações HTML e ruídos
- [x] Remover seções e conteúdos irrelevantes
- [x] Corrigir problemas de codificação e caracteres especiais
- [x] Padronizar a formatação dos textos

### Feature 2.3 — Estruturação
- [x] Definir formato final para os documentos de conhecimento
- [x] Criar metadados úteis para filtragem futura
- [x] Salvar documentos processados na pasta `data/processed/`

> **✅ Definition of Done (Epic 2)**:
> - Base documental bruta e processada criada localmente.
> - Dados textuais limpos e padronizados, prontos para a etapa de indexação.

---

## Epic 3 — Chunking e Embeddings
Responsável pela preparação e armazenamento dos documentos na base vetorial.

### Feature 3.1 — Chunking
- [x] Estudar estratégias de chunking (ex: RecursiveCharacterTextSplitter)
- [x] Definir tamanho ideal de chunk e overlap apropriado
- [x] Implementar a divisão do texto em chunks estruturados

### Feature 3.2 — Embeddings
- [x] Escolher modelo de embeddings adequado para o idioma português
- [x] Implementar geração de embeddings para os chunks
- [x] Validar qualidade de conversão dos embeddings

### Feature 3.3 — Banco Vetorial
- [x] Configurar e instanciar o ChromaDB local
- [x] Criar coleção persistente para o projeto
- [x] Inserir os chunks de documentos com seus respectivos embeddings
- [x] Implementar e validar consultas básicas por similaridade cosseno

> **✅ Definition of Done (Epic 3)**:
> - Divisão do texto em chunks com overlap validado.
> - Embeddings criados e indexados com sucesso no banco ChromaDB local.

---

## Epic 4 — Pipeline RAG
Responsável pela inteligência de busca e orquestração do fluxo de dados com LangChain.

### Feature 4.1 — Retriever
- [x] Configurar a integração do ChromaDB com LangChain
- [x] Criar componente de recuperação (retriever)
- [x] Configurar número de documentos recuperados (Top-K) e limiar de similaridade
- [x] Testar a qualidade dos chunks retornados para perguntas de teste

### Feature 4.2 — Prompt
- [x] Criar System Prompt limitando o modelo a responder estritamente com base nos documentos
- [x] Definir instruções de comportamento do chatbot (ex: tom de voz, o que fazer quando não souber a resposta)
- [x] Configurar tratamento de exceção (evitar alucinação)

### Feature 4.3 — Cadeia RAG
- [x] Configurar a cadeia (chain) integrando o retriever e o template de prompt
- [x] Orquestrar o fluxo de dados do input do usuário à geração do prompt final

> **✅ Definition of Done (Epic 4)**:
> - Mecanismo de busca e formatação do prompt operacionais.
> - Comportamento do prompt validado para impedir alucinações.

---

## Epic 5 — Integração com o Google Gemini
Responsável pela conexão com a LLM do Google Gemini para resposta final.

### Feature 5.1 — API
- [x] Configurar a autenticação e carregamento da chave de API (`GEMINI_API_KEY`)
- [x] Instanciar o cliente e escolher a versão ideal do modelo (ex: Gemini Pro / Flash)

### Feature 5.2 — Geração de Respostas
- [x] Enviar o prompt enriquecido com contexto + pergunta à API
- [x] Tratar respostas vazias, truncadas ou falhas na API do Gemini
- [x] Otimizar os hiperparâmetros de geração (temperatura, top-p)

### Feature 5.3 — Integração
- [x] Conectar o Gemini na cadeia final do LangChain
- [x] Validar respostas completas para variados tipos de perguntas
- [x] Garantir que o modelo informa quando o contexto não possui a resposta

> **✅ Definition of Done (Epic 5)**:
> - Respostas geradas de forma dinâmica utilizando a API oficial do Gemini.
> - Pipeline RAG completo funcional a nível de código/Python.

---

## Epic 6 — Backend FastAPI
Responsável por expor a inteligência do RAG como uma API web utilizável.

### Feature 6.1 — Endpoints
- [x] Implementar endpoint `/health` para verificação de status
- [x] Implementar endpoint principal `/chat` para receber perguntas e retornar respostas com contexto
- [x] Implementar endpoint para status da base de conhecimento (opcional)

### Feature 6.2 — Modelos
- [x] Definir esquemas de entrada (Request Models) com Pydantic
- [x] Definir esquemas de saída (Response Models) contendo a resposta e fontes utilizadas
- [x] Adicionar validações de dados nas requisições

### Feature 6.3 — Tratamento de Erros
- [x] Criar middleware ou handlers para capturar exceções globais
- [x] Configurar logs estruturados do sistema
- [x] Padronizar mensagens de erro retornadas para o cliente

> **✅ Definition of Done (Epic 6)**:
> - API backend documentada nativamente via Swagger (`/docs`).
> - Endpoints respondendo adequadamente sob diferentes inputs.

---

## Epic 7 — Interface Streamlit
Responsável por criar a experiência visual de chat para o usuário.

### Feature 7.1 — Interface
- [ ] Projetar layout visual responsivo e amigável (cabeçalho, barra lateral)
- [ ] Adicionar área de entrada de texto e controles básicos

### Feature 7.2 — Chat
- [ ] Implementar histórico de conversas em memória (session state)
- [ ] Exibir mensagens com estilo diferenciado de Usuário vs. Assistente
- [ ] Adicionar indicadores visuais de carregamento enquanto aguarda a API

### Feature 7.3 — Integração
- [ ] Criar cliente HTTP para consumir os endpoints do backend FastAPI
- [ ] Tratar falhas de conexão com o backend graciosamente na interface do usuário
- [ ] Exibir as fontes dos documentos utilizados na resposta

> **✅ Definition of Done (Epic 7)**:
> - Interface web do chat funcional e estilizada.
> - Comunicação dinâmica e estável entre frontend Streamlit e backend FastAPI.

---

## Epic 8 — Testes e Ajustes Finais
Responsável por certificar a estabilidade e qualidade geral do projeto.

### Feature 8.1 — Testes Funcionais
- [ ] Escrever testes unitários e de integração para os endpoints da API (usando pytest)
- [ ] Escrever testes básicos para o pipeline de dados
- [ ] Testar a interface Streamlit simulando interações

### Feature 8.2 — Testes de Qualidade
- [ ] Avaliar a precisão da recuperação do retriever
- [ ] Analisar a latência de ponta a ponta (tempo de resposta do chat)
- [ ] Avaliar o comportamento de proteção contra alucinações (perguntas fora do escopo)

### Feature 8.3 — Ajustes e Refatoração
- [ ] Corrigir eventuais bugs mapeados
- [ ] Refatorar trechos de código visando legibilidade e eficiência
- [ ] Limpar logs de depuração desnecessários

> **✅ Definition of Done (Epic 8)**:
> - Cobertura de testes essenciais estabelecida e passando.
> - Código limpo, estável e livre de bugs críticos mapeados.

---

# 📌 Organização do Desenvolvimento

Para evitar retrabalho, o desenvolvimento seguirá estritamente a seguinte ordem de execução:
1. **Infraestrutura e Configuração** (Epic 1)
2. **Coleta de Dados** (Epic 2)
3. **Processamento e Chunking** (Epic 3)
4. **Banco Vetorial** (Epic 3)
5. **Retriever e Prompt** (Epic 4)
6. **Orquestração LangChain e Gemini** (Epic 5)
7. **Construção da API Backend** (Epic 6)
8. **Desenvolvimento do Frontend** (Epic 7)
9. **Testes Unitários e de Integração** (Epic 8)
10. **Refinamento e Publicação** (Epic 8)

---

# 🎯 Critérios para Conclusão do MVP

O projeto será considerado concluído e pronto para entrega quando:
1. O backend em **FastAPI** estiver rodando e respondendo com Swagger disponível.
2. A interface **Streamlit** estiver integrada e apresentando o chat interativo.
3. O banco **ChromaDB** estiver populado com dados de conhecimento extraídos da Wikipedia.
4. O pipeline **RAG** estiver recuperando apenas chunks relevantes de conhecimento.
5. O **Google Gemini** estiver formulando respostas de qualidade baseadas no contexto recebido.
6. A interface for capaz de exibir as fontes (links ou seções da wiki) que serviram de contexto.
7. Existir cobertura de testes básicos de integração passando via `pytest`.
8. A documentação estiver completa, organizada e o projeto publicado no GitHub.

---

## 🔗 Veja Também

* 🏗️ **[Arquitetura Detalhada](architecture.md)**
* ⚙️ **[Desenvolvimento e Convenções](development.md)**
* 🏠 **[Voltar ao README](../README.md)**
