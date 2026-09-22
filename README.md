# Vectorpress

Vectorpress é uma API para monitorar notícias sobre Inteligência Artificial e responder perguntas sobre elas usando Retrieval-Augmented Generation (RAG) com base vetorial no PostgreSQL (pgvector).

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-vector%20search-5B5BD6)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-RAG-1C3C3C)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=111111)
![Vite](https://img.shields.io/badge/Vite-6-646CFF?logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-4-06B6D4?logo=tailwindcss&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-automation-EA4B71?logo=n8n&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLM-F55036)
![pytest](https://img.shields.io/badge/pytest-tests-0A9EDC?logo=pytest&logoColor=white)

## Visão geral

O Vectorpress acompanha notícias sobre Inteligência Artificial via RSS, armazena os conteúdos no PostgreSQL com pgvector e permite consultar essas notícias por meio de RAG. O MVP também inclui uma interface web em React, um bot Telegram e automação com n8n para manter a base atualizada.

## Demo

- Frontend: <https://vectorpress-zeta.vercel.app>
- API pública: <https://physiopathologic-marlys-unallayable.ngrok-free.dev>
- Bot Telegram: <https://t.me/@Vectorpress_bot>

O backend roda em um homelab pessoal e é publicado por um túnel reverso. Se a API
estiver fora do ar, o frontend carrega mas não exibe notícias.

## Funcionalidades

- Sincronização de notícias por RSS com deduplicação por URL.
- Persistência de notícias, chunks e embeddings no PostgreSQL.
- Busca vetorial com pgvector e respostas geradas por LLM usando apenas contexto recuperado.
- Endpoint REST para consulta RAG em `POST /ask`.
- Bot Telegram com comandos `/today`, `/list` e `/ask`.
- Workflow n8n para sincronização automática a cada 6 horas.
- Frontend React de tela única com abas de notícias e perguntas.
- Deploy em homelab com túnel reverso (ngrok) e frontend na Vercel.

## Arquitetura

```text
RSS Feeds
  ↓
FastAPI + Services
  ↓
PostgreSQL + pgvector
  ↓
RAG: chunks + embeddings + LLM
  ↓
Frontend React / Bot Telegram / n8n
```

## Stack tecnológica

| Camada | Tecnologias |
|--------|-------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Pydantic v2 |
| Banco | PostgreSQL 16, pgvector |
| IA/RAG | LangChain, sentence-transformers, Groq API |
| Frontend | React 18, Vite, TailwindCSS, shadcn/ui |
| Automação | n8n |
| Integração | Telegram Bot API |
| Infra | Docker, Docker Compose, ngrok, Vercel |
| Testes | pytest, pytest-asyncio |

## Índice

- [Sprint 01 - Fundação](#sprint-01---fundação)
- [Sprint 02 - Ingestão de Notícias](#sprint-02---ingestão-de-notícias)
- [Sprint 03 - Base Vetorial e RAG](#sprint-03---base-vetorial-e-rag)
- [Sprint 04 - Bot Telegram](#sprint-04---bot-telegram)
- [Sprint 05 - Automação com n8n](#sprint-05---automação-com-n8n)
- [Requisitos](#requisitos)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Como executar com Docker](#como-executar-com-docker)
- [Docker Compose de produção](#docker-compose-de-produção)
- [Exposição pública do backend](#exposição-pública-do-backend)
- [Deploy do frontend na Vercel](#deploy-do-frontend-na-vercel)
- [Webhook do Telegram em produção](#webhook-do-telegram-em-produção)
- [Workflow n8n em produção](#workflow-n8n-em-produção)
- [Endpoints](#endpoints)

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
   - `TELEGRAM_WEBHOOK_URL` — URL pública que o Telegram chamará (ex: `https://<sua-url-publica>/telegram/webhook`).
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

Copie o arquivo `.env.example` para `.env` e ajuste os valores conforme o ambiente.

```bash
cp .env.example .env
```

| Variável | Obrigatória | Uso |
|----------|-------------|-----|
| `APP_NAME` | Não | Nome exibido pela aplicação. |
| `APP_ENV` | Não | Ambiente atual: `development` ou `production`. |
| `LOG_LEVEL` | Não | Nível de logs do backend. |
| `DATABASE_URL` | Sim | URL assíncrona usada pelo SQLAlchemy no backend. |
| `POSTGRES_DB` | Sim | Nome do banco criado pelo container PostgreSQL. |
| `POSTGRES_USER` | Sim | Usuário do PostgreSQL. |
| `POSTGRES_PASSWORD` | Sim | Senha do PostgreSQL; altere em produção. |
| `POSTGRES_PORT` | Não | Porta exposta pelo PostgreSQL no compose local. |
| `BACKEND_PORT` | Não | Porta pública do backend no compose de produção. |
| `CORS_ALLOWED_ORIGINS` | Sim em produção | Origens permitidas pelo CORS, separadas por vírgula. |
| `EMBEDDING_PROVIDER` | Não | Provedor de embeddings: `local` ou `openai`. |
| `EMBEDDING_MODEL` | Não | Modelo de embeddings; padrão local `all-MiniLM-L6-v2`. |
| `OPENAI_API_KEY` | Condicional | Necessária para embeddings ou LLM via OpenAI. |
| `LLM_PROVIDER` | Não | Provedor do LLM: `groq` ou `openai`. |
| `LLM_MODEL` | Não | Modelo usado pelo gerador de respostas. |
| `GROQ_API_KEY` | Condicional | Necessária quando `LLM_PROVIDER=groq`. |
| `SYNC_TOKEN` | Recomendada em produção | Quando preenchida, `POST /news/sync` exige o header `X-Sync-Token`. Vazia deixa o endpoint aberto. |
| `ASK_RATE_LIMIT` | Não | Chamadas ao `/ask` por IP na janela; `0` desativa o limite. Padrão `10`. |
| `ASK_RATE_WINDOW_SECONDS` | Não | Tamanho da janela do limite, em segundos. Padrão `60`. |
| `RAG_MAX_AGE_DAYS` | Não | Janela de recência usada pelo endpoint `/ask`. |
| `NEWS_RETENTION_DAYS` | Não | Janela máxima de retenção das notícias no banco. |
| `TELEGRAM_TOKEN` | Condicional | Token do bot; sem ele o webhook responde `503`. |
| `TELEGRAM_WEBHOOK_URL` | Condicional | URL pública HTTPS do endpoint `/telegram/webhook`. |
| `TELEGRAM_WEBHOOK_SECRET` | Recomendada em produção | Quando preenchida, o webhook só aceita updates com o header `X-Telegram-Bot-Api-Secret-Token`. |
| `VITE_API_PROXY_TARGET` | Não | Destino do proxy usado somente pelo Vite em desenvolvimento. |
| `VITE_API_URL` | Sim | URL pública da API embutida no build estático do frontend. |
| `N8N_HOST` | Condicional | Domínio público do n8n em produção. |
| `N8N_PORT` | Não | Porta pública do n8n. |
| `N8N_PROTOCOL` | Condicional | Protocolo do n8n: `http` local ou `https` em produção. |
| `N8N_WEBHOOK_URL` | Condicional | URL pública base dos webhooks do n8n. |
| `GENERIC_TIMEZONE` | Não | Fuso horário usado pelo n8n. |
| `NGROK_AUTHTOKEN` | Condicional | Token do agente ngrok, quando o túnel é feito por ele. |
| `CLOUDFLARE_TUNNEL_TOKEN` | Condicional | Token do túnel nomeado do Cloudflare, quando há domínio próprio. |

Em produção, configure pelo menos `POSTGRES_PASSWORD`, `GROQ_API_KEY`, `SYNC_TOKEN`,
`VITE_API_URL`, `CORS_ALLOWED_ORIGINS`, `TELEGRAM_TOKEN`, `TELEGRAM_WEBHOOK_URL`,
`N8N_HOST`, `N8N_PROTOCOL` e `N8N_WEBHOOK_URL` com valores reais.

Não use comentários na mesma linha de um valor. O `env_file` do Docker Compose só
descarta linhas que começam com `#`, então `GROQ_API_KEY=abc  # chave` faz a chave
chegar ao container com o comentário embutido.

## Como executar com Docker

```bash
docker compose up --build
```

Serviços expostos:

- API: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- PostgreSQL: `localhost:5432`

O frontend (Vite dev server) roda em `http://localhost:5173` e faz proxy das chamadas de API (`/news`, `/ask`, `/health`) para o backend via `VITE_API_PROXY_TARGET` (padrão `http://backend:8000`).

## Docker Compose de produção

A Sprint 07 adiciona um compose separado para o homelab, mantendo o `docker-compose.yml` como ambiente local de desenvolvimento. Em produção, o Compose executa apenas PostgreSQL, backend e n8n; o frontend é publicado separadamente na Vercel.

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Serviços expostos:

- API: `http://localhost:${BACKEND_PORT:-8000}`
- n8n: `http://localhost:${N8N_PORT:-5678}`

O PostgreSQL fica disponível apenas na rede interna do Compose. O serviço `n8n` persiste os dados no volume `n8n_data` e deve chamar o backend pela rede interna usando `http://backend:8000`. A variável `VITE_API_URL` deve ser configurada no projeto da Vercel, não no Compose de produção.

## Exposição pública do backend

O backend roda em um homelab, sem IP público e sem portas abertas no roteador. A
API chega à internet por um túnel reverso: o agente abre uma conexão de saída
para o provedor, que devolve uma URL HTTPS apontando para o serviço local.

O `docker-compose.prod.yml` publica o backend apenas em `127.0.0.1`, de modo que
o túnel é o único caminho de entrada.

### Opção em uso: ngrok

Escolhido por não exigir domínio próprio. O plano gratuito fornece um domínio
estático, o que é essencial: uma URL que muda a cada reinício quebraria o build
do frontend na Vercel e o webhook do Telegram, que gravam o endereço.

Reserve o domínio em <https://dashboard.ngrok.com/domains> e anote o authtoken.
O agente sobe como container na mesma rede do Compose, o que permite alcançar o
backend por `backend:8000` sem passar pela internet:

```bash
docker run -d --name vectorpress-ngrok \
  --network vectorpress_default \
  --restart unless-stopped \
  -e NGROK_AUTHTOKEN=<seu-token> \
  ngrok/ngrok:latest \
  http backend:8000 --url=https://<seu-dominio>.ngrok-free.dev
```

```bash
curl https://<seu-dominio>.ngrok-free.dev/health
```

O plano gratuito serve uma página de aviso antes de responder a requisições de
navegador. O cliente HTTP do frontend envia o header `ngrok-skip-browser-warning`
para contornar isso; veja `frontend/src/lib/api.js`.

### Alternativa com domínio próprio: Cloudflare Tunnel

Com um domínio gerenciado pela Cloudflare, o serviço `cloudflared` já definido no
`docker-compose.prod.yml` substitui o ngrok e entrega um hostname próprio, do tipo
`api.seudominio.com`.

Crie o túnel em Zero Trust → Networks → Tunnels, copie o token para
`CLOUDFLARE_TUNNEL_TOKEN` no `.env` e aponte o *public hostname* para
`HTTP → backend:8000`. Depois:

```bash
docker rm -f vectorpress-ngrok
docker compose -f docker-compose.prod.yml up -d cloudflared
```

### Depois de publicar

Atualize o `.env` de produção com a URL escolhida:

```bash
TELEGRAM_WEBHOOK_URL=https://<sua-url>/telegram/webhook
CORS_ALLOWED_ORIGINS=https://vectorpress-zeta.vercel.app
```

E configure `VITE_API_URL` no projeto da Vercel, não no Compose: o valor é
embutido no build estático, então toda mudança de URL exige um novo deploy do
frontend.

## Deploy do frontend na Vercel

O frontend é um build estático React/Vite. Na Vercel, ele deve ser publicado a partir da pasta `frontend` e precisa receber a URL pública HTTPS do backend na variável `VITE_API_URL`.

Antes de publicar, confirme que o backend já está acessível pelo túnel:

```bash
curl https://<sua-url-publica>/health
```

Configuração do projeto na Vercel:

| Campo | Valor |
|-------|-------|
| Framework Preset | `Vite` |
| Root Directory | `frontend` |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Install Command | `npm ci` |

Variável de ambiente na Vercel:

| Nome | Valor |
|------|-------|
| `VITE_API_URL` | `https://<sua-url-publica>` |

Depois do primeiro deploy, copie o domínio gerado pela Vercel e libere essa origem no backend:

```bash
CORS_ALLOWED_ORIGINS=https://vectorpress-zeta.vercel.app
```

Se usar mais de um domínio, separe as origens por vírgula:

```bash
CORS_ALLOWED_ORIGINS=https://vectorpress-zeta.vercel.app,https://www.seudominio.com  # dominios adicionais, se houver
```

Validação após o deploy:

1. Acesse a URL pública do frontend na Vercel.
2. Abra a aba "Notícias" e confirme que os cards carregam a partir do endpoint `/news`.
3. Abra a aba "Perguntar" e envie uma pergunta para validar o endpoint `/ask`.
4. Se o navegador bloquear a requisição por CORS, confira se `CORS_ALLOWED_ORIGINS` no backend contém exatamente a origem exibida na barra de endereço do frontend, incluindo `https://`.

## Webhook do Telegram em produção

O bot do Telegram usa o endpoint público `POST /telegram/webhook`. Em produção, esse endpoint deve usar a URL HTTPS publicada pelo túnel.

Configure o `.env` do backend:

```bash
TELEGRAM_TOKEN=<token-do-botfather>
TELEGRAM_WEBHOOK_URL=https://<sua-url-publica>/telegram/webhook
```

Com o backend rodando e a URL pública disponível, registre o webhook no Telegram:

```bash
curl -X POST "https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook" \
  -d "url=https://<sua-url-publica>/telegram/webhook" \
  -d "secret_token=<TELEGRAM_WEBHOOK_SECRET>"
```

O endpoint é público, então sem o `secret_token` qualquer pessoa pode forjar um
update e acionar os comandos do bot, incluindo o `/ask`, que consome cota do LLM.
Com ele configurado, o Telegram passa a enviar o header
`X-Telegram-Bot-Api-Secret-Token` e o backend rejeita o resto com `403`.

Confira se o webhook foi registrado:

```bash
curl "https://api.telegram.org/bot<TELEGRAM_TOKEN>/getWebhookInfo"
```

Validação no Telegram:

1. Envie `/today` para o bot e confirme se ele retorna as últimas manchetes.
2. Envie `/list` para validar a listagem paginada.
3. Envie `/ask uma pergunta sobre as notícias recentes` para validar o fluxo RAG.

Se o endpoint `/telegram/webhook` responder `503`, confira se `TELEGRAM_TOKEN` está definido no ambiente do backend e reinicie o serviço:

```bash
docker compose -f docker-compose.prod.yml up -d --build backend
```

## Workflow n8n em produção

O workflow versionado em `n8n/workflows/rss-sync.json` deve ser importado no n8n de produção e ajustado manualmente antes de ser ativado. O arquivo mantém placeholders para evitar commitar URLs e IDs reais.

Se o n8n estiver rodando no `docker-compose.prod.yml`, configure o nó **HTTP Request** para chamar o backend pela rede interna do Compose:

```text
http://backend:8000/news/sync
```

Se o n8n estiver fora do Compose, por exemplo no n8n Cloud, configure o nó **HTTP Request** com a URL pública do túnel:

```text
https://<sua-url-publica>/news/sync
```

Checklist de configuração no editor do n8n:

1. Importe `n8n/workflows/rss-sync.json`.
2. Abra o nó **HTTP Request** e ajuste a URL conforme a tabela acima.
3. Ainda no nó, adicione o header `X-Sync-Token` com o valor de `SYNC_TOKEN`.
   Sem ele o backend responde `401`. Uma credencial **Header Auth** guarda o
   segredo criptografado, em vez de deixá-lo visível no workflow.
4. Crie ou selecione a credencial **Telegram** nos nós de notificação, ou
   desative esses nós se o bot ainda não estiver configurado.
5. Substitua `seu_chat_id_adm` pelo chat ID do administrador.
6. Execute **Test workflow** e confirme que o retorno contém `created`, `skipped`, `errors` e `sources`.
7. Salve antes de ativar: o n8n agenda a versão salva, não a que está na tela.
8. Ative o workflow somente depois do teste manual passar.

O n8n fica acessível apenas em `127.0.0.1` no homelab. Para abrir o editor a
partir de outra máquina, use um túnel SSH:

```bash
ssh -L 5678:localhost:5678 usuario@homelab
```

Para validar pelo container do n8n no Compose de produção, execute uma chamada manual a partir da mesma rede:

```bash
docker compose -f docker-compose.prod.yml exec n8n wget -qO- http://backend:8000/health
```

Depois da primeira execução agendada, confira no banco se novas notícias foram persistidas e verifique se a mensagem de sucesso chegou no Telegram do admin.

## Como executar localmente

1. Crie e ative um ambiente virtual.
2. Instale as dependências do backend (use `requirements-dev.txt` para incluir as dependências de teste).
3. Exporte as variáveis de ambiente.
4. Inicie a API com Uvicorn.
5. (Opcional) Inicie o frontend separadamente com Vite.

Exemplo:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (em outro terminal):

```bash
cd frontend
npm install
npm run dev
# acesse http://localhost:5173
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
{"message":"Vectorpress API"}
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
├── docker-compose.prod.yml
├── docker-compose.yml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ui/
│   │   ├── lib/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
├── n8n/
│   └── workflows/
│       └── rss-sync.json
└── README.md
```

## Próximos passos

As próximas sprints vão adicionar o deploy da aplicação.
