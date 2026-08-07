from app.rss.sources import SOURCES


def test_sources_contains_expected_feeds() -> None:
    names = {source.name for source in SOURCES}
    assert names == {"OpenAI Blog", "Anthropic Blog", "TechCrunch AI"}


def test_sources_have_valid_urls() -> None:
    assert all(source.url.startswith("https://") for source in SOURCES)
