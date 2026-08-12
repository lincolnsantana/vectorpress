from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Chunk, Embedding, News


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    chunk_id: UUID
    text: str
    news_id: UUID
    title: str
    url: str
    source: str
    published_at: datetime | None


class Retriever:
    def __init__(self, top_k: int = 5, max_age_days: int | None = None) -> None:
        self._top_k = top_k
        self._max_age_days = max_age_days

    async def retrieve(
        self,
        session: AsyncSession,
        query_embedding: list[float],
    ) -> list[RetrievedChunk]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=self._max_age_days or 0)
        statement = (
            select(
                Chunk.id,
                Chunk.chunk,
                News.id,
                News.title,
                News.url,
                News.source,
                News.published_at,
            )
            .join(Embedding, Embedding.chunk_id == Chunk.id)
            .join(News, News.id == Chunk.news_id)
            .where(
                func.coalesce(News.published_at, News.created_at) >= cutoff
            )
            .order_by(Embedding.embedding.cosine_distance(query_embedding))
            .limit(self._top_k)
        )
        rows = (await session.execute(statement)).all()
        return [
            RetrievedChunk(
                chunk_id=row[0],
                text=row[1],
                news_id=row[2],
                title=row[3],
                url=row[4],
                source=row[5],
                published_at=row[6],
            )
            for row in rows
        ]
