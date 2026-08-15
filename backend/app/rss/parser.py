from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser

import feedparser

from app.rss.sources import Source


@dataclass(slots=True)
class RawArticle:
    title: str
    url: str
    source: str
    author: str | None
    content: str | None
    image_url: str | None
    published_at: datetime | None


def parse_feed(feed_content: bytes, source: Source) -> list[RawArticle]:
    feed = feedparser.parse(feed_content)
    return [article for entry in feed.entries if (article := _to_article(entry, source))]


def _to_article(entry: feedparser.FeedParserDict, source: Source) -> RawArticle | None:
    title = _clean(entry.get("title"))
    url = _clean(entry.get("link"))
    if not title or not url:
        return None
    return RawArticle(
        title=title,
        url=url,
        source=source.name,
        author=_extract_author(entry),
        content=_extract_content(entry),
        image_url=_extract_image(entry),
        published_at=_extract_published_at(entry),
    )


def _extract_image(entry: feedparser.FeedParserDict) -> str | None:
    media = entry.get("media_content") or entry.get("media_thumbnail")
    if media:
        for item in media:
            url = item.get("url")
            if url:
                return url
    for enclosure in entry.get("enclosures") or []:
        if enclosure.get("type", "").startswith("image"):
            url = enclosure.get("href") or enclosure.get("url")
            if url:
                return url
    content = _extract_content(entry)
    if content:
        return _first_image_url(content)
    return None


def _first_image_url(html: str) -> str | None:
    class ImageFinder(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.src: str | None = None

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            if self.src is not None or tag != "img":
                return
            self.src = dict(attrs).get("src")

    finder = ImageFinder()
    finder.feed(html)
    return finder.src


def _clean(value: object) -> str:
    return str(value).strip() if value is not None else ""


def _extract_author(entry: feedparser.FeedParserDict) -> str | None:
    if entry.get("author"):
        return entry["author"]
    authors = entry.get("authors") or []
    if authors and authors[0].get("name"):
        return authors[0]["name"]
    return None


def _extract_content(entry: feedparser.FeedParserDict) -> str | None:
    content = entry.get("content")
    if content:
        return content[0].get("value")
    return entry.get("summary")


def _extract_published_at(entry: feedparser.FeedParserDict) -> datetime | None:
    published = entry.get("published_parsed") or entry.get("updated_parsed")
    if published is None:
        return None
    return datetime(*published[:6], tzinfo=timezone.utc)
