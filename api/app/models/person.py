from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel

from app.models.credit import Credit


class PersonBase(SQLModel):
    name: str = Field(index=True, max_length=300)
    name_am: str | None = Field(default=None, max_length=300)
    slug: str = Field(unique=True, index=True, max_length=300)
    photo_url: str | None = None
    bio: str | None = None
    tmdb_id: int | None = Field(default=None, unique=True)


class Person(PersonBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    credits: list[Credit] = Relationship(back_populates="person")
