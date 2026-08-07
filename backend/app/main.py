from collections.abc import AsyncIterator

from fastapi import FastAPI


async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield


app = FastAPI(title="AI Pulse", lifespan=lifespan)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "AI Pulse API"}
