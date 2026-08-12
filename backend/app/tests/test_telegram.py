import uuid
from datetime import datetime, timezone

import httpx
import pytest

import app.api.telegram as telegram_api
import app.telegram.bot as bot
import app.telegram.commands as commands
from app.main import app
from app.rag.retriever import RetrievedChunk
from app.schemas.news import NewsListItem
from telegram import Bot, Update
from telegram.error import InvalidToken


def make_item(title: str = "Notícia de teste") -> NewsListItem:
    published = datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc)
    return NewsListItem(
        id=uuid.uuid4(),
        title=title,
        url="https://example.com/artigo",
        source="OpenAI Blog",
        author=None,
        published_at=published,
        created_at=published,
    )


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


class FakeMessage:
    def __init__(self, text: str = "") -> None:
        self.text = text
        self.sent: list[str] = []

    async def reply_text(self, text: str) -> None:
        self.sent.append(text)


class FakeUpdate:
    def __init__(self, message: FakeMessage | None = None) -> None:
        self.message = message


class FakeContext:
    def __init__(self, args: list[str] | None = None) -> None:
        self.args = args


class FakeRAGService:
    def __init__(
        self,
        answer: str = "Resposta baseada nas notícias.",
        chunks: list[RetrievedChunk] | None = None,
    ) -> None:
        self._answer = answer
        self._chunks = chunks or []
        self.called_question: str | None = None

    async def ask(self, session: object, question: str) -> tuple[str, list[RetrievedChunk]]:
        self.called_question = question
        return self._answer, self._chunks


def test_format_today_returns_empty_message() -> None:
    assert commands.format_today([]) == "Ainda não há notícias cadastradas."


def test_format_today_lists_headlines() -> None:
    text = commands.format_today([make_item(f"Notícia {i}") for i in range(5)])

    assert text.startswith("Últimas notícias de hoje")
    assert "1. Notícia 0" in text
    assert "5. Notícia 4" in text
    assert "OpenAI Blog" in text
    assert "https://example.com/artigo" in text


def test_format_list_returns_empty_page_message() -> None:
    assert commands.format_list([], page=1, total_pages=1) == "Não há notícias nesta página."


def test_format_list_mentions_next_page() -> None:
    text = commands.format_list([make_item()], page=1, total_pages=3)

    assert text.startswith("Notícias recentes (página 1)")
    assert "Use /list 2 para ver a próxima." in text


def test_format_list_omits_footer_on_last_page() -> None:
    text = commands.format_list([make_item()], page=3, total_pages=3)

    assert "Use /list" not in text


def test_format_ask_includes_answer_and_sources() -> None:
    text = commands.format_ask("Resposta.", [make_chunk()])

    assert text.startswith("Resposta.")
    assert "Pergunta:" not in text
    assert "Fontes:" in text
    assert "https://example.com/artigo" in text


def test_format_ask_deduplicates_sources_by_url() -> None:
    same_url = "https://example.com/artigo"
    chunks = [make_chunk(), make_chunk(title="Outro título")]

    text = commands.format_ask("Resposta.", chunks)

    assert text.count(same_url) == 1
    assert text.count("Notícia de teste") == 1


def test_parse_page_defaults_to_one() -> None:
    assert commands.parse_page(None) == 1
    assert commands.parse_page([]) == 1
    assert commands.parse_page(["abc"]) == 1
    assert commands.parse_page(["0"]) == 1


def test_parse_page_parses_requested_page() -> None:
    assert commands.parse_page(["3"]) == 3


async def test_today_handler_replies_with_headlines(monkeypatch: pytest.MonkeyPatch) -> None:
    items = [make_item(f"Notícia {i}") for i in range(5)]

    async def fake_fetch(limit: int, offset: int = 0) -> tuple[int, list[NewsListItem]]:
        assert limit == 5
        return len(items), items

    monkeypatch.setattr(commands, "fetch_news", fake_fetch)
    message = FakeMessage()

    await commands.today_handler(FakeUpdate(message), FakeContext())

    assert message.sent[-1].startswith("Últimas notícias de hoje")
    assert "1. Notícia 0" in message.sent[-1]


async def test_today_handler_replies_empty_message(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_fetch(limit: int, offset: int = 0) -> tuple[int, list[NewsListItem]]:
        return 0, []

    monkeypatch.setattr(commands, "fetch_news", fake_fetch)
    message = FakeMessage()

    await commands.today_handler(FakeUpdate(message), FakeContext())

    assert message.sent[-1] == "Ainda não há notícias cadastradas."


async def test_list_handler_uses_requested_page(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[int, int]] = []

    async def fake_fetch(limit: int, offset: int = 0) -> tuple[int, list[NewsListItem]]:
        calls.append((limit, offset))
        return 25, [make_item() for _ in range(10)]

    monkeypatch.setattr(commands, "fetch_news", fake_fetch)
    message = FakeMessage()

    await commands.list_handler(FakeUpdate(message), FakeContext(["2"]))

    assert calls == [(10, 10)]
    text = message.sent[-1]
    assert text.startswith("Notícias recentes (página 2)")
    assert "Use /list 3 para ver a próxima." in text


async def test_list_handler_defaults_to_first_page(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[int, int]] = []

    async def fake_fetch(limit: int, offset: int = 0) -> tuple[int, list[NewsListItem]]:
        calls.append((limit, offset))
        return 5, [make_item() for _ in range(5)]

    monkeypatch.setattr(commands, "fetch_news", fake_fetch)
    message = FakeMessage()

    await commands.list_handler(FakeUpdate(message), FakeContext())

    assert calls == [(10, 0)]


async def test_ask_handler_asks_with_question_and_sources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = FakeRAGService(chunks=[make_chunk()])
    monkeypatch.setattr(commands, "get_rag_service", lambda: service)
    message = FakeMessage()

    await commands.ask_handler(FakeUpdate(message), FakeContext(["Quais", "novidades", "de", "IA?"]))

    assert service.called_question == "Quais novidades de IA?"
    text = message.sent[-1]
    assert "Resposta baseada nas notícias." in text
    assert "Fontes:" in text
    assert "https://example.com/artigo" in text


async def test_ask_handler_without_question_returns_usage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def fake_service() -> FakeRAGService:
        nonlocal called
        called = True
        return FakeRAGService()

    monkeypatch.setattr(commands, "get_rag_service", fake_service)
    message = FakeMessage()

    await commands.ask_handler(FakeUpdate(message), FakeContext())

    assert not called
    assert message.sent[-1].startswith("Use /ask seguido da sua pergunta.")


async def test_ask_handler_replies_gracefully_on_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class BrokenService:
        async def ask(self, session: object, question: str) -> tuple[str, list[RetrievedChunk]]:
            raise RuntimeError("llm falhou")

    monkeypatch.setattr(commands, "get_rag_service", lambda: BrokenService())
    message = FakeMessage()

    await commands.ask_handler(FakeUpdate(message), FakeContext(["pergunta"]))

    assert message.sent[-1] == (
        "Desculpe, não consegui processar sua pergunta agora. Tente novamente mais tarde."
    )


def test_build_application_registers_commands(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeSettings:
        telegram_token = "123456789:" + "A" * 35

    monkeypatch.setattr(bot, "settings", FakeSettings())

    application = bot.build_application()

    commands_registered = {command for handler in application.handlers[0] for command in handler.commands}
    assert commands_registered == {"today", "list", "ask"}


def test_build_application_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeSettings:
        telegram_token = ""

    monkeypatch.setattr(bot, "settings", FakeSettings())

    with pytest.raises(InvalidToken):
        bot.build_application()


@pytest.fixture
async def client() -> httpx.AsyncClient:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


class FakeApplication:
    def __init__(self) -> None:
        self.bot = Bot(token="123456789:" + "A" * 35)
        self.processed: list[Update] = []

    async def process_update(self, update: Update) -> None:
        self.processed.append(update)


async def test_webhook_returns_ok_when_bot_configured(
    client: httpx.AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = FakeApplication()

    async def configured_application() -> FakeApplication:
        return fake

    monkeypatch.setattr(telegram_api, "get_application", configured_application)

    response = await client.post(
        "/telegram/webhook",
        json={
            "update_id": 1,
            "message": {
                "message_id": 1,
                "date": 1784000000,
                "text": "/today",
                "chat": {"id": 1, "type": "private"},
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert len(fake.processed) == 1


async def test_webhook_returns_503_when_bot_not_configured(
    client: httpx.AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def no_application() -> None:
        return None

    monkeypatch.setattr(telegram_api, "get_application", no_application)

    response = await client.post("/telegram/webhook", json={"update_id": 1})

    assert response.status_code == 503
    assert response.json() == {"ok": False, "detail": "Bot não configurado"}
