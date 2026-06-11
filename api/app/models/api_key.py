from datetime import UTC, date, datetime

from sqlmodel import Field, SQLModel


class APIKey(SQLModel, table=True):
    __tablename__ = "api_key"

    id: int | None = Field(default=None, primary_key=True)
    key_hash: str = Field(unique=True, index=True)
    key_prefix: str = Field(max_length=8)
    name: str = Field(max_length=200)
    email: str = Field(index=True, max_length=300)
    rate_limit: int = Field(default=1000)
    requests_today: int = Field(default=0)
    last_reset: date = Field(default_factory=lambda: datetime.now(UTC).date())
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
