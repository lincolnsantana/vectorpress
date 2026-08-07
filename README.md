# AI Pulse

AI Pulse é uma API para monitorar notícias sobre Inteligência Artificial e, nas próximas sprints, apoiar consultas inteligentes com RAG.

## Sprint 01 - Fundação

Nesta etapa o projeto entrega:

- backend FastAPI inicial;
- Docker Compose com PostgreSQL 16 e pgvector;
- configuração de variáveis de ambiente;
- endpoint `GET /`;
- endpoint `GET /health`.

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
2. Instale as dependências do backend.
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

## Endpoints

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

## Estrutura atual

```text
.
├── backend/
├── docker/
├── docker-compose.yml
└── README.md
```

## Próximos passos

As próximas sprints vão adicionar ingestão RSS, base vetorial, RAG, Telegram, frontend e deploy.
