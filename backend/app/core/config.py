import secrets

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_name: str
    db_host: str = "db"
    db_port: int = 5432

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3003"]

    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    redis_host: str = "localhost"
    redis_port: int = 6379

    groq_api_key: str = ""
    demo_data: bool = False

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_login_attempts: int = 5
    rate_limit_login_window_seconds: int = 300

    # Password policy
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digit: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def _generate_secret_key(self) -> "Settings":
        if not self.secret_key:
            self.secret_key = secrets.token_urlsafe(32)
        return self

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()