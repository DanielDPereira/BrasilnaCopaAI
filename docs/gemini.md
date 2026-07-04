# ♊ Integração com o Google Gemini

Este documento detalha o design, a implementação e as decisões da etapa de **Integração com o Google Gemini (Epic 5)** do projeto **BrasilnaCopaAI**.

---

## 🏗️ O que foi feito

Nesta etapa, integramos o modelo de linguagem (LLM) do Google Gemini ao pipeline RAG. O pipeline agora executa a recuperação semântica, monta o prompt com as diretrizes e contexto do banco vetorial, envia a chamada para a API do Gemini e retorna a resposta de texto final do chat de forma totalmente resiliente.

---

## 🛠️ Como foi feito

A estrutura de integração foi implementada no pacote `app/rag/` nas seguintes partes:

### 1. Modelo de Linguagem Resiliente (`llm.py`)
* Classe `FallbackChatGemini` que herda de `Runnable` do LangChain e atua como um wrapper do modelo `ChatGoogleGenerativeAI`.
* **Hiperparâmetros configurados**:
  * Modelo padrão: `gemini-2.5-flash` (selecionado devido ao excelente tempo de resposta e cotas de uso do plano gratuito).
  * `temperature = 0.0` (para evitar alucinações e respostas inventadas).
  * `top_p = 0.95`.
* **Rotação e Fallback**: Caso uma chamada falhe por estouro de cota de requisições por minuto ou limite diário da API (`RESOURCE_EXHAUSTED` / `429`), o wrapper automaticamente rotaciona a chave de API (usando `GeminiAPIKeyManager`) e re-inicializa o modelo sem derrubar a cadeia.
* **Retentativas de Rede**: Em caso de falhas de rede temporárias (timeouts, erros de conexão), são feitas até 3 retentativas locais na chave atual usando espaçamento (backoff) de tempo exponencial.

### 2. Pipeline Completo (`pipeline.py`)
* Atualizamos a classe `RAGPipeline` para unificar a recuperação semântica e a chamada de linguagem através de uma cadeia final do LangChain:
  ```python
  self.chain = self.prompt_chain | self.llm | StrOutputParser()
  ```
* Adicionamos o método `ask(query) -> str` que executa a cadeia de dados completa e retorna diretamente a resposta textual gerada pelo modelo.
* Preservamos o método `generate_prompt(query)` mapeando apenas para `self.prompt_chain` para garantir retrocompatibilidade.

---

## 🧠 Por que foi feito assim

1. **Seleção do Modelo `gemini-2.5-flash`**: Identificamos que o modelo `gemini-2.5-flash` está disponível e possui cotas de execução estáveis no ambiente de sandbox, garantindo a execução sem erros de "model not found".
2. **LCEL de Ponta a Ponta**: A cadeia RAG foi estendida usando a sintaxe declarativa padrão do LangChain, o que permite o fluxo de dados unificado de strings para mensagens de chat, e finalmente para o parseador de saída (`StrOutputParser`).

---

## 🚀 Como testar e executar

### Executar os testes automatizados
```bash
pytest tests/test_llm.py tests/test_rag_pipeline.py
```
* **`test_llm.py`**: Valida a lógica de rotação de chaves e retentativa em caso de erros e limites de quota.
* **`test_rag_pipeline.py`**: Contém testes mockados e de integração real que chamam o modelo do Gemini ativamente usando a chave de API em `.env`.
