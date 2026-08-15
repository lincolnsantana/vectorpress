from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NewsListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    url: str
    source: str
    author: str | None
    image_url: str | None = None
    summary: str = ""
    published_at: datetime | None
    created_at: datetime


class NewsDetailOut(NewsListItem):
    content: str


class NewsListOut(BaseModel):
    items: list[NewsListItem]
    total: int
    limit: int
    offset: int


class SyncResponse(BaseModel):
    sources: int
    articles: int
    created: int
    skipped: int
    errors: int
    indexed: int
