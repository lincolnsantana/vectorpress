import uuid

from app.rag.chunker import Chunk, Chunker

NEWS_ID = uuid.UUID("12345678-1234-5678-1234-567812345678")


def test_split_short_content_returns_single_chunk() -> None:
    chunks = Chunker().split(NEWS_ID, "Texto curto.")

    assert len(chunks) == 1
    assert chunks[0] == Chunk(news_id=NEWS_ID, text="Texto curto.", position=0)


def test_split_long_content_returns_multiple_ordered_chunks() -> None:
    content = " ".join(["palavra" * 100] * 100)
    chunks = Chunker().split(NEWS_ID, content)

    assert len(chunks) > 1
    assert [chunk.position for chunk in chunks] == list(range(len(chunks)))
    assert all(chunk.news_id == NEWS_ID for chunk in chunks)
    assert all(chunk.text for chunk in chunks)


def test_split_empty_content_returns_no_chunks() -> None:
    chunks = Chunker().split(NEWS_ID, "")

    assert chunks == []
