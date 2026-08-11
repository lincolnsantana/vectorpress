from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.rag.ask import RAGService
from app.rag.embeddings import get_embeddings_provider
from app.rag.generator import get_generator
from app.rag.retriever import Retriever
from app.schemas.rag import AskRequest, AskResponse, SourceOut

router = APIRouter(tags=["rag"])


def get_rag_service() -> RAGService:
    return RAGService(
        embeddings=get_embeddings_provider(),
        retriever=Retriever(),
        generator=get_generator(),
    )


@router.post("/ask", response_model=AskResponse)
async def ask_question(
    payload: AskRequest,
    session: AsyncSession = Depends(get_session),
    service: RAGService = Depends(get_rag_service),
) -> AskResponse:
    answer, context = await service.ask(session, payload.question)
    sources: list[SourceOut] = []
    seen_urls: set[str] = set()
    for chunk in context:
        if chunk.url in seen_urls:
            continue
        seen_urls.add(chunk.url)
        sources.append(
            SourceOut(title=chunk.title, url=chunk.url, source=chunk.source)
        )
    return AskResponse(answer=answer, sources=sources)
