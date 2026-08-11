import uuid

import pytest

from app.rag.generator import Generator, SYSTEM_PROMPT
from app.rag.retriever import RetrievedChunk


def make_chunk(**overrides: object) -> RetrievedChunk:
    values: dict[str, object] = {
        "chunk_id": uuid.uuid4(),
        "text": "Anthropic anunciou um novo modelo.",
        "news_id": uuid.uuid4(),
        "title": "Anthropic lança modelo",
        "url": "https://www.anthropic.com/news/model",
        "source": "Anthropic Blog",
        "published_at": None,
    }
    values.update(overrides)
    return RetrievedChunk(**values)  # type: ignore[arg-type]


class FakeResponse:
    def __init__(self, content: str) -> None:
        self._content = content

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return {"choices": [{"message": {"content": self._content}}]}


async def test_generate_returns_no_context_message() -> None:
    generator = Generator(api_key="test-key", model="llama3-8b-8192")

    answer = await generator.generate("O que é IA?", [])

    assert answer == "Não encontrei informações suficientes para responder esta pergunta."


async def test_generate_calls_llm_with_context(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.rag.generator as generator_module

    captured: dict[str, object] = {}

    async def fake_post(self: object, url: str, **kwargs: object) -> FakeResponse:
        captured["url"] = url
        captured["headers"] = kwargs.get("headers")
        captured["body"] = kwargs.get("json")
        return FakeResponse("Resposta baseada no contexto.")

    monkeypatch.setattr(generator_module.httpx.AsyncClient, "post", fake_post)

    generator = Generator(api_key="test-key", model="llama3-8b-8192")
    context = [make_chunk()]

    answer = await generator.generate("Qual modelo foi anunciado?", context)

    assert answer == "Resposta baseada no contexto."
    assert captured["url"] == "https://api.groq.com/openai/v1/chat/completions"
    body = captured["body"]
    assert isinstance(body, dict)
    assert body["model"] == "llama3-8b-8192"
    assert body["messages"][0]["content"] == SYSTEM_PROMPT
    user_content = body["messages"][1]["content"]
    assert isinstance(user_content, str)
    assert "https://www.anthropic.com/news/model" in user_content
    assert "Título: Anthropic lança modelo" in user_content
    assert "Anthropic Blog" in user_content
    assert "Cite as fontes utilizadas" not in user_content
