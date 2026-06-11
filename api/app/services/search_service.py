from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.movie import Movie
from app.models.person import Person
from app.schemas.movie import MoviePublic, MultiSearchResponse
from app.schemas.pagination import PaginatedResponse
from app.schemas.person import PersonPublic


class SearchService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_media(
        self,
        query: str,
        media_type: str | None = None,
        page: int = 1,
        per_page: int = 20,
        year: int | None = None,
        language: str | None = None,
    ) -> PaginatedResponse[MoviePublic]:
        pattern = f"%{query}%"
        stmt = select(Movie).where(
            or_(
                Movie.title.ilike(pattern),
                Movie.original_title.ilike(pattern),
                Movie.overview.ilike(pattern),
            )
        )
        if media_type:
            stmt = stmt.where(Movie.type == media_type)
        if year:
            stmt = stmt.where(Movie.release_year == year)
        if language:
            stmt = stmt.where(Movie.spoken_languages.contains(language))

        stmt = stmt.order_by(Movie.tmdb_rating.desc().nulls_last())
        total = await self._count_movie(stmt)
        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        result = await self.session.execute(stmt)

        return PaginatedResponse.create(
            results=[MoviePublic.model_validate(m) for m in result.scalars().all()],
            total=total,
            page=page,
            per_page=per_page,
        )

    async def search_people(
        self,
        query: str,
        page: int = 1,
        per_page: int = 20,
    ) -> PaginatedResponse[PersonPublic]:
        pattern = f"%{query}%"
        stmt = select(Person).where(
            or_(Person.name.ilike(pattern), Person.name_am.ilike(pattern))
        ).order_by(Person.name.asc())

        total_result = await self.session.execute(
            select(func.count()).select_from(stmt.subquery())
        )
        total = total_result.scalar_one()

        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        result = await self.session.execute(stmt)

        return PaginatedResponse.create(
            results=[PersonPublic.model_validate(p) for p in result.scalars().all()],
            total=total,
            page=page,
            per_page=per_page,
        )

    async def multi_search(self, query: str, limit: int = 5) -> MultiSearchResponse:
        pattern = f"%{query}%"

        movie_stmt = (
            select(Movie)
            .where(Movie.type == "movie")
            .where(or_(Movie.title.ilike(pattern), Movie.original_title.ilike(pattern), Movie.overview.ilike(pattern)))
            .order_by(Movie.tmdb_rating.desc().nulls_last())
            .limit(limit)
        )
        series_stmt = (
            select(Movie)
            .where(Movie.type == "series")
            .where(or_(Movie.title.ilike(pattern), Movie.original_title.ilike(pattern), Movie.overview.ilike(pattern)))
            .order_by(Movie.tmdb_rating.desc().nulls_last())
            .limit(limit)
        )
        people_stmt = (
            select(Person)
            .where(or_(Person.name.ilike(pattern), Person.name_am.ilike(pattern)))
            .order_by(Person.name.asc())
            .limit(limit)
        )

        movies_res = await self.session.execute(movie_stmt)
        series_res = await self.session.execute(series_stmt)
        people_res = await self.session.execute(people_stmt)

        movies = [MoviePublic.model_validate(m) for m in movies_res.scalars().all()]
        series = [MoviePublic.model_validate(m) for m in series_res.scalars().all()]
        people = [PersonPublic.model_validate(p) for p in people_res.scalars().all()]

        return MultiSearchResponse(
            query=query,
            movies=movies,
            series=series,
            people=people,
            total_results=len(movies) + len(series) + len(people),
        )

    async def _count_movie(self, stmt) -> int:
        count_stmt = select(func.count()).select_from(stmt.subquery())
        result = await self.session.execute(count_stmt)
        return result.scalar_one()
