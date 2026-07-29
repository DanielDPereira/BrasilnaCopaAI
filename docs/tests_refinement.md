# 🧪 Testes e Refinamentos Gerais

Este documento detalha o design, a implementação e as decisões da etapa de **Testes e Ajustes Finais (Epic 8)** do projeto **BrasilnaCopaAI**.

---

## 🏗️ O que foi feito

Nesta etapa, focamos na estabilidade, cobertura de testes e qualidade geral do projeto. Desenvolvemos novos testes funcionais de interface do usuário, criamos uma bateria de testes de métricas de qualidade (precisão, latência e segurança contra alucinações do RAG) e resolvemos todos os avisos de depreciação do Python detectados no console de execução.

---

## 🛠️ Como foi feito

As implementações foram estruturadas nas seguintes frentes:

### 1. Testes de Interface Streamlit (`tests/test_gui.py`)
* Usamos a biblioteca de testes nativa do Streamlit (`streamlit.testing.v1.AppTest`) para simular a compilação e a renderização do frontend sem abrir o navegador.
* **Isolamento de API**: Como o frontend depende do backend para monitoramento de saúde (`/health`), mockamos a chamada do módulo `requests.get` para retornar uma resposta fictícia instantânea. Isso tornou o teste da UI determinístico, rápido e livre de conexões externas.
* O teste valida o estado inicial da página, a existência do controle de Top-K no sidebar e o botão para limpar a conversa.

### 2. Testes de Métricas de Qualidade do RAG (`tests/test_quality.py`)
* **Precisão do Retriever**: Valida se a busca semântica pelo termo "Pelé" traz trechos relevantes com conteúdo associado a "Pelé", "Copa", "Brasil", etc.
* **Medição de Latência**:
  * Mede o tempo de busca local no ChromaDB (garantindo que seja `< 1.5` segundo). Para isolar a latência da busca vetorial local dos atrasos da rede, o LLM de expansão de consultas é mockado no teste de latência.
  * Mede e exibe a latência da chamada externa à API do Gemini. Para evitar que variações de conexão com os servidores do Google causem falhas intermitentes no CI, o tempo da LLM é impresso no console sem gerar falhas rígidas (evitando testes flaky).
* **Proteção contra Alucinações (Perguntas Fora do Escopo)**: Testa o envio de perguntas não correlacionadas com a Seleção nas Copas (ex: *"Como cozinhar uma lasanha de berinjela?"*). O teste valida se o pipeline ativa a resposta literal de fallback especificada nas diretrizes do prompt.

### 3. Refatoração e Correção de Avisos
* Identificamos avisos de depreciação causados pelo uso do método `datetime.utcnow()`.
* Substituímos o uso do método legado por `datetime.now(timezone.utc)` nos seguintes módulos de processamento de dados e endpoints:
  * `app/main.py`
  * `app/ingestion/collector.py`
  * `app/ingestion/processor.py`

---

## 🚀 Como executar os testes

Você pode rodar toda a suíte de testes (agora com **29 testes ativos**) utilizando:

```bash
.\.venv\Scripts\python.exe -m pytest -v -s
```
O parâmetro `-s` permite visualizar os tempos de latência e as saídas das métricas impressas no terminal.
