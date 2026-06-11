from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.movie import Movie
from app.schemas.movie import MoviePublic
from app.schemas.pagination import PaginatedResponse


class SearchService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_movies(
        self,
        query: str,
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

        if year:
            stmt = stmt.where(Movie.release_year == year)
        if language:
            stmt = stmt.where(Movie.spoken_languages.contains(language))

        stmt = stmt.order_by(Movie.tmdb_rating.desc().nulls_last())

        total = await self._count(stmt)

        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        result = await self.session.execute(stmt)
        movies = result.scalars().all()

        return PaginatedResponse.create(
            results=[MoviePublic.model_validate(m) for m in movies],
            total=total,
            page=page,
            per_page=per_page,
        )

    async def _count(self, query) -> int:
        count_query = select(func.count()).select_from(query.subquery())
        result = await self.session.execute(count_query)
        return result.scalar_one()
