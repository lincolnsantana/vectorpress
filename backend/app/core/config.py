from dataclasses import dataclass, field
from os import getenv


def parse_csv_env(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = getenv("APP_NAME", "Vectorpress")
    app_env: str = getenv("APP_ENV", "development")
    log_level: str = getenv("LOG_LEVEL", "INFO")
    database_url: str = getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://vectorpress:vectorpress@postgres:5432/vectorpress",
    )
    postgres_db: str = getenv("POSTGRES_DB", "vectorpress")
    postgres_user: str = getenv("POSTGRES_USER", "vectorpress")
    postgres_password: str = getenv("POSTGRES_PASSWORD", "vectorpress")
    postgres_port: int = int(getenv("POSTGRES_PORT", "5432"))
    embedding_provider: str = getenv("EMBEDDING_PROVIDER", "local")
    embedding_model: str = getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    openai_api_key: str = getenv("OPENAI_API_KEY", "")
    llm_provider: str = getenv("LLM_PROVIDER", "groq")
    llm_model: str = getenv("LLM_MODEL", "qwen/qwen3.8-27b")
    groq_api_key: str = getenv("GROQ_API_KEY", "")
    rag_max_age_days: int = int(getenv("RAG_MAX_AGE_DAYS", "3"))
    news_retention_days: int = int(getenv("NEWS_RETENTION_DAYS", "7"))
    telegram_token: str = getenv("TELEGRAM_TOKEN", "")
    telegram_webhook_url: str = getenv("TELEGRAM_WEBHOOK_URL", "")
    sync_token: str = getenv("SYNC_TOKEN", "")
    ask_rate_limit: int = int(getenv("ASK_RATE_LIMIT", "10"))
    ask_rate_window_seconds: int = int(getenv("ASK_RATE_WINDOW_SECONDS", "60"))
    cors_allowed_origins: list[str] = field(
        default_factory=lambda: parse_csv_env(getenv("CORS_ALLOWED_ORIGINS", ""))
    )


settings = Settings()
