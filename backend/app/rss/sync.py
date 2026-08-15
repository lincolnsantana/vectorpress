from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.connection import async_session
from app.database.models import News
from app.rss.parser import RawArticle, extract_og_image, parse_feed
from app.rss.sources import SOURCES


@dataclass(slots=True)
class SyncSummary:
    sources: int
    articles: int
    created: int
    updated: int
    skipped: int
    errors: int


async def sync_news(session: AsyncSession | None = None) -> SyncSummary:
    owns_session = session is None
    session = session or async_session()
    try:
        active_sources = {source.name for source in SOURCES}
        await session.execute(
            delete(News).where(News.source.not_in(active_sources))
        )
        if settings.news_retention_days > 0:
            cutoff_retention = datetime.now(timezone.utc) - timedelta(
                days=settings.news_retention_days
            )
            await session.execute(
                delete(News).where(
                    func.coalesce(News.published_at, News.created_at) < cutoff_retention
                )
            )
        existing = {
            news.url: news
            for news in (await session.scalars(select(News))).all()
        }
        summary = SyncSummary(
            sources=len(SOURCES),
            articles=0,
            created=0,
            updated=0,
            skipped=0,
            errors=0,
        )
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0), follow_redirects=True) as client:
            for source in SOURCES:
                try:
                    response = await client.get(source.url)
                    response.raise_for_status()
                    for article in parse_feed(response.content, source):
                        summary.articles += 1
                        news = existing.get(article.url)
                        if news is not None:
                            summary.skipped += 1
                            if news.image_url is None:
                                image_url = await _resolve_image(client, article)
                                if image_url is not None:
                                    news.image_url = image_url
                                    summary.updated += 1
                            continue
                        image_url = await _resolve_image(client, article)
                        news = News(
                            title=article.title,
                            url=article.url,
                            source=article.source,
                            author=article.author,
                            content=article.content or "",
                            image_url=image_url,
                            published_at=article.published_at,
                        )
                        existing[article.url] = news
                        summary.created += 1
                        session.add(news)
                except httpx.HTTPError:
                    summary.errors += 1
        await session.commit()
        return summary
    finally:
        if owns_session:
            await session.close()


async def _resolve_image(client: httpx.AsyncClient, article: RawArticle) -> str | None:
    if article.image_url:
        return article.image_url
    try:
        response = await client.get(article.url)
        response.raise_for_status()
        return extract_og_image(response.text)
    except httpx.HTTPError:
        return None
