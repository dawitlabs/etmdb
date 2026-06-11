from datetime import UTC, datetime

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel

from app.models.credit import Credit
from app.models.genre import Genre, MovieGenre
from app.models.youtube_link import YouTubeLink


class MovieBase(SQLModel):
    title: str = Field(index=True, max_length=500)
    original_title: str | None = Field(default=None, max_length=500)
    slug: str = Field(unique=True, index=True, max_length=300)
    overview: str | None = None
    poster_url: str | None = None
    backdrop_url: str | None = None
    release_date: str | None = None
    release_year: int | None = Field(default=None, index=True)
    runtime: int | None = None
    spoken_languages: list[str] = Field(default=[], sa_column=Column(JSON, default=[]))
    countries: list[str] = Field(default=[], sa_column=Column(JSON, default=[]))
    tmdb_id: int | None = Field(default=None, unique=True, index=True)
    imdb_id: str | None = Field(default=None, unique=True, index=True)
    wikidata_id: str | None = Field(default=None, unique=True)
    wikipedia_url: str | None = None
    source: str | None = None
    tmdb_rating: float | None = None
    tmdb_votes: int | None = None
    type: str = Field(default="movie", index=True)  # "movie" | "series"


class Movie(MovieBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    genres: list[Genre] = Relationship(back_populates="movies", link_model=MovieGenre)
    credits: list[Credit] = Relationship(back_populates="movie")
    youtube_links: list[YouTubeLink] = Relationship(back_populates="movie")
