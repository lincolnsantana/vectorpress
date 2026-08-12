from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.rag.retriever import RetrievedChunk

SYSTEM_PROMPT = (
    "Você é um assistente que responde perguntas sobre notícias recentes de "
    "Inteligência Artificial. Responda APENAS usando o contexto fornecido. "
    "Responda de forma natural e conversacional, em texto corrido, como uma pessoa "
    "explicando a notícia a um amigo. "
    "Não liste as notícias uma a uma como um catálogo. "
    "Sintetize: responda de forma breve e direta o que for relevante para a pergunta. "
    "Se a pergunta pedir novidades, mencione os temas principais (com a data, se útil) "
    "em um ou dois parágrafos curtos. "
    "Quando citar uma fonte, faça de forma natural no texto (ex.: \"segundo o "
    "TechCrunch\"). As URLs das fontes são exibidas separadamente, então não as "
    "repita na resposta. "
    "Se o contexto for insuficiente para responder, diga: "
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
        today = datetime.now(timezone.utc).strftime("%d/%m/%Y")
        user_prompt = (
            f"Data de hoje: {today}\n\n"
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
                    "max_tokens": 400,
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
