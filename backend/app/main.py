from collections.abc import AsyncIterator
import logging

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.news import router as news_router
from app.api.rag import router as rag_router
from app.api.telegram import router as telegram_router
from app.core.config import settings
from app.database.connection import dispose_engine, engine
from app.database.models import Base
from app.telegram.bot import get_application, shutdown_application

logger = logging.getLogger(__name__)


async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    try:
        await get_application()
    except Exception:
        logger.warning("Bot Telegram indisponível: verifique TELEGRAM_TOKEN.", exc_info=True)
    yield
    await shutdown_application()
    await dispose_engine()


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "AI Pulse API"}


app.include_router(health_router)
app.include_router(news_router)
app.include_router(rag_router)
app.include_router(telegram_router)
