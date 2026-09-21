from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Request

from app.core.security import (
    SlidingWindowLimiter,
    client_ip,
    require_sync_token,
)


def make_request(headers: dict[str, str], host: str = "10.0.0.1") -> Request:
    scope = {
        "type": "http",
        "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
        "client": (host, 12345),
    }
    return Request(scope)


def test_limiter_blocks_after_reaching_limit() -> None:
    limiter = SlidingWindowLimiter(limit=2, window_seconds=60)

    assert limiter.allow("ip", now=0.0) is True
    assert limiter.allow("ip", now=1.0) is True
    assert limiter.allow("ip", now=2.0) is False


def test_limiter_releases_after_window() -> None:
    limiter = SlidingWindowLimiter(limit=1, window_seconds=60)

    assert limiter.allow("ip", now=0.0) is True
    assert limiter.allow("ip", now=30.0) is False
    assert limiter.allow("ip", now=61.0) is True


def test_limiter_counts_each_key_separately() -> None:
    limiter = SlidingWindowLimiter(limit=1, window_seconds=60)

    assert limiter.allow("ip-a", now=0.0) is True
    assert limiter.allow("ip-b", now=0.0) is True
    assert limiter.allow("ip-a", now=0.0) is False


def test_client_ip_prefers_forwarded_header() -> None:
    request = make_request({"x-forwarded-for": "203.0.113.5, 10.0.0.9"})

    assert client_ip(request) == "203.0.113.5"


def test_client_ip_falls_back_to_peer() -> None:
    assert client_ip(make_request({})) == "10.0.0.1"


async def test_sync_token_is_optional_when_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.core.security.settings", SimpleNamespace(sync_token=""))

    assert await require_sync_token(x_sync_token="") is None


async def test_sync_token_rejects_wrong_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.core.security.settings", SimpleNamespace(sync_token="segredo")
    )

    with pytest.raises(HTTPException) as excinfo:
        await require_sync_token(x_sync_token="errado")

    assert excinfo.value.status_code == 401


async def test_sync_token_accepts_correct_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.core.security.settings", SimpleNamespace(sync_token="segredo")
    )

    assert await require_sync_token(x_sync_token="segredo") is None
