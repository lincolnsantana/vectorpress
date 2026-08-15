import httpx
import pytest

from app.database.models import News
from app.rss.sources import SOURCES
from app.rss.sync import sync_news

FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <item><title>Novo artigo</title><link>https://example.com/new</link></item>
  <item><title>Artigo duplicado</title><link>https://example.com/dup</link></item>
  <item><title>Sem conteudo</title><link>https://example.com/nc</link></item>
</channel></rss>
"""


class FakeResponse:
    def __init__(self, content: bytes, text: str = "") -> None:
        self.content = content
        self.text = text

    def raise_for_status(self) -> None:
        return None


class FakeClient:
    def __init__(self, responses: dict[str, bytes], pages: dict[str, str] | None = None) -> None:
        self.responses = responses
        self.pages = pages or {}

    async def get(self, url: str, timeout: httpx.Timeout | None = None) -> FakeResponse:
        if url in self.pages:
            return FakeResponse(b"", self.pages[url])
        if url not in self.responses:
            raise httpx.ConnectError("source unavailable")
        return FakeResponse(self.responses[url])


class FakeClientContext:
    def __init__(
        self,
        responses: dict[str, bytes],
        pages: dict[str, str] | None = None,
    ) -> None:
        self.responses = responses
        self.pages = pages

    async def __aenter__(self) -> FakeClient:
        return FakeClient(self.responses, self.pages)

    async def __aexit__(self, *args: object) -> None:
        return None


class FakeSession:
    def __init__(self, existing_news: list[News]) -> None:
        self.existing_news = existing_news
        self.added: list[News] = []
        self.committed = False
        self.executed: list[object] = []

    async def scalars(self, stmt: object) -> object:
        return _ScalarResult(self.existing_news)

    async def execute(self, stmt: object) -> None:
        self.executed.append(stmt)

    def add(self, news: News) -> None:
        self.added.append(news)

    async def commit(self) -> None:
        self.committed = True


class _ScalarResult:
    def __init__(self, items: list[News]) -> None:
        self._items = items

    def all(self) -> list[News]:
        return list(self._items)


def _patch_http(
    monkeypatch: pytest.MonkeyPatch,
    responses: dict[str, bytes],
    pages: dict[str, str] | None = None,
) -> None:
    monkeypatch.setattr(
        "app.rss.sync.httpx.AsyncClient",
        lambda **kwargs: FakeClientContext(responses, pages),
    )


async def test_sync_news_purges_removed_sources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_http(monkeypatch, {SOURCES[0].url: FEED})
    session = FakeSession(existing_news=[])

    await sync_news(session=session)

    delete_statements = [str(stmt) for stmt in session.executed if str(stmt).startswith("DELETE")]
    assert len(delete_statements) >= 2


async def test_sync_news_creates_and_skips_duplicates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = {source.url: FEED for source in SOURCES}
    _patch_http(monkeypatch, responses)
    dup = News(title="Artigo duplicado", url="https://example.com/dup", source="Test Blog")
    session = FakeSession(existing_news=[dup])

    summary = await sync_news(session=session)

    assert summary.sources == len(SOURCES)
    assert summary.articles == len(SOURCES) * 3
    assert summary.created == 2
    assert summary.updated == 0
    assert summary.skipped == len(SOURCES) * 3 - 2
    assert summary.errors == 0
    assert session.committed
    assert len(session.added) == 2
    assert {news.title for news in session.added} == {"Novo artigo", "Sem conteudo"}


async def test_sync_news_tolerates_source_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_http(monkeypatch, {SOURCES[0].url: FEED})
    session = FakeSession(existing_news=[])

    summary = await sync_news(session=session)

    assert summary.sources == len(SOURCES)
    assert summary.articles == 3
    assert summary.created == 3
    assert summary.errors == len(SOURCES) - 1
    assert session.committed


async def test_sync_news_backfills_image_from_og_image(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = {source.url: FEED for source in SOURCES}
    pages = {
        "https://example.com/new": (
            '<html><head><meta property="og:image" '
            'content="https://example.com/new/cover.jpg"/></head></html>'
        )
    }
    _patch_http(monkeypatch, responses, pages)
    session = FakeSession(existing_news=[])

    summary = await sync_news(session=session)

    created = {news.url: news for news in session.added}
    assert summary.updated == 0
    assert summary.created == 3
    assert created["https://example.com/new"].image_url == (
        "https://example.com/new/cover.jpg"
    )
    assert created["https://example.com/dup"].image_url is None


async def test_sync_news_updates_image_of_existing_article(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = {source.url: FEED for source in SOURCES}
    _patch_http(monkeypatch, responses)
    existing = News(
        title="Artigo duplicado",
        url="https://example.com/dup",
        source="Test Blog",
        image_url=None,
    )
    session = FakeSession(existing_news=[existing])

    await sync_news(session=session)

    assert existing.image_url is None
    assert session.committed


async def test_sync_news_keeps_existing_image(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = {source.url: FEED for source in SOURCES}
    _patch_http(monkeypatch, responses)
    existing = News(
        title="Artigo duplicado",
        url="https://example.com/dup",
        source="Test Blog",
        image_url="https://example.com/dup/old.jpg",
    )
    session = FakeSession(existing_news=[existing])

    await sync_news(session=session)

    assert existing.image_url == "https://example.com/dup/old.jpg"
    assert session.committed