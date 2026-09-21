import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import enforce_ask_rate_limit
from app.database.connection import get_session
from app.rag.ask import RAGService
from app.rag.embeddings import get_embeddings_provider
from app.rag.generator import get_generator
from app.rag.retriever import Retriever
from app.schemas.rag import AskRequest, AskResponse, SourceOut

logger = logging.getLogger(__name__)

router = APIRouter(tags=["rag"])


def _upstream_detail(exc: httpx.HTTPStatusError) -> str:
    """Mensagem curta do provedor, sem vazar corpo de resposta inteiro."""
    try:
        body = exc.response.json()
    except ValueError:
        return exc.response.text[:200]
    error = body.get("error")
    if isinstance(error, dict):
        return str(error.get("message", ""))[:200]
    return str(error or body)[:200]


def get_rag_service() -> RAGService:
    return RAGService(
        embeddings=get_embeddings_provider(),
        retriever=Retriever(max_age_days=settings.rag_max_age_days),
        generator=get_generator(),
    )


@router.post(
    "/ask",
    response_model=AskResponse,
    dependencies=[Depends(enforce_ask_rate_limit)],
)
async def ask_question(
    payload: AskRequest,
    session: AsyncSession = Depends(get_session),
    service: RAGService = Depends(get_rag_service),
) -> AskResponse:
    try:
        answer, context = await service.ask(session, payload.question)
    except httpx.HTTPStatusError as exc:
        detail = _upstream_detail(exc)
        logger.error(
            "provedor de LLM respondeu %s: %s", exc.response.status_code, detail
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Provedor de LLM respondeu {exc.response.status_code}: {detail}",
        ) from exc
    except httpx.RequestError as exc:
        logger.error("falha de conexao com o provedor de LLM: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Nao foi possivel contatar o provedor de LLM.",
        ) from exc
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
