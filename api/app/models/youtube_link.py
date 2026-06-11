from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class YouTubeLinkBase(SQLModel):
    video_id: str = Field(unique=True, index=True, max_length=20)
    title: str = Field(max_length=500)
    channel_title: str | None = None
    channel_id: str | None = None
    published_at: datetime | None = None
    duration_seconds: int | None = None
    view_count: int | None = None
    like_count: int | None = None
    thumbnail_url: str | None = None
    embeddable: bool = True
    language: str | None = None


class YouTubeLink(YouTubeLinkBase, table=True):
    __tablename__ = "youtube_link"

    id: int | None = Field(default=None, primary_key=True)
    movie_id: int | None = Field(default=None, foreign_key="movie.id", index=True)
    is_primary: bool = False
    match_confidence: float | None = None

    movie: "Movie" = Relationship(back_populates="youtube_links")  # noqa: F821
