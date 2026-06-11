from sqlmodel import Field, Relationship, SQLModel


class MovieGenre(SQLModel, table=True):
    __tablename__ = "movie_genre"

    movie_id: int = Field(foreign_key="movie.id", primary_key=True)
    genre_id: int = Field(foreign_key="genre.id", primary_key=True)


class Genre(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=100)
    name_am: str | None = Field(default=None, max_length=100)
    slug: str = Field(unique=True, max_length=100)

    movies: list["Movie"] = Relationship(  # noqa: F821
        back_populates="genres", link_model=MovieGenre
    )
