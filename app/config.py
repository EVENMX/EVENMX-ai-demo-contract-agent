from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openrouter_api_key: str | None = None
    openrouter_model: str = "openai/gpt-5-mini"
    google_drive_folder: str = "Contract_Reviews"
    telegram_bot_token: str | None = None
    telegram_boss_chat_id: str | None = None
    report_storage_dir: str = "reports"


@lru_cache
def get_settings() -> Settings:
    return Settings()

# Note: To reload settings after .env changes, restart the server
# or call: get_settings.cache_clear()
