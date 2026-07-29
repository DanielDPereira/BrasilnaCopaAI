# 🔍 Pipeline de Recuperação Semântica (RAG)

Este documento detalha o design, a implementação e as decisões da etapa de **Pipeline RAG (Epic 4)** do projeto **BrasilnaCopaAI**.

---

## 🏗️ O que foi feito

Nesta etapa, implementamos a orquestração do fluxo RAG usando **LangChain**. O pipeline recebe a pergunta do usuário, busca de forma inteligente os fragmentos textuais (chunks) mais relevantes no ChromaDB, formata os documentos recuperados como contexto estruturado e injeta tudo em um template de prompt controlado para o modelo de linguagem (LLM).

---

## 🛠️ Como foi feito

A lógica do pipeline foi estruturada sob o pacote `app/rag/` nas seguintes partes:

### 1. Componente de Recuperação Multi-Query (`retriever.py`)
* Classe `MultiQueryRAGRetriever` que estende `BaseRetriever` do LangChain e implementa a técnica de **Query Expansion** (expansão de consultas).
* **Expansão Dinâmica**: Diante de uma pergunta do usuário, o retriever invoca o LLM para gerar exatamente 3 termos de busca ou perguntas curtas alternativas em português que cobrem tópicos relacionados.
* **Busca e Desduplicação**: É feita a busca semântica no ChromaDB para a pergunta original e para cada uma das 3 variações geradas. Todos os documentos recuperados são agregados, desduplicados e o resultado final é retornado, elevando expressivamente o recall para perguntas amplas.
* **Resiliência**: Possui fallback seguro para usar apenas a query original em caso de falha ou quota excedida no LLM durante a etapa de expansão.

### 2. Instruções do Sistema e Engenharia de Prompt (`prompts.py`)
* **System Prompt Restritivo**: Definimos diretrizes rígidas instruindo o assistente a responder *única e exclusivamente* com base no contexto fornecido.
* **Instrução de Fallback Seguro**: Caso a informação não esteja no contexto recuperado, o modelo é obrigado a responder de forma literal: *"Não possuo essa informação em minha base de dados sobre a Seleção Brasileira nas Copas do Mundo."* (evitando alucinação).
* **Formatador de Prompt**: Função `get_prompt_template()` que cria o `ChatPromptTemplate` contendo a mensagem do sistema e do usuário.

### 3. Orquestração da Cadeia LCEL (`pipeline.py`)
* Implementamos a classe `RAGPipeline` que une o retriever, o formatador de documentos e o prompt template em uma cadeia declarativa usando LCEL (LangChain Expression Language).
* **Estrutura da Cadeia**:
  ```python
  chain = (
      {
          "context": retriever | format_docs,
          "question": RunnablePassthrough()
      }
      | prompt_template
  )
  ```
* O resultado da execução do pipeline é um `ChatPromptValue` pronto com o contexto estruturado e a pergunta, servindo de elo perfeito para a entrada do modelo de linguagem (Gemini) no Epic 5.

---

## 🧠 Por que foi feito assim

1. **Separação de Responsabilidades**: O pipeline RAG manipula puramente a busca de contexto e formatação do prompt. Ele não se preocupa com rotas da API ou componentes de UI, permitindo testes isolados de qualidade de busca.
2. **Formatação Estruturada do Contexto**: Cada documento injetado é demarcado com seu título e link de origem (URL da Wikipedia). Isso prepara o terreno para que, futuramente, a interface possa citar as fontes exatas utilizadas para responder.
3. **Sintaxe LCEL**: A adoção de LCEL simplifica a legibilidade da cadeia de dados e facilita a extensão do pipeline (por exemplo, adicionar histórico de conversa ou encadear a LLM Gemini no próximo Epic).

---

## 🚀 Como testar e executar

### Executar os testes automatizados
```bash
pytest tests/test_retriever.py tests/test_prompts.py tests/test_rag_pipeline.py
```
* **`test_retriever.py`**: Garante o correto mapeamento do retriever com o banco vetorial.
* **`test_prompts.py`**: Valida a correta injeção de contexto e formatação de variáveis no template.
* **`test_rag_pipeline.py`**: Testa o fluxo da cadeia LCEL usando um retriever simulado (`RunnableLambda`) e realiza uma busca de integração contra o banco ChromaDB local.
