from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.core.config import settings


async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "AI Pulse API"}
