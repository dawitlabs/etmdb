from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.genre import Genre
from app.models.movie import Movie
from app.models.person import Person
from app.models.youtube_link import YouTubeLink
from app.schemas.stats import StatsResponse


class StatsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_stats(self) -> StatsResponse:
        total_movies = await self._count_where(Movie.type == "movie")
        total_series = await self._count_where(Movie.type == "series")
        total_people = await self._scalar(select(func.count()).select_from(Person))
        total_youtube = await self._scalar(select(func.count()).select_from(YouTubeLink))
        total_genres = await self._scalar(select(func.count()).select_from(Genre))

        movies_with_posters = await self._count_where(Movie.poster_url.is_not(None))

        yt_result = await self.session.execute(
            select(func.count(func.distinct(YouTubeLink.movie_id))).where(YouTubeLink.movie_id.is_not(None))
        )
        movies_with_youtube = yt_result.scalar_one()

        movies_with_ratings = await self._count_where(
            (Movie.tmdb_rating.is_not(None)) & (Movie.tmdb_rating > 0)
        )

        return StatsResponse(
            total_titles=total_movies + total_series,
            total_movies=total_movies,
            total_series=total_series,
            total_people=total_people,
            total_youtube_links=total_youtube,
            total_genres=total_genres,
            movies_with_posters=movies_with_posters,
            movies_with_youtube=movies_with_youtube,
            movies_with_ratings=movies_with_ratings,
        )

    async def _count_where(self, condition) -> int:
        result = await self.session.execute(select(func.count()).where(condition).select_from(Movie))
        return result.scalar_one()

    async def _scalar(self, stmt) -> int:
        result = await self.session.execute(stmt)
        return result.scalar_one()
