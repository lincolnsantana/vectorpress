import asyncio
from abc import ABC, abstractmethod
from functools import partial

import httpx

from app.core.config import settings


class EmbeddingsProvider(ABC):
    dimension: int

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    async def warmup(self) -> None:
        return None


class LocalEmbeddingsProvider(EmbeddingsProvider):
    def __init__(self, model_name: str) -> None:
        self._model_name = model_name
        self._model = None
        self.dimension = 384

    def _load_model(self) -> object:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
        return self._model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        model = self._load_model()
        loop = asyncio.get_running_loop()
        embeddings = await loop.run_in_executor(None, partial(model.encode, texts))
        return [vector.tolist() for vector in embeddings]

    async def warmup(self) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._load_model)


class OpenAIEmbeddingsProvider(EmbeddingsProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model
        self.dimension = 384

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"model": self._model, "input": texts},
            )
            response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]


_provider_cache: dict[tuple[str, str], EmbeddingsProvider] = {}


def get_embeddings_provider() -> EmbeddingsProvider:
    key = (settings.embedding_provider, settings.embedding_model)
    if key not in _provider_cache:
        if settings.embedding_provider == "openai":
            _provider_cache[key] = OpenAIEmbeddingsProvider(
                api_key=settings.openai_api_key,
                model=settings.embedding_model,
            )
        else:
            _provider_cache[key] = LocalEmbeddingsProvider(model_name=settings.embedding_model)
    return _provider_cache[key]
