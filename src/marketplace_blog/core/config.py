from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Marketplace Blog API"
    environment: str = "local"
    debug: bool = True

    database_url: str

    mail_host: str
    mail_port: int
    mail_username: str
    mail_password: str
    mail_from: str

    test_database_url: str = "postgresql+asyncpg://marketplace:marketplace@127.0.0.1:5433/marketplace_blog_test"

    rabbitmq_url: str

    minio_endpoint_url: str = "http://localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "blog-images"
    minio_public_url: str = "http://localhost:9000/blog-images"

    secret_key: str = "change-me-before-production"
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"
    auth_cookie_name: str = "access_token"


@lru_cache
def get_settings() -> Settings:
    return Settings()
