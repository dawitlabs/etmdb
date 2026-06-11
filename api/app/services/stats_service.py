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
        total_movies = await self._count(Movie)
        total_people = await self._count(Person)
        total_youtube = await self._count(YouTubeLink)
        total_genres = await self._count(Genre)

        poster_result = await self.session.execute(
            select(func.count()).where(Movie.poster_url.is_not(None))
        )
        movies_with_posters = poster_result.scalar_one()

        yt_result = await self.session.execute(
            select(func.count(func.distinct(YouTubeLink.movie_id))).where(
                YouTubeLink.movie_id.is_not(None)
            )
        )
        movies_with_youtube = yt_result.scalar_one()

        return StatsResponse(
            total_movies=total_movies,
            total_people=total_people,
            total_youtube_links=total_youtube,
            total_genres=total_genres,
            movies_with_posters=movies_with_posters,
            movies_with_youtube=movies_with_youtube,
        )

    async def _count(self, model) -> int:
        result = await self.session.execute(select(func.count()).select_from(model))
        return result.scalar_one()
