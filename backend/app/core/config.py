from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

# * points to src/
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".envs" / ".env.local"),
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = ""
    PROJECT_NAME: str = ""
    PROJECT_DESCRIPTION: str = ""
    SITE_NAME: str = ""
    DATABASE_URL: str = ""


settings = Settings()
