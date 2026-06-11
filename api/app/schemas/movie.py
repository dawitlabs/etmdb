from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GenrePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    name_am: str | None
    slug: str


class CreditPublic(BaseModel):
    id: int
    person_id: int
    person_name: str
    person_slug: str
    role: str
    character_name: str | None
    sort_order: int | None


class YouTubeLinkBrief(BaseModel):
    video_id: str
    title: str
    channel_title: str | None
    published_at: datetime | None
    duration_seconds: int | None
    view_count: int | None
    thumbnail_url: str | None
    is_primary: bool


class MoviePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type: str
    title: str
    original_title: str | None
    slug: str
    overview: str | None
    poster_url: str | None
    backdrop_url: str | None
    release_year: int | None
    release_date: str | None
    runtime: int | None
    number_of_seasons: int | None
    number_of_episodes: int | None
    spoken_languages: list[str]
    countries: list[str]
    tmdb_rating: float | None
    tmdb_votes: int | None
    source: str | None


class MovieDetail(BaseModel):
    id: int
    type: str
    title: str
    original_title: str | None
    slug: str
    overview: str | None
    tagline: str | None
    status: str | None
    poster_url: str | None
    backdrop_url: str | None
    release_date: str | None
    release_year: int | None
    runtime: int | None
    number_of_seasons: int | None
    number_of_episodes: int | None
    spoken_languages: list[str]
    countries: list[str]
    tmdb_id: int | None
    imdb_id: str | None
    wikidata_id: str | None
    wikipedia_url: str | None
    source: str | None
    tmdb_rating: float | None
    tmdb_votes: int | None
    genres: list[GenrePublic]
    credits: list[CreditPublic]
    youtube_links: list[YouTubeLinkBrief]


class MultiSearchResponse(BaseModel):
    query: str
    movies: list[MoviePublic]
    series: list[MoviePublic]
    people: list
    total_results: int
