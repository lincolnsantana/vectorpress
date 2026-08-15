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
- purga automática: o sync remove notícias de fontes que saíram de `sources.py` (ex.: arXiv removido);
- preload do modelo de embeddings na inicialização da API (reduz o tempo de resposta do `/ask`);
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

Durante o `/ask`, o bot exibe o indicador de digitação ("Digitando...") enquanto a resposta é gerada.

### Comandos

| Comando         | Descrição                                    |
|-----------------|----------------------------------------------|
| `/today`        | Últimas 5 manchetes com links                |
| `/list [página]`| Lista paginada de notícias recentes (10 por página) |
| `/ask <pergunta>` | Consulta RAG sobre as notícias armazenadas  |

## Sprint 05 - Automação com n8n

Nesta etapa o projeto entrega:

- workflow n8n para sincronização automática das notícias (a cada 6 horas);
- o workflow apenas dispara o endpoint `POST /news/sync` — a leitura dos feeds RSS, deduplicação e indexação vetorial continuam na API;
- notificações no Telegram para o admin:
  - início da sincronização;
  - sucesso, com a quantidade de notícias novas, duplicadas, erros e fontes;
  - falha, com o corpo da resposta para diagnóstico;
- workflow exportado e versionado em `n8n/workflows/rss-sync.json`.

### Estrutura do workflow

```
Schedule Trigger (a cada 6 horas)
↓
Telegram: "Atualizando notícias com o sync/news..."
↓
HTTP Request: POST /news/sync
↓
IF: resposta contém "created"?
├── true  → Telegram: "Base de notícias atualizada" (com contagens)
└── false → Telegram: "Falha ao atualizar as notícias" (com resposta)
```

### Como importar o workflow

1. Suba o n8n:

   ```bash
   docker run -it --rm -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
   ```

2. Acesse `http://localhost:5678`.
3. Clique em **Workflows** → **Import** e selecione `n8n/workflows/rss-sync.json`.
4. Crie a credencial **Telegram** (token do bot) e associe-a aos nós do tipo Telegram.
5. Substitua os valores placeholder antes de ativar:
   - URL do nó **HTTP Request**: `https://SEU-SUB.ngrok-free.app/news/sync` → sua URL pública real;
   - `chatId` dos nós Telegram → o chat ID do admin (obtido via `getUpdates`);
6. Use **Test workflow** para validar e, em seguida, ative o workflow com o toggle **Active**.

> Dica: se a URL pública for do ngrok e aparecer a página de aviso do navegador na resposta do nó HTTP Request, adicione o header `ngrok-skip-browser-warning: true`.

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
- `RAG_MAX_AGE_DAYS`
- `NEWS_RETENTION_DAYS`
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

Dispara a sincronização das notícias das fontes RSS.

- URLs já armazenadas não são duplicadas;
- quando um artigo já existente ainda não tem `image_url`, o sync tenta preenchê-lo (backfill);
- quando o feed não fornece imagem, a API busca a tag `og:image` da página do artigo.

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
      "image_url": "https://…",
      "summary": "…",
      "published_at": "2025-01-01T10:00:00Z",
      "created_at": "2025-01-01T10:00:00Z"
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

> `image_url` pode ser nulo quando nem o feed nem a página do artigo fornecem uma imagem (o frontend exibe um placeholder). `summary` pode ser vazio quando o feed não fornece conteúdo.

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
├── n8n/
│   └── workflows/
│       └── rss-sync.json
└── README.md
```

## Próximos passos

As próximas sprints vão adicionar o frontend e o deploy.
