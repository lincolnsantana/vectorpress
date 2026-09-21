from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_sync_token
from app.database.connection import get_session
from app.database.models import News
from app.rag.indexer import index_news
from app.rss.sync import sync_news
from app.schemas.news import NewsDetailOut, NewsListItem, NewsListOut, SyncResponse
from app.utils.helpers import make_summary

router = APIRouter(prefix="/news", tags=["news"])


@router.post(
    "/sync",
    response_model=SyncResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_sync_token)],
)
async def sync_news_endpoint() -> SyncResponse:
    summary = await sync_news()
    indexed = await index_news()
    return SyncResponse(
        sources=summary.sources,
        articles=summary.articles,
        created=summary.created,
        skipped=summary.skipped,
        errors=summary.errors,
        indexed=indexed,
    )


@router.get("", response_model=NewsListOut)
async def list_news(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> NewsListOut:
    total = await session.scalar(select(func.count()).select_from(News))
    result = await session.scalars(
        select(News)
        .order_by(News.published_at.desc().nullslast(), News.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    items = result.all()
    return NewsListOut(
        items=[
            NewsListItem(
                id=item.id,
                title=item.title,
                url=item.url,
                source=item.source,
                author=item.author,
                image_url=item.image_url,
                summary=make_summary(item.content),
                published_at=item.published_at,
                created_at=item.created_at,
            )
            for item in items
        ],
        total=total or 0,
        limit=limit,
        offset=offset,
    )


@router.get("/{news_id}", response_model=NewsDetailOut)
async def get_news(
    news_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> NewsDetailOut:
    news = await session.get(News, news_id)
    if news is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notícia não encontrada",
        )
    return news
