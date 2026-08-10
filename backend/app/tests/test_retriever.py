import uuid

from app.rag.retriever import RetrievedChunk, Retriever


class Row:
    def __init__(self, *values: object) -> None:
        self._values = values

    def __getitem__(self, index: int) -> object:
        return self._values[index]


class Result:
    def __init__(self, rows: list[Row]) -> None:
        self._rows = rows

    def all(self) -> list[Row]:
        return self._rows


class FakeSession:
    def __init__(self, rows: list[Row]) -> None:
        self.rows = rows
        self.executed_statement: object | None = None

    async def execute(self, statement: object) -> Result:
        self.executed_statement = statement
        limit = getattr(statement, "_limit", None)
        rows = self.rows[:limit] if limit else self.rows
        return Result(rows)


def make_row(**overrides: object) -> Row:
    values: dict[str, object] = {
        "chunk_id": uuid.uuid4(),
        "text": "Fragmento relevante.",
        "news_id": uuid.uuid4(),
        "title": "Notícia de teste",
        "url": "https://example.com/artigo",
        "source": "OpenAI Blog",
    }
    values.update(overrides)
    return Row(
        values["chunk_id"],
        values["text"],
        values["news_id"],
        values["title"],
        values["url"],
        values["source"],
    )


async def test_retrieve_returns_ranked_chunks() -> None:
    rows = [make_row(), make_row(text="Segundo fragmento.")]
    session = FakeSession(rows)

    results = await Retriever().retrieve(session, [0.1] * 384)

    assert len(results) == 2
    assert all(isinstance(item, RetrievedChunk) for item in results)
    assert results[0].title == "Notícia de teste"
    assert results[0].url == "https://example.com/artigo"
    assert results[0].source == "OpenAI Blog"


async def test_retrieve_applies_top_k_limit() -> None:
    session = FakeSession([make_row() for _ in range(5)])

    results = await Retriever(top_k=3).retrieve(session, [0.1] * 384)

    assert len(results) == 3


async def test_retrieve_returns_empty_when_no_matches() -> None:
    session = FakeSession([])

    results = await Retriever().retrieve(session, [0.1] * 384)

    assert results == []
