# 💾 Banco Vetorial, Chunking e Estratégia de Fallback

Este documento detalha o design, a implementação e as decisões arquiteturais da etapa de **Chunking e Banco Vetorial (Epic 3)** do projeto **BrasilnaCopaAI**.

---

## 🏗️ O que foi feito

Nesta etapa, estruturamos a base de conhecimento do chatbot RAG. O conteúdo textual bruto coletado da Wikipédia foi fatiado em segmentos menores (chunks), convertido em vetores de alta dimensão (embeddings) utilizando a API do Google Gemini e indexado localmente em um banco vetorial persistente ChromaDB.

---

## 🛠️ Como foi feito

A implementação foi dividida em três frentes principais dentro do pacote `app/vectorstore/`:

### 1. Fatiamento Inteligente (`chunker.py`)
Implementado através da classe `DocumentChunker` utilizando o `RecursiveCharacterTextSplitter` do LangChain.
* **Tamanho do Chunk**: 1000 caracteres (limite recomendado para manter a coesão semântica e contextual).
* **Sobreposição (Overlap)**: 200 caracteres (garante que informações nas divisões não se percam).
* **Propagação de Metadados**: Cada chunk gerado retém todas as propriedades originais do artigo (URL, título original, número de palavras, etc.) e recebe metadados adicionais de controle, como `chunk_index` e `total_chunks`.

### 2. Modelo de Embeddings e Rotação de Chaves (`database.py`)
* **Modelos Suportados**:
  * **Remoto (Gemini API)**: Usa `models/gemini-embedding-2` (3072 dimensões) com fallback automático para `models/gemini-embedding-001`.
  * **Local (ONNX Runtime)**: Usa o modelo **`paraphrase-multilingual-MiniLM-L12-v2`** em formato ONNX (384 dimensões), ativado por `USE_LOCAL_EMBEDDINGS=true` no arquivo `.env`. Ideal para testes rápidos, execuções offline e contorno de quotas de API.
* **Gerenciador de Chaves (`GeminiAPIKeyManager`)**: Permite o carregamento de múltiplas chaves de API a partir da variável de ambiente `GEMINI_API_KEYS` (lista separada por vírgula) ou fallback automático para a chave tradicional `GEMINI_API_KEY`.
* **Resiliência e Rotação**: Criamos a classe wrapper `FallbackGeminiEmbeddings` que encapsula o cliente de embeddings e intercepta erros de cota ou limites de taxa (`429 RESOURCE_EXHAUSTED`). Caso uma chave falhe, ela é rotacionada automaticamente para a próxima chave configurada na lista.
* **Retentativas locais com Backoff**: Para suportar falhas temporárias de rede (ex: `WinError 10060`), implementamos uma lógica de retentativas locais (até 3 tentativas) com tempo de espera exponencial crescente (2s, 4s, 8s) antes de desistir ou rotacionar a chave.

### 3. Script de Indexação Resiliente (`populate.py`)
Criamos um script utilitário CLI para processar a base de dados de `data/processed/` e indexar tudo no banco vetorial.
* **Modo de Recuperação/Resume**: O script gera IDs determinísticos para cada chunk (`f"{source_title}_{chunk_index}"`) e verifica os metadados já presentes no ChromaDB antes de indexar. Ele envia apenas os chunks ausentes, permitindo retomar de onde parou caso ocorra alguma queda no processo.
* **Carga Fracionada**: Os chunks são enviados ao banco em lotes de 20 chunks com 4 segundos de intervalo entre envios (quando rodando via API Gemini) para respeitar o limite de requisições por minuto (RPM). Quando `USE_LOCAL_EMBEDDINGS` está ativado, o script pula este intervalo de espera, rodando a indexação em velocidade máxima local.
* **Limpeza Explicitada**: Use a flag `--clear` para remover todos os dados existentes no banco vetorial antes de iniciar uma nova carga:
  ```bash
  python -m app.vectorstore.populate --clear
  ```

### 4. Monitoramento e Endpoint de Saúde (`main.py`)
* Atualizamos o endpoint `/health` da API FastAPI para verificar a conectividade com o ChromaDB em tempo real, exibindo também a quantidade de chunks indexados (ex: `"database": "connected (502 chunks)"`).

---

## 🧠 Por que foi feito assim

1. **Escolha do Chunker Recursivo**: Dividir o texto usando separadores lógicos (parágrafos, depois frases, depois palavras) é mais eficiente que cortes secos por caractere fixo, pois preserva o contexto natural da leitura humana.
2. **Uso de Lotes Menores (Batching)**: Tentar enviar 502 chunks em uma única chamada de embeddings gerava erros de timeout na rede e estouro de cota da API. Reduzir para lotes de 10 chunks com intervalo de repouso é a forma ideal de respeitar os limites da API gratuita.
3. **Resiliência a N Chaves e Falhas**: Ambientes de produção e ferramentas que dependem de limites estritos da API necessitam de redundância. O gerenciador de chaves previne que o pipeline pare de funcionar por falta de limite de cota de uma única chave. As retentativas locais curam falhas rápidas de conexão sem a necessidade de rotacionar credenciais desnecessariamente.

---

## 🚀 Como testar e executar

### Executar os testes automatizados
```bash
# Rodar todos os testes unitários e de integração
pytest
```

### Executar a carga no banco
```bash
python -m app.vectorstore.populate
```
A base vetorial será criada e persistida no caminho definido por `CHROMA_DB_PATH` no arquivo `.env` (ex: `data/db/`).
