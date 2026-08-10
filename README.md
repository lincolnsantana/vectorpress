# AI Pulse

AI Pulse é uma API para monitorar notícias sobre Inteligência Artificial e, nas próximas sprints, apoiar consultas inteligentes com RAG.

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
- fontes iniciais: OpenAI Blog, Anthropic Blog, TechCrunch AI, Google AI Blog, DeepMind Blog, Microsoft AI Blog, MIT Tech Review AI, The Verge AI, Hugging Face Blog, Meta AI Blog, arXiv cs.AI, VentureBeat AI, Wired AI e 404 Media AI;
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

## Estrutura atual

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── rss/
│   │   ├── schemas/
│   │   └── tests/
│   ├── requirements.txt
│   └── requirements-dev.txt
├── docker/
├── docker-compose.yml
└── README.md
```

## Próximos passos

As próximas sprints vão adicionar base vetorial com RAG, Telegram, frontend e deploy.
