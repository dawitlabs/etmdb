from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ETMDB_")

    database_url: str = "sqlite+aiosqlite:///./etmdb.db"
    api_key_salt: str = "change-me-in-production"
    cors_origins: list[str] = ["http://localhost:3000"]
    rate_limit_per_day: int = 1000
    debug: bool = False


settings = Settings()
