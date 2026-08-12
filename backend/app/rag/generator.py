import httpx

from app.core.config import settings
from app.rag.retriever import RetrievedChunk

SYSTEM_PROMPT = (
    "Você é um assistente especializado em notícias de Inteligência Artificial. "
    "Responda APENAS usando o contexto fornecido. "
    "Quando a pergunta buscar um tema específico, priorize os trechos mais recentes "
    "e as fontes mais relevantes ao tema solicitado. "
    "Se o contexto for insuficiente, diga: "
    "'Não encontrei informações suficientes para responder esta pergunta.' "
    "NÃO use conhecimento externo."
)


class Generator:
    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    @staticmethod
    def _format_source(chunk: RetrievedChunk) -> str:
        date = chunk.published_at.strftime("%d/%m/%Y %H:%M") if chunk.published_at else ""
        meta = " · ".join(filter(None, [chunk.source, date]))
        return f"Título: {chunk.title}\n{meta}\nURL: {chunk.url}\n{chunk.text}"

    async def generate(self, question: str, context: list[RetrievedChunk]) -> str:
        if not context:
            return "Não encontrei informações suficientes para responder esta pergunta."

        context_text = "\n\n".join(
            self._format_source(chunk) for chunk in context
        )
        user_prompt = (
            f"Contexto:\n{context_text}\n\n"
            f"Pergunta: {question}"
        )

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    **(
                        {"reasoning_effort": "none"}
                        if self._model.startswith("qwen/")
                        else {}
                    ),
                },
            )
            response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def get_generator() -> Generator:
    return Generator(api_key=settings.groq_api_key, model=settings.llm_model)
