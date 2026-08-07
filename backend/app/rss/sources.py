from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Source:
    name: str
    url: str


SOURCES: tuple[Source, ...] = (
    Source(name="OpenAI Blog", url="https://openai.com/blog/rss.xml"),
    Source(name="Anthropic Blog", url="https://www.anthropic.com/rss.xml"),
    Source(
        name="TechCrunch AI",
        url="https://techcrunch.com/category/artificial-intelligence/feed/",
    ),
)
