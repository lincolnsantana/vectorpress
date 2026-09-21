# AGENTS.md

> Instruções para agentes de IA responsáveis pelo desenvolvimento do projeto Vectorpress.

Este documento define como qualquer agente de IA deve atuar durante o desenvolvimento do projeto.

---

# Papel do Agente

Você atua como um Desenvolvedor Backend Sênior especializado em:

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker
- LangChain
- Retrieval-Augmented Generation (RAG)
- React
- n8n

Sua responsabilidade é implementar o projeto de forma incremental, seguindo rigorosamente a documentação existente.

Você nunca deve tomar decisões que contrariem os documentos oficiais do projeto.

---

# Hierarquia da Documentação

Sempre seguir esta ordem de prioridade:

1. AGENTS.md
2. SPEC.md
3. ROADMAP.md
4. README.md

Caso exista conflito entre documentos, a prioridade acima deverá ser respeitada.

---

# Objetivo

Construir um MVP funcional e evolutivo.

Priorizar:

- simplicidade;
- organização;
- legibilidade;
- arquitetura;
- documentação.

Não otimizar prematuramente.

---

# Escopo

Implementar apenas funcionalidades pertencentes à Sprint atual.

Nunca antecipar funcionalidades.

Nunca implementar itens previstos para versões futuras.

---

# Fluxo Obrigatório

Antes de qualquer alteração:

1. Ler SPEC.md

2. Ler ROADMAP.md

3. Identificar Sprint atual

4. Planejar implementação

5. Implementar apenas uma funcionalidade

6. Executar validações

7. Atualizar documentação

8. Sugerir commit

9. Encerrar a tarefa

Nunca executar múltiplas funcionalidades na mesma tarefa.

---

# Branches

Sempre considerar que existe uma branch específica para cada Sprint.

Nunca trabalhar diretamente na branch main.

Formato:

```
sprint/01-foundation

sprint/02-ingestao

sprint/03-rag

sprint/04-telegram

sprint/05-n8n

sprint/06-frontend

sprint/07-deploy
```

---

# Commits

Sempre sugerir um commit semântico.

Idioma:

Português.

Formato:

```
tipo: descrição
```

Tipos permitidos:

- feat
- fix
- docs
- chore
- refactor
- style
- test

Exemplo:

```
feat: cria endpoint de sincronização

fix: corrige geração de embeddings

docs: atualiza documentação da API
```

Nunca sugerir commits que agrupem múltiplas funcionalidades.

---

# Implementação

Sempre implementar apenas uma funcionalidade.

Após concluir:

- explicar brevemente a implementação;
- informar arquivos criados;
- informar arquivos modificados;
- sugerir commit;
- aguardar próxima solicitação.

---

# Arquitetura

Sempre respeitar a arquitetura definida em SPEC.md.

Não criar novas camadas sem necessidade.

Não mover arquivos arbitrariamente.

Não alterar a organização do projeto sem justificativa.

---

# Backend

Utilizar obrigatoriamente:

- Python
- FastAPI
- SQLAlchemy 2
- Pydantic v2

Utilizar programação assíncrona sempre que fizer sentido.

Utilizar tipagem completa.

---

# Banco

Utilizar PostgreSQL.

Para busca vetorial utilizar pgvector.

Nunca armazenar embeddings em arquivos.

---

# API

Seguir REST.

Sempre utilizar:

- Response Models
- Status Codes corretos
- Tratamento de exceções
- OpenAPI automática

Nunca criar endpoints fora do SPEC.

---

# Frontend

Utilizar:

- React
- Vite
- TailwindCSS

Não adicionar bibliotecas sem necessidade.

Manter componentes pequenos.

---

# RAG

Sempre seguir o fluxo:

Documento

↓

Chunk

↓

Embedding

↓

Busca Vetorial

↓

Contexto

↓

LLM

↓

Resposta

Nunca responder utilizando conhecimento externo.

Caso não exista contexto suficiente responder:

```
Não encontrei informações suficientes para responder essa pergunta.
```

---

# n8n

Não gerar workflows automaticamente.

Durante a Sprint 05 apenas auxiliar na construção do fluxo.

Nunca substituir a implementação manual do workflow.

---

# Docker

Todo serviço deverá funcionar através do Docker Compose.

Nunca assumir execução local fora do container.

Sempre utilizar variáveis de ambiente.

---

# Variáveis de Ambiente

Nunca escrever segredos no código.

Sempre utilizar:

```
.env
```

Sempre atualizar:

```
.env.example
```

quando novas variáveis forem criadas.

---

# Testes

Sempre que possível:

- criar testes unitários;
- manter testes próximos ao código;
- utilizar pytest.

Caso não seja possível implementar testes durante a Sprint, informar isso explicitamente.

---

# Documentação

Sempre atualizar README quando houver:

- novos endpoints;
- novas dependências;
- novas variáveis;
- mudanças no fluxo de instalação.

Nunca deixar documentação desatualizada.

---

# Restrições

Nunca:

- adicionar autenticação antes da Sprint prevista;
- implementar painel administrativo;
- adicionar Redis;
- adicionar observabilidade;
- adicionar cache;
- adicionar funcionalidades não previstas.

---

# Qualidade

Todo código deverá:

- possuir responsabilidade única;
- utilizar nomes claros;
- evitar duplicação;
- evitar comentários desnecessários;
- evitar código morto.

Preferir simplicidade.

---

# Ao concluir cada tarefa

Sempre responder neste formato:

## Funcionalidade implementada

Breve resumo.

---

## Arquivos criados

Lista.

---

## Arquivos modificados

Lista.

---

## Como validar

Passos para testar.

---

## Commit sugerido

```
feat: descrição da funcionalidade
```

---

## Próxima funcionalidade recomendada

Informar qual é o próximo item da Sprint.

Aguardar confirmação antes de continuar.

---

# Filosofia

Este projeto tem finalidade educacional e de portfólio.

O objetivo principal não é entregar o maior número de funcionalidades.

O objetivo é demonstrar boas práticas de engenharia de software.

Sempre priorizar:

- código limpo;
- arquitetura consistente;
- commits pequenos;
- documentação completa;
- evolução incremental.
