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
    def __init__(self, content: bytes) -> None:
        self.content = content

    def raise_for_status(self) -> None:
        return None


class FakeClient:
    def __init__(self, responses: dict[str, bytes]) -> None:
        self.responses = responses

    async def get(self, url: str) -> FakeResponse:
        if url not in self.responses:
            raise httpx.ConnectError("source unavailable")
        return FakeResponse(self.responses[url])


class FakeClientContext:
    def __init__(self, responses: dict[str, bytes]) -> None:
        self.responses = responses

    async def __aenter__(self) -> FakeClient:
        return FakeClient(self.responses)

    async def __aexit__(self, *args: object) -> None:
        return None


class FakeSession:
    def __init__(self, existing_urls: set[str]) -> None:
        self.existing_urls = existing_urls
        self.added: list[News] = []
        self.committed = False

    async def scalars(self, stmt: object) -> list[str]:
        return list(self.existing_urls)

    def add(self, news: News) -> None:
        self.added.append(news)

    async def commit(self) -> None:
        self.committed = True


def _patch_http(monkeypatch: pytest.MonkeyPatch, responses: dict[str, bytes]) -> None:
    monkeypatch.setattr(
        "app.rss.sync.httpx.AsyncClient",
        lambda **kwargs: FakeClientContext(responses),
    )


async def test_sync_news_creates_and_skips_duplicates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = {source.url: FEED for source in SOURCES}
    _patch_http(monkeypatch, responses)
    session = FakeSession(existing_urls={"https://example.com/dup"})

    summary = await sync_news(session=session)

    assert summary.sources == 3
    assert summary.articles == 9
    assert summary.created == 2
    assert summary.skipped == 7
    assert summary.errors == 0
    assert session.committed
    assert len(session.added) == 2
    assert {news.title for news in session.added} == {"Novo artigo", "Sem conteudo"}


async def test_sync_news_tolerates_source_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_http(monkeypatch, {SOURCES[0].url: FEED})
    session = FakeSession(existing_urls=set())

    summary = await sync_news(session=session)

    assert summary.sources == 3
    assert summary.articles == 3
    assert summary.created == 3
    assert summary.errors == 2
    assert session.committed
