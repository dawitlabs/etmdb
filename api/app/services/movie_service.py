from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, subqueryload
from sqlmodel import select

from app.models.credit import Credit
from app.models.movie import Movie
from app.schemas.movie import (
    CreditPublic,
    GenrePublic,
    MovieDetail,
    MoviePublic,
    YouTubeLinkBrief,
)
from app.schemas.pagination import PaginatedResponse


class MovieService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_movies(
        self,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = "title",
        year: int | None = None,
        language: str | None = None,
    ) -> PaginatedResponse[MoviePublic]:
        query = select(Movie)

        if year:
            query = query.where(Movie.release_year == year)
        if language:
            query = query.where(Movie.spoken_languages.contains(language))

        sort_column = self._resolve_sort(sort_by)
        query = query.order_by(sort_column)

        total = await self._count(query)

        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await self.session.execute(query)
        movies = result.scalars().all()

        return PaginatedResponse.create(
            results=[MoviePublic.model_validate(m) for m in movies],
            total=total,
            page=page,
            per_page=per_page,
        )

    async def get_by_slug(self, slug: str) -> MovieDetail | None:
        query = (
            select(Movie)
            .where(Movie.slug == slug)
            .options(
                selectinload(Movie.genres),
                selectinload(Movie.credits).selectinload(Credit.person),
                selectinload(Movie.youtube_links),
            )
        )
        result = await self.session.execute(query)
        movie = result.scalars().first()
        if not movie:
            return None

        return MovieDetail(
            id=movie.id,
            title=movie.title,
            original_title=movie.original_title,
            slug=movie.slug,
            overview=movie.overview,
            poster_url=movie.poster_url,
            backdrop_url=movie.backdrop_url,
            release_date=movie.release_date,
            release_year=movie.release_year,
            runtime=movie.runtime,
            spoken_languages=movie.spoken_languages,
            countries=movie.countries,
            tmdb_id=movie.tmdb_id,
            imdb_id=movie.imdb_id,
            wikidata_id=movie.wikidata_id,
            wikipedia_url=movie.wikipedia_url,
            source=movie.source,
            tmdb_rating=movie.tmdb_rating,
            tmdb_votes=movie.tmdb_votes,
            genres=[
                GenrePublic(id=g.id, name=g.name, name_am=g.name_am, slug=g.slug)
                for g in movie.genres
            ],
            credits=[
                CreditPublic(
                    id=c.id,
                    person_id=c.person_id,
                    person_name=c.person.name if c.person else "",
                    person_slug=c.person.slug if c.person else "",
                    role=c.role,
                    character_name=c.character_name,
                    sort_order=c.sort_order,
                )
                for c in movie.credits
            ],
            youtube_links=[
                YouTubeLinkBrief(
                    video_id=yl.video_id,
                    title=yl.title,
                    channel_title=yl.channel_title,
                    duration_seconds=yl.duration_seconds,
                    view_count=yl.view_count,
                    thumbnail_url=yl.thumbnail_url,
                    is_primary=yl.is_primary,
                )
                for yl in movie.youtube_links
            ],
        )

    def _resolve_sort(self, sort_by: str):
        mapping = {
            "title": Movie.title.asc(),
            "release_year": Movie.release_year.desc().nulls_last(),
            "tmdb_rating": Movie.tmdb_rating.desc().nulls_last(),
        }
        return mapping.get(sort_by, Movie.title.asc())

    async def _count(self, query) -> int:
        count_query = select(func.count()).select_from(query.subquery())
        result = await self.session.execute(count_query)
        return result.scalar_one()
