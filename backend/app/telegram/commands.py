from collections.abc import Sequence
from datetime import datetime
from math import ceil

from sqlalchemy import func, select
from telegram import Update
from telegram.ext import ContextTypes

from app.api.rag import get_rag_service
from app.database.connection import async_session
from app.database.models import News
from app.rag.retriever import RetrievedChunk
from app.schemas.news import NewsListItem

PAGE_SIZE = 10


def format_news_item(
    index: int,
    title: str,
    source: str,
    url: str,
    published_at: datetime | None,
) -> str:
    date = published_at.strftime("%d/%m/%Y %H:%M") if published_at else ""
    meta = " · ".join(filter(None, [source, date]))
    return f"{index}. {title}\n{meta}\n{url}"


def format_today(news: Sequence[NewsListItem]) -> str:
    if not news:
        return "Ainda não há notícias cadastradas."
    items = [
        format_news_item(index, item.title, item.source, item.url, item.published_at)
        for index, item in enumerate(news, start=1)
    ]
    return "Últimas notícias de hoje\n\n" + "\n\n".join(items)


def format_list(
    news: Sequence[NewsListItem],
    page: int,
    total_pages: int,
) -> str:
    if not news:
        return "Não há notícias nesta página."
    items = [
        format_news_item(index, item.title, item.source, item.url, item.published_at)
        for index, item in enumerate(news, start=1)
    ]
    footer = (
        f"\n\nPágina {page} de {total_pages}. Use /list {page + 1} para ver a próxima."
        if page < total_pages
        else ""
    )
    return f"Notícias recentes (página {page})\n\n" + "\n\n".join(items) + footer


def format_ask(
    answer: str,
    chunks: Sequence[RetrievedChunk],
) -> str:
    parts = [answer]
    sources: list[str] = []
    seen_urls: set[str] = set()
    for chunk in chunks:
        if chunk.url in seen_urls:
            continue
        seen_urls.add(chunk.url)
        sources.append(f"- {chunk.title}\n  {chunk.url}")
    if sources:
        parts += ["", "Fontes:", *sources]
    return "\n".join(parts)


def parse_page(args: list[str] | None) -> int:
    if not args:
        return 1
    try:
        page = int(args[0])
    except ValueError:
        return 1
    return max(1, page)


async def fetch_news(limit: int, offset: int = 0) -> tuple[int, list[NewsListItem]]:
    async with async_session() as session:
        total = await session.scalar(select(func.count()).select_from(News))
        result = await session.scalars(
            select(News)
            .order_by(News.published_at.desc().nullslast(), News.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        items = [NewsListItem.model_validate(item) for item in result.all()]
        return total or 0, items


async def today_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    _, news = await fetch_news(limit=5)
    await update.message.reply_text(format_today(news))


async def list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    page = parse_page(context.args)
    total, news = await fetch_news(limit=PAGE_SIZE, offset=(page - 1) * PAGE_SIZE)
    total_pages = max(1, ceil(total / PAGE_SIZE))
    await update.message.reply_text(format_list(news, page, total_pages))


async def ask_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    message = update.message
    if not context.args:
        await message.reply_text(
            "Use /ask seguido da sua pergunta. Exemplo:\n/ask Quais as novidades de IA?"
        )
        return
    question = " ".join(context.args)
    try:
        service = get_rag_service()
        async with async_session() as session:
            answer, chunks = await service.ask(session, question)
        text = format_ask(answer, chunks)
    except Exception:
        text = "Desculpe, não consegui processar sua pergunta agora. Tente novamente mais tarde."
    await message.reply_text(text)
