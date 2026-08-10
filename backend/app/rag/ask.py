from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.embeddings import EmbeddingsProvider
from app.rag.generator import Generator
from app.rag.retriever import RetrievedChunk, Retriever


class RAGService:
    def __init__(
        self,
        embeddings: EmbeddingsProvider,
        retriever: Retriever,
        generator: Generator,
    ) -> None:
        self._embeddings = embeddings
        self._retriever = retriever
        self._generator = generator

    async def ask(self, session: AsyncSession, question: str) -> tuple[str, list[RetrievedChunk]]:
        query_embedding = (await self._embeddings.embed([question]))[0]
        context = await self._retriever.retrieve(session, query_embedding)
        answer = await self._generator.generate(question, context)
        return answer, context
