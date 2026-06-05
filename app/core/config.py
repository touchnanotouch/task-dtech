from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    debug: bool = True

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/payment_api"
    )

    jwt_secret: str = "dev-jwt-secret-key-change-in-production!"
    webhook_secret: str = "dev-webhook-secret-key-change-in-production!"

    jwt_expiration_hours: int = 24
