from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.connection import async_session
from app.database.models import News
from app.rss.parser import parse_feed
from app.rss.sources import SOURCES


@dataclass(slots=True)
class SyncSummary:
    sources: int
    articles: int
    created: int
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
        existing_urls = set(await session.scalars(select(News.url)))
        summary = SyncSummary(
            sources=len(SOURCES),
            articles=0,
            created=0,
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
                        if article.url in existing_urls:
                            summary.skipped += 1
                            continue
                        existing_urls.add(article.url)
                        summary.created += 1
                        session.add(
                            News(
                                title=article.title,
                                url=article.url,
                                source=article.source,
                                author=article.author,
                                content=article.content or "",
                                image_url=article.image_url,
                                published_at=article.published_at,
                            )
                        )
                except httpx.HTTPError:
                    summary.errors += 1
        await session.commit()
        return summary
    finally:
        if owns_session:
            await session.close()
