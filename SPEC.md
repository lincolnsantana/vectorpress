# Vectorpress
> Especificação Técnica (SPEC)

Versão: 1.0.0

---

# 1. Visão Geral

## Objetivo

Desenvolver uma plataforma capaz de monitorar notícias relacionadas à Inteligência Artificial, armazenar essas informações em uma base vetorial e disponibilizar consultas inteligentes através de Retrieval-Augmented Generation (RAG).

O projeto servirá como portfólio técnico, demonstrando conhecimentos em:

- Backend Python
- APIs REST
- FastAPI
- PostgreSQL + pgvector
- Docker
- RAG com LangChain
- Bot Telegram
- Automação com n8n
- Deploy
- Arquitetura limpa

Este projeto representa um MVP (Minimum Viable Product).

O foco é entregar um produto pequeno, funcional e facilmente evolutivo.

---

# 2. Objetivos do Projeto

O projeto deverá demonstrar capacidade de:

- construir APIs REST profissionais;
- trabalhar com dados estruturados e vetoriais;
- integrar LLMs;
- construir pipelines de ingestão;
- implementar RAG;
- desenvolver integrações com Telegram;
- utilizar Docker;
- preparar aplicações para produção.

---

# 3. Escopo do MVP

## Incluir

- API REST
- PostgreSQL com pgvector
- Ingestão de notícias (RSS)
- Base vetorial
- Endpoint de consulta RAG
- Bot Telegram
- Interface Web simples
- Docker e Docker Compose
- Deploy na AWS
- Testes automatizados (pytest)

## Não incluir (versões futuras)

- Autenticação / Login
- Cadastro de usuários
- Painel administrativo
- Redis / Cache
- Observabilidade
- Multi-tenant
- Histórico de conversas
- Sistema de permissões

---

# 4. Público-alvo

- Recrutadores
- Desenvolvedores
- Estudantes
- Profissionais interessados em IA

---

# 5. Stack

## Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic v2
- pytest

## Banco de dados
- PostgreSQL
- Extensão pgvector

## IA
- LangChain
- LLM configurável via variável de ambiente (padrão: Groq API)
- Modelo de embeddings configurável via variável de ambiente (padrão: sentence-transformers)

## Frontend
- React 18 + Vite + TailwindCSS + shadcn/ui (mínimo, apenas 1 tela)

## Automação
- n8n (self-hosted ou cloud)

## Deploy
- Docker e Docker Compose
- Self-hosted
- Render (alternativa gratuita)

---

# 6. Arquitetura

Arquitetura em camadas, simplificada para clareza de nível júnior/pleno.

```
Cliente (Navegador / Telegram)
↓
Frontend (React)  ou  Bot Telegram (webhook)
↓
Routers FastAPI
↓
Services (lógica de negócio)
↓
SQLAlchemy Models + pgvector
↓
PostgreSQL
```

A lógica de negócio fica nas Services. O acesso ao banco passa pelo SQLAlchemy ORM.
Não há necessidade de uma camada de Repository explícita no MVP — o ORM já abstrai o banco.

---

# 7. Estrutura de Pastas

```
vectorpress/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── news.py
│   │   │   ├── rag.py
│   │   │   ├── telegram.py
│   │   │   └── health.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── logging.py
│   │   │
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   └── models.py
│   │   │
│   │   ├── rag/
│   │   │   ├── chunker.py
│   │   │   ├── embeddings.py
│   │   │   ├── retriever.py
│   │   │   └── generator.py
│   │   │
│   │   ├── rss/
│   │   │   ├── parser.py
│   │   │   ├── sources.py
│   │   │   └── sync.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── news.py
│   │   │   └── rag.py
│   │   │
│   │   ├── telegram/
│   │   │   ├── bot.py
│   │   │   └── commands.py
│   │   │
│   │   ├── tests/
│   │   │   ├── test_health.py
│   │   │   ├── test_news.py
│   │   │   └── test_rag.py
│   │   │
│   │   ├── utils/
│   │   │   └── helpers.py
│   │   │
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ui/            # componentes gerados pelo shadcn/ui
│   │   ├── lib/
│   │   │   └── utils.ts       # utilitário cn (clsx + tailwind-merge)
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
│
├── n8n/
│   └── workflows/
│       └── rss-sync.json
│
├── docs/
│
├── .env.example
├── .gitignore
├── CONTRIBUTING.md
├── ROADMAP.md
├── LICENSE
├── README.md
└── docker-compose.yml
```

---

# 8. Fontes de Notícias

Feeds RSS (MVP):

- OpenAI Blog
- Anthropic Blog
- TechCrunch AI
- Hacker News (tag AI)
- Google AI Blog

Novas fontes podem ser adicionadas via arquivo `sources.py`.

---

# 9. Pipeline

```
Feed RSS
↓
Parser (feedparser)
↓
Normalização e deduplicação
↓
Salva no PostgreSQL (tabela news)
↓
Fragmenta conteúdo (LangChain)
↓
Gera embeddings (sentence-transformers ou OpenAI)
↓
Salva no pgvector (tabela embeddings)
↓
Usuário pergunta via API ou Telegram
↓
Embedding da pergunta
↓
Busca vetorial (similaridade cosseno no pgvector)
↓
Monta prompt com contexto
↓
LLM gera resposta
↓
Retorna resposta + fontes
```

---

# 10. Schema do Banco de Dados

## news
| Coluna       | Tipo        | Observações              |
|--------------|-------------|--------------------------|
| id           | UUID (PK)   |                          |
| title        | VARCHAR     | not null                 |
| url          | VARCHAR     | unique, not null         |
| source       | VARCHAR     | ex: "OpenAI Blog"        |
| author       | VARCHAR     | nullable                 |
| content      | TEXT        | texto completo           |
| published_at | TIMESTAMP   |                          |
| created_at   | TIMESTAMP   | default now()            |

## chunks
| Coluna   | Tipo      | Observações              |
|----------|-----------|--------------------------|
| id       | UUID (PK) |                          |
| news_id  | UUID (FK) | → news.id                |
| chunk    | TEXT      | fragmento de texto       |
| position | INTEGER   | ordem no artigo          |

## embeddings
| Coluna    | Tipo        | Observações                    |
|-----------|-------------|--------------------------------|
| id        | UUID (PK)   |                                |
| chunk_id  | UUID (FK)   | → chunks.id                    |
| embedding | VECTOR(384) | dimensão depende do modelo     |

---

# 11. Endpoints da API

| Método | Endpoint        | Descrição                            |
|--------|-----------------|--------------------------------------|
| GET    | /               | Mensagem raiz                        |
| GET    | /health         | Health check (DB + extensão vetorial)|
| POST   | /news/sync      | Disparar sincronização RSS manual    |
| GET    | /news           | Listar notícias (paginado)           |
| GET    | /news/{id}      | Buscar notícia por ID                |
| POST   | /ask            | Consulta RAG                         |

Nenhum endpoint exige autenticação no MVP.

---

# 12. Comportamento do RAG

Pipeline:

```
Pergunta
↓
Embedding
↓
Busca Vetorial (pgvector, top_k=5)
↓
Recupera chunks + metadados da fonte
↓
Monta prompt com instrução de sistema
↓
LLM (Groq / Bedrock / OpenAI)
↓
Resposta
```

O prompt de sistema deve instruir o modelo:
> "Responda APENAS usando o contexto fornecido. Se o contexto for insuficiente, diga: 'Não encontrei informações suficientes para responder esta pergunta.' NÃO use conhecimento externo."

---

# 13. Bot Telegram

Comandos:

| Comando  | Descrição                                |
|----------|------------------------------------------|
| /today   | Últimas 5 manchetes com links            |
| /list    | Lista paginada de notícias recentes      |
| /ask     | Fazer uma pergunta (dispara pipeline RAG)|

Sem autenticação. O bot conversa diretamente com a API.

---

# 14. Frontend (Mínimo)

Apenas uma tela, com duas abas:

### Aba "Notícias"
- Cards das últimas notícias (título, fonte, data)
- Link para a fonte original

### Aba "Perguntar"
- Caixa de pergunta (chama endpoint /ask, mostra resposta com fontes)

**Design system:** shadcn/ui (construído sobre TailwindCSS e Radix UI).

Sem funcionalidades administrativas. Sem dashboards. Sem página de detalhes.

---

# 15. Docker

Totalmente executável via:

```bash
docker compose up --build
```

Serviços:
- `backend` — aplicação FastAPI
- `postgres` — PostgreSQL 16 com pgvector
- `frontend` — servidor de desenvolvimento React (ou build estático)

O n8n roda separadamente (local ou cloud) e NÃO está no docker-compose.yml do MVP.

---

# 16. Variáveis de Ambiente

```bash
# Banco de dados
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/vectorpress

# LLM
LLM_PROVIDER=groq          # groq | bedrock | openai
LLM_MODEL=llama3-8b-8192   # ou ID do modelo para Bedrock
GROQ_API_KEY=              # se usar Groq
AWS_ACCESS_KEY_ID=         # se usar Bedrock
AWS_SECRET_ACCESS_KEY=     # se usar Bedrock
AWS_REGION=us-east-1       # se usar Bedrock
OPENAI_API_KEY=            # se usar OpenAI

# Embeddings
EMBEDDING_PROVIDER=local   # local | openai
# Para local: usa sentence-transformers (all-MiniLM-L6-v2, 384d)

# Telegram
TELEGRAM_TOKEN=            # do @BotFather
TELEGRAM_WEBHOOK_URL=      # https://seudominio.com/telegram/webhook

# App
APP_ENV=development
LOG_LEVEL=INFO
```

Nunca commitar segredos. Sempre usar `.env` + `.env.example`.

---

# 17. Fluxo Git

Cada Fase tem sua própria branch.

```
main
↓
git checkout -b phase/01-foundation
↓
merge via PR
↓
main
↓
git checkout -b phase/02-ingestion
↓
merge via PR
↓
...
```

Nunca commitar diretamente na `main`.

---

# 18. Commits

Todos os commits seguem Conventional Commits.

Idioma: **inglês** (padrão da indústria para portfólios técnicos).

Exemplos:

```
feat: add health check endpoint
feat: setup Docker Compose with Postgres
feat: implement RSS parser for OpenAI blog
feat: create news sync endpoint
fix: correct vector similarity query
refactor: simplify chunking service
docs: update README with setup instructions
test: add pytest for RAG endpoint
chore: configure pre-commit hooks
```

Um commit = um propósito. Nunca misturar mudanças não relacionadas.

---

# 19. Fluxo de Desenvolvimento

Para cada Fase:

Planejar → Implementar → Testar (pytest) → Atualizar docs → Commitar → Próxima funcionalidade

Nunca implementar duas funcionalidades antes de commitar.

---

# 20. Definição de Concluído (Definition of Done)

Uma funcionalidade só está concluída quando:

- Código implementado e tipado
- Sem warnings críticos (ruff / mypy limpo)
- pytest passando
- README atualizado (se necessário)
- Commit realizado

---

# 21. Requisitos de Código

Todo código deve:

- Usar type hints
- Ter responsabilidade única
- Evitar duplicação (DRY)
- Seguir princípios de Clean Code
- Usar nomes descritivos
- Evitar comentários desnecessários

---

# 22. Versionamento

Cada Fase concluída gera uma versão.

| Fase | Versão | Foco                |
|------|--------|---------------------|
| 01   | v0.1.0 | Fundação            |
| 02   | v0.2.0 | Ingestão            |
| 03   | v0.3.0 | RAG                 |
| 04   | v0.4.0 | Bot Telegram        |
| 05   | v0.5.0 | Automação n8n       |
| 06   | v0.6.0 | Frontend            |
| 07   | v0.7.0 | Deploy (AWS/Render) |
| —    | v1.0.0 | Primeiro release público |

---

# 23. Roadmap Futuro (pós v1.0)

- Autenticação JWT
- Painel administrativo
- Múltiplos provedores de LLM
- Agentes com LangGraph
- Busca híbrida (BM25 + vetorial)
- Redis caching
- Observabilidade (Langfuse, OpenTelemetry)
- Geração de newsletter
- Resumos em áudio
- Favoritos e tags
