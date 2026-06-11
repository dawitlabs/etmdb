from pydantic import BaseModel, ConfigDict


class FilmographyEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    movie_id: int
    movie_title: str
    movie_slug: str
    movie_poster_url: str | None
    role: str
    character_name: str | None
    release_year: int | None


class PersonPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    name_am: str | None
    slug: str
    photo_url: str | None


class PersonDetail(BaseModel):
    id: int
    name: str
    name_am: str | None
    slug: str
    photo_url: str | None
    bio: str | None
    tmdb_id: int | None
    filmography: list[FilmographyEntry]
