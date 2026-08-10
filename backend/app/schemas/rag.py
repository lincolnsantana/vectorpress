from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class SourceOut(BaseModel):
    title: str
    url: str
    source: str


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceOut]
