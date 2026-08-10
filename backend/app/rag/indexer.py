from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import async_session
from app.database.models import Chunk, Embedding, News
from app.rag.chunker import Chunker
from app.rag.embeddings import EmbeddingsProvider, get_embeddings_provider


async def index_news(session: AsyncSession | None = None) -> int:
    owns_session = session is None
    session = session or async_session()
    chunker = Chunker()
    provider = get_embeddings_provider()
    indexed = 0
    try:
        news_without_chunks = await session.scalars(
            select(News)
            .outerjoin(Chunk)
            .where(Chunk.id.is_(None))
            .order_by(News.created_at)
        )
        for news in news_without_chunks.all():
            pieces = chunker.split(news.id, news.content or "")
            if not pieces:
                continue
            chunks = [
                Chunk(news_id=piece.news_id, chunk=piece.text, position=piece.position)
                for piece in pieces
            ]
            session.add_all(chunks)
            await session.flush()
            embeddings = await provider.embed([chunk.chunk for chunk in chunks])
            session.add_all(
                [
                    Embedding(chunk_id=chunk.id, embedding=vector)
                    for chunk, vector in zip(chunks, embeddings, strict=True)
                ]
            )
            indexed += 1
        await session.commit()
        return indexed
    finally:
        if owns_session:
            await session.close()
