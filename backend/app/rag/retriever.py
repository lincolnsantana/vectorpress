from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
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


class Retriever:
    def __init__(self, top_k: int = 5) -> None:
        self._top_k = top_k

    async def retrieve(
        self,
        session: AsyncSession,
        query_embedding: list[float],
    ) -> list[RetrievedChunk]:
        statement = (
            select(
                Chunk.id,
                Chunk.chunk,
                News.id,
                News.title,
                News.url,
                News.source,
            )
            .join(Embedding, Embedding.chunk_id == Chunk.id)
            .join(News, News.id == Chunk.news_id)
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
            )
            for row in rows
        ]
