from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.core.enums import LanguageEnum

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        case_sensitive=False,
        extra="ignore"
    )
    database_url: str
    redis_url: str

    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    jwt_refresh_token_expire_days: int

    default_language: LanguageEnum

    upload_root: str = "static"
    max_image_size_mb: int = 5

settings = Settings()

