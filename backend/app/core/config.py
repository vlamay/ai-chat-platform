from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_chat"
    )

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Chat Platform"
    VERSION: str = "1.0.0"
    # Debug mode - True if DEBUG env var is set OR if not on Railway
    DEBUG: bool = os.getenv("DEBUG", "").lower() in ("true", "1") or "railway" not in os.getenv("RAILWAY_ENVIRONMENT_NAME", "").lower()

    # Server
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # Claude API
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Sentry
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")

    # Redis Caching
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # CORS
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost,http://127.0.0.1:3000,http://127.0.0.1:5173,https://ai-chat-platform-liard.vercel.app"
    ).split(",")

    class Config:
        env_file = ".env"


settings = Settings()
