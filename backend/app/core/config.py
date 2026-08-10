from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = getenv("APP_NAME", "AI Pulse")
    app_env: str = getenv("APP_ENV", "development")
    log_level: str = getenv("LOG_LEVEL", "INFO")
    database_url: str = getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://ai_pulse:ai_pulse@postgres:5432/ai_pulse",
    )
    postgres_db: str = getenv("POSTGRES_DB", "ai_pulse")
    postgres_user: str = getenv("POSTGRES_USER", "ai_pulse")
    postgres_password: str = getenv("POSTGRES_PASSWORD", "ai_pulse")
    postgres_port: int = int(getenv("POSTGRES_PORT", "5432"))
    embedding_provider: str = getenv("EMBEDDING_PROVIDER", "local")
    embedding_model: str = getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    openai_api_key: str = getenv("OPENAI_API_KEY", "")
    llm_provider: str = getenv("LLM_PROVIDER", "groq")
    llm_model: str = getenv("LLM_MODEL", "llama3-8b-8192")
    groq_api_key: str = getenv("GROQ_API_KEY", "")


settings = Settings()
