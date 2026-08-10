import uuid

import httpx
import pytest

import app.api.rag as rag_api
from app.database.connection import get_session
from app.main import app
from app.rag.retriever import RetrievedChunk


def make_chunk(**overrides: object) -> RetrievedChunk:
    values: dict[str, object] = {
        "chunk_id": uuid.uuid4(),
        "text": "Fragmento relevante.",
        "news_id": uuid.uuid4(),
        "title": "Notícia de teste",
        "url": "https://example.com/artigo",
        "source": "OpenAI Blog",
    }
    values.update(overrides)
    return RetrievedChunk(**values)  # type: ignore[arg-type]


class FakeSession:
    async def close(self) -> None:
        return None


@pytest.fixture
async def client() -> httpx.AsyncClient:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


async def test_ask_returns_answer_with_sources(
    client: httpx.AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = [make_chunk()]

    class FakeService:
        async def ask(self, session: object, question: str) -> tuple[str, list[RetrievedChunk]]:
            return "Resposta baseada nas notícias.", context

    app.dependency_overrides[get_session] = FakeSession
    app.dependency_overrides[rag_api.get_rag_service] = lambda: FakeService()
    try:
        response = await client.post(
            "/ask",
            json={"question": "O que houve com a IA?"},
        )
    finally:
        app.dependency_overrides.pop(get_session, None)
        app.dependency_overrides.pop(rag_api.get_rag_service, None)

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Resposta baseada nas notícias."
    assert len(data["sources"]) == 1
    assert data["sources"][0]["url"] == "https://example.com/artigo"
    assert data["sources"][0]["title"] == "Notícia de teste"
