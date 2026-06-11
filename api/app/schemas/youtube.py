from datetime import datetime

from pydantic import BaseModel, ConfigDict


class YouTubeLinkPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    video_id: str
    title: str
    channel_title: str | None
    channel_id: str | None
    published_at: datetime | None
    duration_seconds: int | None
    view_count: int | None
    like_count: int | None
    thumbnail_url: str | None
    embeddable: bool
    language: str | None
    movie_id: int | None
    is_primary: bool
    match_confidence: float | None
