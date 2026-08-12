# AI Pulse

AI Pulse é uma API para monitorar notícias sobre Inteligência Artificial e responder perguntas sobre elas usando Retrieval-Augmented Generation (RAG) com base vetorial no PostgreSQL (pgvector).

## Sprint 01 - Fundação

Nesta etapa o projeto entrega:

- backend FastAPI inicial;
- Docker Compose com PostgreSQL 16 e pgvector;
- configuração de variáveis de ambiente;
- endpoint `GET /`;
- endpoint `GET /health`.

## Sprint 02 - Ingestão de Notícias

Nesta etapa o projeto entrega:

- ingestão de notícias via RSS (feedparser + httpx);
- fontes iniciais: OpenAI Blog, Anthropic Blog, TechCrunch AI, Google AI Blog, DeepMind Blog, Microsoft AI Blog, MIT Tech Review AI, The Verge AI, Hugging Face Blog, Meta AI Blog, VentureBeat AI, Wired AI e 404 Media AI;
- prevenção de duplicatas por URL;
- persistência das notícias no PostgreSQL;
- endpoint `POST /news/sync`;
- endpoint `GET /news`;
- endpoint `GET /news/{id}`.

### Sincronização de notícias

Para buscar e salvar as notícias das fontes RSS:

```bash
curl -X POST http://localhost:8000/news/sync
```

Resposta com contagens:

```json
{"sources":14,"articles":42,"created":40,"skipped":2,"errors":0}
```

### Listagem paginada

```bash
curl "http://localhost:8000/news?limit=10&offset=0"
```

### Notícia por ID

```bash
curl http://localhost:8000/news/{id}
```

## Sprint 03 - Base Vetorial e RAG

Nesta etapa o projeto entrega:

- fragmentação de conteúdo em chunks (LangChain RecursiveCharacterTextSplitter);
- geração de embeddings (sentence-transformers local ou OpenAI API);
- armazenamento vetorial no PostgreSQL (pgvector, tabela `embeddings`);
- indexação incremental: notícias novas são fragmentadas e embedadas durante o `POST /news/sync`;
- busca vetorial por similaridade cosseno (top 5 chunks);
- filtro de recência: o `/ask` considera apenas notícias publicadas na janela configurável `RAG_MAX_AGE_DAYS` (padrão: 3 dias);
- geração de respostas via LLM (Groq API) usando apenas o contexto recuperado;
- endpoint `POST /ask`.

### Consulta RAG

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que aconteceu com IA recentemente?"}'
```

Resposta com a resposta e as fontes citadas:

```json
{
  "answer": "…",
  "sources": [
    {"title": "…", "url": "https://…", "source": "OpenAI Blog"}
  ]
}
```

### Pipeline RAG

```
Pergunta
↓
Embedding da pergunta
↓
Busca vetorial (pgvector, top 5 chunks)
↓
Contexto
↓
LLM (Groq)
↓
Resposta + fontes
```

Quando não há contexto suficiente, a resposta é: *"Não encontrei informações suficientes para responder esta pergunta."*

### Configuração de IA

- `EMBEDDING_PROVIDER=local` usa sentence-transformers localmente (modelo `all-MiniLM-L6-v2`, 384 dimensões). `EMBEDDING_PROVIDER=openai` usa a API da OpenAI.
- `LLM_PROVIDER=groq` usa a Groq API (requer `GROQ_API_KEY`).
- `RAG_MAX_AGE_DAYS` define quantos dias de recência o `/ask` considera (padrão `3`). Notícias mais antigas que essa janela são ignoradas na busca vetorial.

## Sprint 04 - Bot Telegram

Nesta etapa o projeto entrega:

- bot do Telegram integrado à API via webhook (`POST /telegram/webhook`);
- comando `/today` — últimas 5 manchetes com links;
- comando `/list` — lista paginada de notícias recentes;
- comando `/ask <pergunta>` — consulta RAG (`POST /ask`) com fontes;
- tratamento de erros nos comandos (falhas graciosas).

### Configuração do bot

1. Crie um bot com o [@BotFather](https://t.me/BotFather) e copie o token.
2. Adicione no `.env`:
   - `TELEGRAM_TOKEN` — token do bot;
   - `TELEGRAM_WEBHOOK_URL` — URL pública que o Telegram chamará (ex: `https://seudominio.com/telegram/webhook`).
3. Suba a aplicação e registre o webhook:

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=<TELEGRAM_WEBHOOK_URL>"
```

Se `TELEGRAM_TOKEN` não estiver definido, a API sobe normalmente e o webhook responde `503` até o bot ser configurado.

### Comandos

| Comando         | Descrição                                    |
|-----------------|----------------------------------------------|
| `/today`        | Últimas 5 manchetes com links                |
| `/list [página]`| Lista paginada de notícias recentes (10 por página) |
| `/ask <pergunta>` | Consulta RAG sobre as notícias armazenadas  |

## Requisitos

- Docker e Docker Compose;
- Python 3.12+ para execução local;
- PostgreSQL rodando via Docker Compose.

## Variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e ajuste os valores se necessário.

Variáveis disponíveis:

- `APP_NAME`
- `APP_ENV`
- `LOG_LEVEL`
- `DATABASE_URL`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_PORT`
- `EMBEDDING_PROVIDER`
- `EMBEDDING_MODEL`
- `OPENAI_API_KEY`
- `LLM_PROVIDER`
- `LLM_MODEL`
- `GROQ_API_KEY`
- `TELEGRAM_TOKEN`
- `TELEGRAM_WEBHOOK_URL`

## Como executar com Docker

```bash
docker compose up --build
```

Serviços expostos:

- API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

## Como executar localmente

1. Crie e ative um ambiente virtual.
2. Instale as dependências do backend (use `requirements-dev.txt` para incluir as dependências de teste).
3. Exporte as variáveis de ambiente.
4. Inicie a API com Uvicorn.

Exemplo:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testes

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

## Endpoints

| Método | Endpoint    | Descrição                            |
|--------|-------------|--------------------------------------|
| GET    | `/`         | Mensagem inicial da API              |
| GET    | `/health`   | Health check (DB + pgvector)         |
| POST   | `/news/sync`| Sincronização manual das notícias    |
| GET    | `/news`     | Lista paginada de notícias           |
| GET    | `/news/{id}`| Detalhe de uma notícia               |
| POST   | `/ask`      | Consulta RAG sobre as notícias       |
| POST   | `/telegram/webhook` | Recebe atualizações do bot Telegram |

### `GET /`

Retorna a mensagem inicial da API.

Exemplo de resposta:

```json
{"message":"AI Pulse API"}
```

### `GET /health`

Verifica a API e a disponibilidade do PostgreSQL com pgvector.

Exemplo de resposta:

```json
{"status":"ok","database":"ok","pgvector":"ok"}
```

### `POST /news/sync`

Dispara a sincronização das notícias das fontes RSS. Idempotente: URLs já armazenadas são ignoradas.

### `GET /news`

Lista paginada de notícias.

Parâmetros de query:

- `limit` (padrão `20`, máximo `100`);
- `offset` (padrão `0`).

Exemplo de resposta:

```json
{
  "items": [
    {
      "id": "…",
      "title": "…",
      "url": "https://…",
      "source": "OpenAI Blog",
      "author": null,
      "published_at": "2025-01-01T10:00:00Z",
      "created_at": "2025-01-01T10:00:00Z"
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

### `GET /news/{id}`

Retorna o detalhe completo de uma notícia, incluindo o `content`. Retorna `404` se o ID não existir.

### `POST /ask`

Recebe uma pergunta e responde com base apenas nas notícias armazenadas (RAG).

Corpo:

```json
{"question": "O que aconteceu com IA recentemente?"}
```

Resposta com `answer` e `sources` (URLs das notícias utilizadas como contexto).

### `POST /telegram/webhook`

Recebe as atualizações do bot Telegram e processa os comandos `/today`, `/list` e `/ask`. Responde `200` quando o bot está configurado (`TELEGRAM_TOKEN` válido) e `503` caso contrário.

## Estrutura atual

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── rag/
│   │   ├── rss/
│   │   ├── schemas/
│   │   ├── telegram/
│   │   └── tests/
│   ├── requirements.txt
│   └── requirements-dev.txt
├── docker/
├── docker-compose.yml
└── README.md
```

## Próximos passos

As próximas sprints vão adicionar automação com n8n, frontend e deploy.
