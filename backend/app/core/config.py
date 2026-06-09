from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

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

    MAIL_FROM: str = ""
    MAIL_FROM_NAME: str = ""
    SMTP_HOST: str = "mailpit"
    SMTP_PORT: int = 1025
    MAILPIT_UI_PORT: int = 8025

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"

    OTP_EXPIRATION_MINUTES: int = 2 if ENVIRONMENT == "local" else 5
    LOGIN_ATTEMPTS: int = 3
    LOGOUT_DURATION_MINUTES: int = 2 if ENVIRONMENT == "local" else 5
    ACTIVATION_TOKEN_EXPIRATION_MINUTES: int = 2 if ENVIRONMENT == "local" else 5
    API_BASE_URL: str = ""
    SUPPORT_EMAIL: str = ""
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRATION_MINUTES: int = 30 if ENVIRONMENT == "local" else 15
    JWT_REFRESH_TOKEN_EXPIRATION_DAYS: int = 1
    COOKIE_SECURE: bool = False if ENVIRONMENT == "local" else True
    COOKIE_ACCESS_NAME: str = "access_token"
    COOKIE_REFRESH_NAME: str = "refresh_token"
    COOKIE_LOGGED_IN_NAME: str = "logged_in"
    # ? means that the cookie cannot be accessed by js running in the browser
    # ? this prevenst cross-site scripting attacks
    COOKIE_HTTP_ONLY: bool = True
    # ? this specifies whether the cookie should be sent with requests to the same site
    # ? lax -> this cookie is gonna be sent with request to the same site, but not with requests to subdomains
    COOKIE_SAMESITE: str = "lax"
    # ? cookie is gonna be available for the specified path and its above
    # ? / -> the cookie is gonna be available for the root path and its sub-paths
    COOKIE_PATH: str = "/"
    # ? use to sign JWT tokens to make them tamper resistant
    SIGNING_KEY: str = ""


settings = Settings()
