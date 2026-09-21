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
        "published_at": None,
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


async def test_ask_deduplicates_sources_by_url(
    client: httpx.AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    same_url = "https://example.com/mesmo-artigo"
    context = [make_chunk(url=same_url), make_chunk(url=same_url, title="Outro título")]

    class FakeService:
        async def ask(self, session: object, question: str) -> tuple[str, list[RetrievedChunk]]:
            return "Resposta.", context

    app.dependency_overrides[get_session] = FakeSession
    app.dependency_overrides[rag_api.get_rag_service] = lambda: FakeService()
    try:
        response = await client.post("/ask", json={"question": "O que houve?"})
    finally:
        app.dependency_overrides.pop(get_session, None)
        app.dependency_overrides.pop(rag_api.get_rag_service, None)

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Resposta."
    assert [source["url"] for source in data["sources"]] == [same_url]


async def test_ask_maps_llm_provider_error_to_502(
    client: httpx.AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    response = httpx.Response(
        404,
        request=request,
        json={"error": {"message": "The model `x` does not exist"}},
    )

    class FakeService:
        async def ask(self, session: object, question: str) -> tuple[str, list[RetrievedChunk]]:
            raise httpx.HTTPStatusError("404", request=request, response=response)

    app.dependency_overrides[get_session] = FakeSession
    app.dependency_overrides[rag_api.get_rag_service] = lambda: FakeService()
    try:
        result = await client.post("/ask", json={"question": "O que houve?"})
    finally:
        app.dependency_overrides.pop(get_session, None)
        app.dependency_overrides.pop(rag_api.get_rag_service, None)

    assert result.status_code == 502
    assert "404" in result.json()["detail"]
    assert "does not exist" in result.json()["detail"]


async def test_ask_maps_llm_connection_error_to_504(
    client: httpx.AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeService:
        async def ask(self, session: object, question: str) -> tuple[str, list[RetrievedChunk]]:
            raise httpx.ConnectTimeout("timeout")

    app.dependency_overrides[get_session] = FakeSession
    app.dependency_overrides[rag_api.get_rag_service] = lambda: FakeService()
    try:
        result = await client.post("/ask", json={"question": "O que houve?"})
    finally:
        app.dependency_overrides.pop(get_session, None)
        app.dependency_overrides.pop(rag_api.get_rag_service, None)

    assert result.status_code == 504
