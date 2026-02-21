from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://taskhive:taskhive@localhost:5432/taskhive"
    NEXTAUTH_SECRET: str = "dev-secret"
    ENCRYPTION_KEY: str = ""  # 64 hex chars = 32 bytes for AES-256-GCM
    CORS_ORIGINS: str = "http://localhost:3000"
    ENVIRONMENT: str = "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
