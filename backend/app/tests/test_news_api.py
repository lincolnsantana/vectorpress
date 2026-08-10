import uuid
from datetime import datetime, timezone

import httpx
import pytest

import app.api.news as news_api
from app.database.connection import get_session
from app.database.models import News
from app.main import app
from app.rss.sync import SyncSummary


def make_news(**overrides: object) -> News:
    values: dict[str, object] = {
        "id": uuid.uuid4(),
        "title": "Notícia de teste",
        "url": "https://example.com/artigo",
        "source": "OpenAI Blog",
        "author": None,
        "content": "Conteúdo completo do artigo.",
        "published_at": datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc),
        "created_at": datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc),
    }
    values.update(overrides)
    return News(**values)  # type: ignore[arg-type]


class ScalarResult:
    def __init__(self, items: list[News]) -> None:
        self._items = items

    def all(self) -> list[News]:
        return self._items


class FakeSession:
    def __init__(self, items: list[News]) -> None:
        self.items = items

    async def scalar(self, stmt: object) -> int:
        return len(self.items)

    async def scalars(self, stmt: object) -> ScalarResult:
        return ScalarResult(self.items)

    async def get(self, model: object, news_id: uuid.UUID) -> News | None:
        return next((item for item in self.items if item.id == news_id), None)


@pytest.fixture
def news_items() -> list[News]:
    return [
        make_news(),
        make_news(url="https://example.com/segundo", title="Segunda notícia"),
    ]


@pytest.fixture
async def client() -> httpx.AsyncClient:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


async def test_list_news(client: httpx.AsyncClient, news_items: list[News]) -> None:
    session = FakeSession(news_items)
    app.dependency_overrides[get_session] = lambda: session
    try:
        response = await client.get("/news")
    finally:
        app.dependency_overrides.pop(get_session, None)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["limit"] == 20
    assert data["offset"] == 0


async def test_get_news_returns_detail(
    client: httpx.AsyncClient,
    news_items: list[News],
) -> None:
    session = FakeSession(news_items)
    app.dependency_overrides[get_session] = lambda: session
    try:
        response = await client.get(f"/news/{news_items[0].id}")
    finally:
        app.dependency_overrides.pop(get_session, None)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(news_items[0].id)
    assert data["title"] == news_items[0].title
    assert data["content"] == news_items[0].content


async def test_get_news_not_found(
    client: httpx.AsyncClient,
    news_items: list[News],
) -> None:
    session = FakeSession(news_items)
    app.dependency_overrides[get_session] = lambda: session
    try:
        response = await client.get(f"/news/{uuid.uuid4()}")
    finally:
        app.dependency_overrides.pop(get_session, None)

    assert response.status_code == 404


async def test_sync_news_endpoint(
    client: httpx.AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_sync() -> SyncSummary:
        return SyncSummary(sources=3, articles=10, created=8, skipped=1, errors=1)

    async def fake_index() -> int:
        return 5

    monkeypatch.setattr(news_api, "sync_news", fake_sync)
    monkeypatch.setattr(news_api, "index_news", fake_index)

    response = await client.post("/news/sync")

    assert response.status_code == 200
    data = response.json()
    assert data["sources"] == 3
    assert data["created"] == 8
    assert data["skipped"] == 1
    assert data["errors"] == 1
    assert data["indexed"] == 5
