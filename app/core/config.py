"""Application configuration management using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    DATABASE_URL: str

    # Upstash Redis REST API Configuration
    UPSTASH_REDIS_REST_URL: str = ""
    UPSTASH_REDIS_REST_TOKEN: str = ""

    # JWT Configuration
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Application Configuration
    APP_NAME: str = "ChatAPI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Gmail SMTP Configuration (Free - No Credit Card!)
    SMTP_EMAIL: str = ""
    SMTP_PASSWORD: str = ""  # Gmail App Password

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
