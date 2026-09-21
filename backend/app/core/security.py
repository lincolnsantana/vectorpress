import time
from collections import defaultdict, deque
from hmac import compare_digest

from fastapi import Header, HTTPException, Request, status

from app.core.config import settings


async def require_sync_token(
    x_sync_token: str = Header(default=""),
) -> None:
    """Protege a ingestao quando SYNC_TOKEN esta configurado."""
    if not settings.sync_token:
        return
    if not compare_digest(x_sync_token, settings.sync_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de sincronizacao invalido.",
        )


def client_ip(request: Request) -> str:
    """IP real do cliente, considerando o proxy do tunel na frente da API."""
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "desconhecido"


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int) -> None:
        self._limit = limit
        self._window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, now: float | None = None) -> bool:
        moment = time.monotonic() if now is None else now
        cutoff = moment - self._window
        hits = self._hits[key]
        while hits and hits[0] <= cutoff:
            hits.popleft()
        if not hits:
            # evita acumular chaves de IPs que pararam de chamar
            self._hits.pop(key, None)
            hits = self._hits[key]
        if len(hits) >= self._limit:
            return False
        hits.append(moment)
        return True


_ask_limiter = SlidingWindowLimiter(
    limit=settings.ask_rate_limit,
    window_seconds=settings.ask_rate_window_seconds,
)


async def enforce_ask_rate_limit(request: Request) -> None:
    """Limita chamadas ao /ask por IP; ASK_RATE_LIMIT=0 desativa."""
    if settings.ask_rate_limit <= 0:
        return
    if not _ask_limiter.allow(client_ip(request)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas perguntas em sequencia. Tente novamente em instantes.",
            headers={"Retry-After": str(settings.ask_rate_window_seconds)},
        )
