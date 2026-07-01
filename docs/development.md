# ⚙️ Guia de Desenvolvimento, Testes e Convenções

Este documento serve como guia de boas práticas, padrões de desenvolvimento, estratégia de versionamento e execução de testes para o projeto **BrasilnaCopaAI**.

---

# 💡 Motivação do Projeto

Grande parte das aplicações atuais de IA utiliza **Retrieval-Augmented Generation (RAG)** para complementar modelos de linguagem com conhecimento específico de um determinado domínio.

O **BrasilnaCopaAI** foi escolhido como tema por possuir um escopo bem definido, permitindo concentrar o desenvolvimento na arquitetura da solução em vez da complexidade do domínio. Dessa forma, o projeto serve como laboratório para estudar e aplicar conceitos modernos de IA, mantendo um problema suficientemente pequeno para ser desenvolvido individualmente.

---

# 🎓 Objetivos de Aprendizagem

Este projeto busca consolidar conhecimentos práticos em:
- **Linguagem**: Python (3.12+)
- **APIs REST**: FastAPI (Uvicorn, Pydantic)
- **Interface Visual**: Streamlit
- **Orquestração de IA**: LangChain
- **Modelos Generativos**: Google Gemini API
- **Banco de Dados Vetorial**: ChromaDB
- **Engenharia de RAG**: Embeddings, Busca Vetorial e Estratégias de Chunking
- **Arquitetura de Software**: Separação clara de responsabilidades (Backend vs. Frontend) e organização profissional
- **Versionamento**: Git e GitHub

---

# 🌳 Estratégia de Branches (Git Flow Simplificado)

O projeto utilizará um fluxo simplificado de branches para manter o código organizado e estável.

* **`main`**: Contém apenas versões estáveis de produção. Nada é desenvolvido diretamente nesta branch.
* **`develop`**: Branch principal de integração. É a partir dela que as branches de feature surgem e para onde elas retornam após validação.
* **`feature/*`**: Utilizada para desenvolvimento de novas funcionalidades. Exemplos:
  - `feature/fastapi`
  - `feature/chromadb`
  - `feature/rag`
  - `feature/streamlit`
  - `feature/gemini`

---

# 💬 Convenção de Commits (Conventional Commits)

Adotamos a especificação de **Conventional Commits** para manter o histórico de alterações limpo e legível. Os commits devem seguir a seguinte estrutura:

```text
<tipo>: <descrição curta em português>
```

### Tipos recomendados:
* **`feat`**: Introdução de uma nova funcionalidade (ex: `feat: adiciona integração com Gemini`).
* **`fix`**: Correção de algum bug ou problema (ex: `fix: corrige recuperação vetorial`).
* **`docs`**: Alterações na documentação (ex: `docs: atualiza guia de desenvolvimento`).
* **`refactor`**: Modificações no código que não alteram o comportamento final (ex: `refactor: reorganiza pipeline RAG`).
* **`style`**: Mudanças de estilo que não afetam a lógica (ex: `style: melhora formatação do código`).
* **`test`**: Criação ou alteração de testes (ex: `test: adiciona testes da API`).
* **`chore`**: Tarefas de manutenção do repositório ou dependências (ex: `chore: atualiza requirements.txt`).

---

# 📚 Convenções de Código

Durante o desenvolvimento do BrasilnaCopaAI, as seguintes regras de design e implementação devem ser seguidas:
1. **Separação de Responsabilidades**: A interface (Streamlit) não deve conter nenhuma regra de negócio ou lógica RAG. Ela atua apenas como camada de visualização e faz requisições HTTP para a API.
2. **Código Modular**: Cada componente (ingestão, vetorização, RAG, rotas) deve residir em seu respectivo módulo.
3. **Type Hints**: Utilizar anotações de tipo em todas as assinaturas de funções e métodos.
4. **Pydantic**: Validar entradas (request) e saídas (response) na API FastAPI utilizando modelos Pydantic.
5. **Tratamento de Exceções**: Todo serviço externo (chamadas HTTP, Wikipedia, Gemini, ChromaDB) deve possuir tratamento de erro robusto.
6. **Segurança**: Nunca salvar chaves de API (`.env`) no repositório. Utilizar variáveis de ambiente.

---

# 🧪 Execução de Testes

Os testes são centralizados na pasta `tests/` e utilizam o framework **pytest**.

### Como executar todos os testes:
```bash
pytest
```

### Escopo de validação dos testes:
* **API**: Garantir que as rotas HTTP (como `/health` e `/chat`) respondam nos formatos corretos com validações do Pydantic.
* **Pipeline RAG**: Validar se a busca vetorial retorna chunks adequados e se as fontes recuperadas estão corretas.
* **Integração com Gemini**: Testar a autenticação na API do Google Gemini e o retorno de respostas.
* **Interface**: Testar a estabilidade do fluxo de chat no Streamlit.

---

## 🔗 Veja Também

* 🏗️ **[Arquitetura Detalhada](architecture.md)**
* 📋 **[Roadmap e Backlog](backlog.md)**
* 🏠 **[Voltar ao README](../README.md)**
