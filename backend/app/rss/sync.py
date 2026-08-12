from dataclasses import dataclass

import httpx
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

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
