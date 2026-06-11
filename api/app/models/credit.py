from sqlmodel import Field, Relationship, SQLModel


class Credit(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    movie_id: int = Field(foreign_key="movie.id", index=True)
    person_id: int = Field(foreign_key="person.id", index=True)
    role: str = Field(max_length=50)
    character_name: str | None = None
    sort_order: int = 0

    movie: "Movie" = Relationship(back_populates="credits")  # noqa: F821
    person: "Person" = Relationship(back_populates="credits")  # noqa: F821
