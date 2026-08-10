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
    Source(name="Google AI Blog", url="https://feeds.feedburner.com/blogspot/gJZg"),
    Source(name="DeepMind Blog", url="https://deepmind.google/blog/rss.xml"),
    Source(
        name="Microsoft AI Blog",
        url="https://blogs.microsoft.com/ai/feed/",
    ),
    Source(
        name="MIT Tech Review AI",
        url="https://www.technologyreview.com/topic/artificial-intelligence/feed",
    ),
    Source(
        name="The Verge AI",
        url="https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    ),
    Source(name="Hugging Face Blog", url="https://huggingface.co/blog/feed.xml"),
    Source(name="Meta AI Blog", url="https://ai.meta.com/blog/rss/"),
    Source(name="arXiv cs.AI", url="https://export.arxiv.org/rss/cs.AI"),
    Source(
        name="VentureBeat AI",
        url="https://venturebeat.com/category/ai/feed/",
    ),
    Source(name="Wired AI", url="https://www.wired.com/feed/tag/ai/latest/rss"),
    Source(name="404 Media AI", url="https://www.404media.co/tag/ai/rss"),
)
