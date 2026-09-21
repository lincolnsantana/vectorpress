# ROADMAP.md
> Roadmap oficial do projeto Vectorpress

Versão: 1.0

---

# Objetivo

Este documento descreve o planejamento de desenvolvimento do projeto.

Cada Fase representa um dia de trabalho focado.

Ao final de cada Fase deverá existir:
- uma branch finalizada;
- commits semânticos;
- documentação atualizada;
- merge para `main`;
- criação de uma tag.

Nenhuma Fase poderá iniciar sem que a anterior tenha sido concluída.

---

# Convenções

## Branches

Padrão:
```
phase/01-foundation
phase/02-ingestion
phase/03-rag
phase/04-telegram
phase/05-n8n
phase/06-frontend
phase/07-deploy
```

## Commits

Todos os commits utilizam Conventional Commits em **inglês**.

Exemplo:
```
feat: add health check endpoint
feat: configure Docker Compose
feat: implement RSS client
fix: correct vector search query
docs: update API documentation
refactor: simplify service layer
test: add RSS parser tests
chore: setup development environment
```

Um commit = um propósito.

---

# Fase 01 — Fundação

**Versão:** v0.1.0
**Branch:** `phase/01-foundation`
**Duração:** 1 dia

## Objetivo
Criar toda a infraestrutura do projeto.

## Entregáveis
- [ ] Estrutura de pastas do projeto
- [ ] Docker Compose (backend + postgres)
- [ ] Aplicação FastAPI com lifespan async
- [ ] PostgreSQL 16 + extensão pgvector
- [ ] Variáveis de ambiente (.env + .env.example)
- [ ] Endpoint de health check (`GET /health`)
- [ ] Conexão com banco via SQLAlchemy 2 (async)
- [ ] README inicial com instruções de execução
- [ ] pytest configurado (pelo menos um teste passando)

## Fora do escopo
- Ingestão RSS
- RAG
- Telegram
- Frontend
- n8n

## Critérios de aceite
- [ ] `docker compose up --build` executa sem erros
- [ ] API inicia e responde na porta 8000
- [ ] `/health` retorna 200 com status do banco
- [ ] PostgreSQL tem extensão pgvector habilitada
- [ ] README explica como rodar localmente
- [ ] Pelo menos um teste pytest passa

## Merge
```bash
git checkout main
git merge phase/01-foundation
git tag v0.1.0
```

---

# Fase 02 — Ingestão de Notícias

**Versão:** v0.2.0
**Branch:** `phase/02-ingestion`
**Duração:** 1 dia

## Objetivo
Construir a camada responsável pela coleta das notícias.

## Entregáveis
- [ ] Parser RSS (feedparser ou aiohttp + xmltodict)
- [ ] Serviço de sincronização de notícias
- [ ] Models SQLAlchemy: `news`, `chunks`
- [ ] Migração Alembic (opcional, mas recomendado)
- [ ] Endpoint `POST /news/sync` (disparo manual)
- [ ] Endpoint `GET /news` (lista paginada)
- [ ] Endpoint `GET /news/{id}` (artigo único)
- [ ] Prevenção de duplicatas (por URL)
- [ ] Testes para endpoints de sync e listagem

## Fontes (MVP)
- OpenAI Blog
- Anthropic Blog
- TechCrunch AI

## Fora do escopo
- Embeddings
- RAG
- Telegram

## Critérios de aceite
- [ ] Chamada `POST /news/sync` importa artigos reais
- [ ] Artigos são persistidos no PostgreSQL
- [ ] URLs duplicadas são ignoradas
- [ ] `GET /news` retorna resultados paginados
- [ ] pytest cobre caminho feliz e casos de borda

## Merge
```bash
git tag v0.2.0
```

---

# Fase 03 — Base Vetorial + RAG

**Versão:** v0.3.0
**Branch:** `phase/03-rag`
**Duração:** 1 dia

## Objetivo
Transformar notícias em conhecimento pesquisável.

## Entregáveis
- [ ] Serviço de chunking (LangChain RecursiveCharacterTextSplitter)
- [ ] Serviço de embeddings (sentence-transformers via `sentence-transformers` ou `langchain-huggingface`)
- [ ] Integração com pgvector (busca por similaridade cosseno)
- [ ] Tabela `embeddings` com tipo VECTOR
- [ ] Endpoint RAG `POST /ask`
- [ ] Template de prompt com regra estrita de contexto apenas
- [ ] Citação de fontes nas respostas
- [ ] Testes para chunking, embeddings e endpoint RAG

## Pipeline
```
Pergunta
↓
Embedding (mesmo modelo da ingestão)
↓
Busca Vetorial (pgvector, top 5 chunks)
↓
Monta prompt com contexto
↓
LLM (Groq API — tier gratuito, sem cartão necessário)
↓
Resposta com fontes
```

## Fora do escopo
- Telegram
- Frontend
- n8n

## Critérios de aceite
- [ ] Após sync, artigos são fragmentados e embedados
- [ ] `POST /ask` retorna respostas baseadas APENAS nas notícias armazenadas
- [ ] Se não houver chunks relevantes, retorna: "Não encontrei informações suficientes..."
- [ ] Resposta inclui URLs das fontes
- [ ] pytest passa para o fluxo RAG

## Estratégia de LLM
Usar **Groq API** (tier gratuito: 20 req/min, 1M tokens/dia) para custo zero durante desenvolvimento.
Modelo: `llama3-8b-8192` ou `mixtral-8x7b-32768`.

## Merge
```bash
git tag v0.3.0
```

---

# Fase 04 — Bot Telegram

**Versão:** v0.4.0
**Branch:** `phase/04-telegram`
**Duração:** 1 dia

## Objetivo
Disponibilizar consultas através do Telegram.

## Entregáveis
- [ ] Configuração do bot Telegram (python-telegram-bot v20+, async)
- [ ] Integração via webhook (`POST /telegram/webhook`)
- [ ] Comando `/today` — últimas 5 manchetes
- [ ] Comando `/list` — lista paginada de notícias
- [ ] Comando `/ask <pergunta>` — consulta RAG
- [ ] Tratamento de erros (falhas graciosas)
- [ ] Testes para handlers de comandos (Telegram API mockada)

## Fora do escopo
- Histórico de conversas
- Login / Admin

## Critérios de aceite
- [ ] Bot registrado no @BotFather
- [ ] `/today` mostra notícias reais do banco
- [ ] `/ask` retorna respostas contextuais com fontes
- [ ] Webhook funciona quando deployado
- [ ] pytest cobre comandos do bot

## Merge
```bash
git tag v0.4.0
```

---

# Fase 05 — Automação com n8n

**Versão:** v0.5.0
**Branch:** `phase/05-n8n`
**Duração:** 1 dia

## Objetivo
Automatizar a sincronização das notícias utilizando n8n.

> Esta Fase é construída MANUALMENTE no editor n8n (drag-and-drop), não via geração de código.
> Isso demonstra habilidade real com n8n.

## Design do Workflow
```
Cron (a cada 6 horas)
↓
RSS Read (3 feeds em paralelo)
↓
Split Items
↓
HTTP Request → POST /news/sync
↓
IF (sucesso / falha)
↓
Log em arquivo ou mensagem Telegram para admin
```

## Nós
- **Schedule Trigger** — a cada 6 horas
- **RSS Read** — feeds OpenAI, Anthropic, TechCrunch
- **Split Out** — processa cada item
- **HTTP Request** — chama sua API `/news/sync`
- **IF** — trata 200 vs erro
- **Telegram** — notifica admin em caso de falha (opcional)

## Entregáveis
- [ ] Workflow n8n construído e testado manualmente
- [ ] Workflow exportado para `/n8n/workflows/rss-sync.json`
- [ ] Documentação no README sobre como importar
- [ ] Screenshot do workflow no README (opcional, mas valoriza)

## Critérios de aceite
- [ ] Workflow executa automaticamente no agendamento
- [ ] Novos artigos aparecem no banco sem intervenção manual
- [ ] Falhas são registradas (não silenciosas)
- [ ] Arquivo do workflow está versionado no git

## Opções de Hospedagem do n8n
- **Desenvolvimento local:** `docker run -it --rm -p 5678:5678 n8nio/n8n`
- **Produção:** n8n Cloud (500 execuções/mês gratuitas) OU self-hosted em VPS barato (~$5/mês)

## Merge
```bash
git tag v0.5.0
```

---

# Fase 06 — Frontend

**Versão:** v0.6.0
**Branch:** `phase/06-frontend`
**Duração:** 1 dia

## Objetivo
Criar uma interface web mínima de tela única.

## Entregáveis
- [ ] Setup React + Vite + TailwindCSS + shadcn/ui
- [ ] Tela única com abas (shadcn/ui):
  - Aba "Notícias":
    - Cards das últimas notícias (título, fonte, data)
    - Link para a fonte original
  - Aba "Perguntar":
    - Caixa de pergunta (chama `/ask`)
    - Exibição da resposta com fontes
- [ ] Responsivo (mobile-friendly)
- [ ] Variável de ambiente para URL da API

## Fora do escopo
- Dashboard
- Login
- Painel administrativo
- Atualizações em tempo real
- Página de detalhes do artigo

## Critérios de aceite
- [ ] Frontend conecta à API do backend
- [ ] Aba "Notícias" exibe os cards corretamente
- [ ] Aba "Perguntar" retorna resposta RAG com fontes
- [ ] Design system shadcn/ui aplicado de forma consistente
- [ ] Funciona no celular

## Nota sobre Experiência com React
Sua experiência com React é limitada (estágio de 3 meses, WordPress/Elementor).
Mantenha componentes pequenos e simples. Use apenas functional components + hooks.
O shadcn/ui fornece os componentes prontos (Tabs, Card, Button, Input), então o foco fica na composição, não na criação de componentes do zero.
Se React virar gargalo, considere trocar para **Jinja2 templates** ou **Streamlit** — mas tente React primeiro, pois está no SPEC.

## Merge
```bash
git tag v0.6.0
```

---

# Fase 07 — Deploy

**Versão:** v0.7.0 → v1.0.0
**Branch:** `phase/07-deploy`
**Duração:** 1 dia

## Objetivo
Preparar o primeiro release público.

## Arquitetura de Deploy (homelab + Vercel)

| Camada | Onde | Detalhes |
|---|---|---|
| Backend (FastAPI) | Homelab (Docker) | Precisa de URL pública HTTPS |
| PostgreSQL + pgvector | Homelab (Docker) | Junto ao backend |
| n8n | Homelab (Docker) | Chama o backend pela rede interna |
| Bot Telegram | Homelab (Docker) | Webhook HTTPS público (ou polling) |
| Frontend (React) | Vercel | Build estático + `VITE_API_URL` |

## Exposição do Homelab

O backend precisa de uma **URL pública HTTPS** para:
- O frontend no Vercel chamar `/news` e `/ask`
- O Telegram entregar o webhook (exige HTTPS válido)

Abordagem escolhida: **Cloudflare Tunnel** (gratuito, HTTPS automático, funciona sem IP público e mascara a infra doméstica).

Alternativa: reverse proxy (Caddy/Nginx + Let's Encrypt) caso o ISP forneça IP público.

## Entregáveis
- [ ] Docker Compose pronto para produção (backend + postgres + n8n + telegram)
- [ ] `.env.example` completamente documentado
- [ ] Guia de exposição do backend via Cloudflare Tunnel
- [ ] Deploy do frontend no Vercel (build estático + `VITE_API_URL`)
- [ ] CORS configurado no backend para o domínio do Vercel
- [ ] README final com:
  - O que o projeto faz
  - Stack tecnológica
  - Screenshots / demo GIF
  - Como rodar localmente
  - Como fazer deploy
  - Tabela de variáveis de ambiente
- [ ] Bot Telegram configurado com webhook de produção
- [ ] Workflow n8n conectado à API de produção

## Critérios de aceite
- [ ] Aplicação está publicamente acessível
- [ ] Frontend no Vercel acessa o backend do homelab (CORS OK)
- [ ] Bot Telegram responde em produção
- [ ] n8n sincroniza notícias automaticamente
- [ ] RAG responde perguntas corretamente
- [ ] README tem link para demo ao vivo

## Merge e Release
```bash
git checkout main
git merge phase/07-deploy
git tag v1.0.0
```

---

# Critérios de Encerramento do Projeto

O projeto será considerado concluído quando:
- [ ] Todas as 7 Fases forem finalizadas
- [ ] Todas as branches forem integradas à `main`
- [ ] Todas as tags forem criadas
- [ ] README estiver atualizado e profissional
- [ ] Deploy público estiver funcionando
- [ ] Bot Telegram estiver respondendo
- [ ] Workflow n8n estiver em execução

---

# Evolução Pós v1.0

| Versão | Recurso                          |
|--------|----------------------------------|
| v1.1.0 | Autenticação JWT                 |
| v1.2.0 | Dashboard Administrativo (React) |
| v1.3.0 | Observabilidade (Langfuse)       |
| v1.4.0 | Busca Híbrida (BM25 + Vetorial)  |
| v1.5.0 | Seletor de múltiplos provedores LLM |
| v2.0.0 | Agentes com LangGraph            |
