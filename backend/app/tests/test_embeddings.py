import pytest

from app.rag.embeddings import (
    LocalEmbeddingsProvider,
    OpenAIEmbeddingsProvider,
    get_embeddings_provider,
)
from app.core.config import settings


class FakeModel:
    def encode(self, texts: list[str]) -> list[object]:
        return [type("V", (), {"tolist": lambda self, t=t: [1.0] * 384})() for t in texts]


async def test_local_provider_embeds_texts() -> None:
    provider = LocalEmbeddingsProvider(model_name="fake")
    provider._model = FakeModel()

    vectors = await provider.embed(["texto um", "texto dois"])

    assert len(vectors) == 2
    assert all(len(vector) == 384 for vector in vectors)


async def test_local_provider_returns_empty_for_empty_input() -> None:
    provider = LocalEmbeddingsProvider(model_name="fake")

    vectors = await provider.embed([])

    assert vectors == []


async def test_openai_provider_embeds_texts(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {
                "data": [
                    {"embedding": [0.5] * 384},
                    {"embedding": [0.6] * 384},
                ]
            }

    async def fake_post(self: object, url: str, **kwargs: object) -> FakeResponse:
        return FakeResponse()

    import app.rag.embeddings as embeddings_module

    monkeypatch.setattr(embeddings_module.httpx.AsyncClient, "post", fake_post)

    provider = OpenAIEmbeddingsProvider(api_key="test-key", model="text-embedding-3-small")

    vectors = await provider.embed(["texto um", "texto dois"])

    assert len(vectors) == 2
    assert all(len(vector) == 384 for vector in vectors)


async def test_get_provider_returns_local_by_default() -> None:
    object.__setattr__(settings, "embedding_provider", "local")
    try:
        provider = get_embeddings_provider()
        assert isinstance(provider, LocalEmbeddingsProvider)
    finally:
        object.__setattr__(settings, "embedding_provider", "local")


async def test_get_provider_returns_openai() -> None:
    object.__setattr__(settings, "embedding_provider", "openai")
    try:
        provider = get_embeddings_provider()
        assert isinstance(provider, OpenAIEmbeddingsProvider)
    finally:
        object.__setattr__(settings, "embedding_provider", "local")
