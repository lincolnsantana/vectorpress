from app.rss.sources import SOURCES


def test_sources_contains_expected_feeds() -> None:
    names = {source.name for source in SOURCES}
    assert names == {
        "OpenAI Blog",
        "Anthropic Blog",
        "TechCrunch AI",
        "Google AI Blog",
        "DeepMind Blog",
        "Microsoft AI Blog",
        "MIT Tech Review AI",
        "The Verge AI",
        "Hugging Face Blog",
        "Meta AI Blog",
        "VentureBeat AI",
        "Wired AI",
        "404 Media AI",
    }


def test_sources_have_valid_urls() -> None:
    assert all(source.url.startswith("https://") for source in SOURCES)
