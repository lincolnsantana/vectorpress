from datetime import datetime, timezone

from app.rss.parser import extract_og_image, parse_feed
from app.rss.sources import Source

SOURCE = Source(name="Test Blog", url="https://example.com/rss")

RSS_WITH_ITEMS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
  <channel>
    <title>Test Blog</title>
    <item>
      <title>Primeiro artigo</title>
      <link>https://example.com/one</link>
      <description>Resumo do primeiro artigo</description>
      <author>John Doe</author>
      <pubDate>Wed, 01 Jan 2025 10:00:00 GMT</pubDate>
      <media:content url="https://example.com/one/image.jpg" medium="image"/>
    </item>
    <item>
      <title>Segundo artigo</title>
      <link>https://example.com/two</link>
      <pubDate>Thu, 02 Jan 2025 11:30:00 GMT</pubDate>
      <description><![CDATA[<p>Texto do artigo</p><img src="https://example.com/two/cover.png"/><p>Fim</p>]]></description>
    </item>
    <item>
      <link>https://example.com/sem-titulo</link>
    </item>
  </channel>
</rss>
"""

EMPTY_FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Empty</title></channel></rss>
"""


def test_parse_feed_extracts_articles() -> None:
    articles = parse_feed(RSS_WITH_ITEMS, SOURCE)

    assert len(articles) == 2

    first = articles[0]
    assert first.title == "Primeiro artigo"
    assert first.url == "https://example.com/one"
    assert first.source == "Test Blog"
    assert first.author == "John Doe"
    assert first.content == "Resumo do primeiro artigo"
    assert first.published_at == datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
    assert first.image_url == "https://example.com/one/image.jpg"


def test_parse_feed_handles_missing_metadata() -> None:
    articles = parse_feed(RSS_WITH_ITEMS, SOURCE)

    second = articles[1]
    assert second.author is None
    assert second.content == "<p>Texto do artigo</p><img src=\"https://example.com/two/cover.png\"/><p>Fim</p>"
    assert second.image_url == "https://example.com/two/cover.png"
    assert second.published_at == datetime(2025, 1, 2, 11, 30, tzinfo=timezone.utc)


def test_parse_feed_skips_entries_without_title() -> None:
    articles = parse_feed(RSS_WITH_ITEMS, SOURCE)

    assert all(article.title for article in articles)
    assert len(articles) == 2


def test_parse_feed_empty_feed_returns_no_articles() -> None:
    assert parse_feed(EMPTY_FEED, SOURCE) == []


def test_extract_og_image_finds_meta_tag() -> None:
    html = (
        '<html><head><meta property="og:title" content="Titulo"/>'
        '<meta property="og:image" content="https://example.com/cover.jpg"/>'
        "</head></html>"
    )

    assert extract_og_image(html) == "https://example.com/cover.jpg"


def test_extract_og_image_finds_url_variant() -> None:
    html = '<meta property="og:image:url" content="https://example.com/alt.jpg"/>'

    assert extract_og_image(html) == "https://example.com/alt.jpg"


def test_extract_og_image_returns_none_when_missing() -> None:
    html = "<html><head><title>Sem imagem</title></head></html>"

    assert extract_og_image(html) is None
