from dataclasses import dataclass
from uuid import UUID

from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass(frozen=True, slots=True)
class Chunk:
    news_id: UUID
    text: str
    position: int


class Chunker:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def split(self, news_id: UUID, content: str) -> list[Chunk]:
        parts = self._splitter.split_text(content)
        return [
            Chunk(news_id=news_id, text=part, position=index)
            for index, part in enumerate(parts)
        ]
