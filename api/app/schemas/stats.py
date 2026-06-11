from pydantic import BaseModel


class StatsResponse(BaseModel):
    total_movies: int
    total_people: int
    total_youtube_links: int
    total_genres: int
    movies_with_posters: int
    movies_with_youtube: int
