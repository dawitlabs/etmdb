from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.genre import Genre, MovieGenre
from app.models.movie import Movie
from app.models.youtube_link import YouTubeLink
from app.schemas.movie import MoviePublic
from app.schemas.pagination import PaginatedResponse

SORT_MAP = {
    "popularity.desc": None,  # handled with join
    "rating.desc": Movie.tmdb_rating.desc().nulls_last(),
    "rating.asc": Movie.tmdb_rating.asc().nulls_last(),
    "year.desc": Movie.release_year.desc().nulls_last(),
    "year.asc": Movie.release_year.asc().nulls_last(),
    "title.asc": Movie.title.asc(),
    "title.desc": Movie.title.desc(),
}


class DiscoverService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def discover(
        self,
        media_type: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        year_gte: int | None = None,
        year_lte: int | None = None,
        rating_gte: float | None = None,
        rating_lte: float | None = None,
        language: str | None = None,
        country: str | None = None,
        sort_by: str = "popularity.desc",
        page: int = 1,
        per_page: int = 20,
    ) -> PaginatedResponse[MoviePublic]:
        if sort_by == "popularity.desc":
            return await self._discover_by_popularity(
                media_type, genre, year, year_gte, year_lte,
                rating_gte, rating_lte, language, country, page, per_page,
            )

        stmt = select(Movie)
        stmt = self._apply_filters(stmt, media_type, genre, year, year_gte, year_lte, rating_gte, rating_lte, language, country)
        stmt = stmt.order_by(SORT_MAP.get(sort_by, Movie.title.asc()))

        total = await self._count(stmt)
        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        result = await self.session.execute(stmt)

        return PaginatedResponse.create(
            results=[MoviePublic.model_validate(m) for m in result.scalars().all()],
            total=total,
            page=page,
            per_page=per_page,
        )

    async def _discover_by_popularity(
        self,
        media_type, genre, year, year_gte, year_lte,
        rating_gte, rating_lte, language, country, page, per_page,
    ) -> PaginatedResponse[MoviePublic]:
        views_sub = (
            select(YouTubeLink.movie_id, func.sum(YouTubeLink.view_count).label("total_views"))
            .where(YouTubeLink.movie_id.is_not(None))
            .group_by(YouTubeLink.movie_id)
            .subquery()
        )
        stmt = (
            select(Movie, func.coalesce(views_sub.c.total_views, 0).label("pop"))
            .outerjoin(views_sub, views_sub.c.movie_id == Movie.id)
        )
        stmt = self._apply_filters(stmt, media_type, genre, year, year_gte, year_lte, rating_gte, rating_lte, language, country)
        stmt = stmt.order_by(func.coalesce(views_sub.c.total_views, 0).desc())

        base = select(Movie)
        base = self._apply_filters(base, media_type, genre, year, year_gte, year_lte, rating_gte, rating_lte, language, country)
        total = await self._count(base)

        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        result = await self.session.execute(stmt)
        movies = [row[0] for row in result.all()]

        return PaginatedResponse.create(
            results=[MoviePublic.model_validate(m) for m in movies],
            total=total,
            page=page,
            per_page=per_page,
        )

    def _apply_filters(self, stmt, media_type, genre, year, year_gte, year_lte, rating_gte, rating_lte, language, country):
        if media_type and media_type != "all":
            stmt = stmt.where(Movie.type == media_type)
        if genre:
            stmt = (
                stmt.join(MovieGenre, MovieGenre.movie_id == Movie.id)
                .join(Genre, Genre.id == MovieGenre.genre_id)
                .where(Genre.slug == genre)
            )
        if year:
            stmt = stmt.where(Movie.release_year == year)
        if year_gte:
            stmt = stmt.where(Movie.release_year >= year_gte)
        if year_lte:
            stmt = stmt.where(Movie.release_year <= year_lte)
        if rating_gte is not None:
            stmt = stmt.where(Movie.tmdb_rating >= rating_gte)
        if rating_lte is not None:
            stmt = stmt.where(Movie.tmdb_rating <= rating_lte)
        if language:
            stmt = stmt.where(Movie.spoken_languages.contains(language))
        if country:
            stmt = stmt.where(Movie.countries.contains(country))
        return stmt

    async def _count(self, stmt) -> int:
        count_stmt = select(func.count()).select_from(stmt.subquery())
        result = await self.session.execute(count_stmt)
        return result.scalar_one()
