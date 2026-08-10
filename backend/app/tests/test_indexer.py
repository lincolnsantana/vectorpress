import uuid
from datetime import datetime, timezone

import pytest

from app.database.models import News
from app.rag.indexer import index_news


def make_news(**overrides: object) -> News:
    values: dict[str, object] = {
        "id": uuid.uuid4(),
        "title": "Notícia de teste",
        "url": "https://example.com/artigo",
        "source": "OpenAI Blog",
        "author": None,
        "content": "Conteúdo " + "com palavras repetidas " * 200,
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
    def __init__(self, news_without_chunks: list[News]) -> None:
        self.news_without_chunks = news_without_chunks
        self.added_chunks: list[object] = []
        self.added_embeddings: list[object] = []
        self.committed = False

    async def scalars(self, stmt: object) -> ScalarResult:
        return ScalarResult(self.news_without_chunks)

    def add_all(self, items: list[object]) -> None:
        from app.database.models import Chunk, Embedding

        for item in items:
            if isinstance(item, Chunk):
                self.added_chunks.append(item)
            elif isinstance(item, Embedding):
                self.added_embeddings.append(item)

    async def flush(self) -> None:
        from app.database.models import Chunk

        for chunk in self.added_chunks:
            if chunk.id is None:
                chunk.id = uuid.uuid4()

    async def commit(self) -> None:
        self.committed = True

    async def close(self) -> None:
        return None


async def test_index_news_indexes_news_without_chunks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    news = make_news()
    session = FakeSession([news])

    def fake_provider() -> object:
        class FakeProvider:
            async def embed(self, texts: list[str]) -> list[list[float]]:
                return [[0.1] * 384 for _ in texts]

        return FakeProvider()

    monkeypatch.setattr("app.rag.indexer.get_embeddings_provider", fake_provider)

    indexed = await index_news(session=session)

    assert indexed == 1
    assert len(session.added_chunks) > 0
    assert len(session.added_embeddings) == len(session.added_chunks)
    assert session.committed


async def test_index_news_skips_empty_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession([make_news(content="")])

    monkeypatch.setattr(
        "app.rag.indexer.get_embeddings_provider",
        lambda: None,
    )

    indexed = await index_news(session=session)

    assert indexed == 0
    assert session.added_chunks == []
    assert session.added_embeddings == []
    assert session.committed


async def test_index_news_skips_when_no_pending_news(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession([])

    indexed = await index_news(session=session)

    assert indexed == 0
    assert session.committed
