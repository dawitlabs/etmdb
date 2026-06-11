from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.models.credit import Credit
from app.models.movie import Movie
from app.models.youtube_link import YouTubeLink
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

    async def list_media(
        self,
        media_type: str | None = None,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = "title",
        year: int | None = None,
        language: str | None = None,
        country: str | None = None,
    ) -> PaginatedResponse[MoviePublic]:
        stmt = select(Movie)
        if media_type:
            stmt = stmt.where(Movie.type == media_type)
        if year:
            stmt = stmt.where(Movie.release_year == year)
        if language:
            stmt = stmt.where(Movie.spoken_languages.contains(language))
        if country:
            stmt = stmt.where(Movie.countries.contains(country))

        stmt = stmt.order_by(self._sort_col(sort_by))
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

    async def popular(
        self,
        media_type: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> PaginatedResponse[MoviePublic]:
        views_sub = (
            select(YouTubeLink.movie_id, func.sum(YouTubeLink.view_count).label("total_views"))
            .where(YouTubeLink.movie_id.is_not(None))
            .group_by(YouTubeLink.movie_id)
            .subquery()
        )
        stmt = (
            select(Movie, func.coalesce(views_sub.c.total_views, 0).label("popularity"))
            .outerjoin(views_sub, views_sub.c.movie_id == Movie.id)
        )
        if media_type:
            stmt = stmt.where(Movie.type == media_type)
        stmt = stmt.order_by(func.coalesce(views_sub.c.total_views, 0).desc())

        total_stmt = select(func.count()).select_from(
            select(Movie).where(Movie.type == media_type).subquery() if media_type
            else select(Movie).subquery()
        )
        total_result = await self.session.execute(total_stmt)
        total = total_result.scalar_one()

        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        result = await self.session.execute(stmt)
        movies = [row[0] for row in result.all()]

        return PaginatedResponse.create(
            results=[MoviePublic.model_validate(m) for m in movies],
            total=total,
            page=page,
            per_page=per_page,
        )

    async def top_rated(
        self,
        media_type: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> PaginatedResponse[MoviePublic]:
        stmt = (
            select(Movie)
            .where(Movie.tmdb_rating.is_not(None))
            .where(Movie.tmdb_rating > 0)
        )
        if media_type:
            stmt = stmt.where(Movie.type == media_type)
        stmt = stmt.order_by(Movie.tmdb_rating.desc(), Movie.tmdb_votes.desc().nulls_last())

        total = await self._count(stmt)
        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        result = await self.session.execute(stmt)

        return PaginatedResponse.create(
            results=[MoviePublic.model_validate(m) for m in result.scalars().all()],
            total=total,
            page=page,
            per_page=per_page,
        )

    async def recent(
        self,
        media_type: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> PaginatedResponse[MoviePublic]:
        stmt = select(Movie).where(Movie.release_year.is_not(None))
        if media_type:
            stmt = stmt.where(Movie.type == media_type)
        stmt = stmt.order_by(Movie.release_year.desc())

        total = await self._count(stmt)
        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        result = await self.session.execute(stmt)

        return PaginatedResponse.create(
            results=[MoviePublic.model_validate(m) for m in result.scalars().all()],
            total=total,
            page=page,
            per_page=per_page,
        )

    async def get_by_slug(self, slug: str) -> MovieDetail | None:
        stmt = (
            select(Movie)
            .where(Movie.slug == slug)
            .options(
                selectinload(Movie.genres),
                selectinload(Movie.credits).selectinload(Credit.person),
                selectinload(Movie.youtube_links),
            )
        )
        result = await self.session.execute(stmt)
        movie = result.scalars().first()
        if not movie:
            return None

        return self._to_detail(movie)

    async def similar(self, slug: str, limit: int = 12) -> list[MoviePublic]:
        # Load target movie with genres
        stmt = (
            select(Movie)
            .where(Movie.slug == slug)
            .options(selectinload(Movie.genres))
        )
        result = await self.session.execute(stmt)
        target = result.scalars().first()
        if not target or not target.genres:
            return []

        genre_ids = [g.id for g in target.genres]

        from app.models.genre import MovieGenre
        similar_stmt = (
            select(Movie)
            .join(MovieGenre, MovieGenre.movie_id == Movie.id)
            .where(MovieGenre.genre_id.in_(genre_ids))
            .where(Movie.id != target.id)
            .where(Movie.type == target.type)
            .group_by(Movie.id)
            .order_by(Movie.tmdb_rating.desc().nulls_last())
            .limit(limit)
        )
        result = await self.session.execute(similar_stmt)
        return [MoviePublic.model_validate(m) for m in result.scalars().all()]

    async def videos(self, slug: str) -> list[YouTubeLinkBrief]:
        stmt = (
            select(Movie)
            .where(Movie.slug == slug)
            .options(selectinload(Movie.youtube_links))
        )
        result = await self.session.execute(stmt)
        movie = result.scalars().first()
        if not movie:
            return []

        links = sorted(movie.youtube_links, key=lambda yl: (not yl.is_primary, -(yl.view_count or 0)))
        return [
            YouTubeLinkBrief(
                video_id=yl.video_id,
                title=yl.title,
                channel_title=yl.channel_title,
                published_at=yl.published_at,
                duration_seconds=yl.duration_seconds,
                view_count=yl.view_count,
                thumbnail_url=yl.thumbnail_url,
                is_primary=yl.is_primary,
            )
            for yl in links
        ]

    def _to_detail(self, movie: Movie) -> MovieDetail:
        return MovieDetail(
            id=movie.id,
            type=movie.type,
            title=movie.title,
            original_title=movie.original_title,
            slug=movie.slug,
            overview=movie.overview,
            tagline=movie.tagline,
            status=movie.status,
            poster_url=movie.poster_url,
            backdrop_url=movie.backdrop_url,
            release_date=movie.release_date,
            release_year=movie.release_year,
            runtime=movie.runtime,
            number_of_seasons=movie.number_of_seasons,
            number_of_episodes=movie.number_of_episodes,
            spoken_languages=movie.spoken_languages,
            countries=movie.countries,
            tmdb_id=movie.tmdb_id,
            imdb_id=movie.imdb_id,
            wikidata_id=movie.wikidata_id,
            wikipedia_url=movie.wikipedia_url,
            source=movie.source,
            tmdb_rating=movie.tmdb_rating,
            tmdb_votes=movie.tmdb_votes,
            genres=[GenrePublic(id=g.id, name=g.name, name_am=g.name_am, slug=g.slug) for g in movie.genres],
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
                    published_at=yl.published_at,
                    duration_seconds=yl.duration_seconds,
                    view_count=yl.view_count,
                    thumbnail_url=yl.thumbnail_url,
                    is_primary=yl.is_primary,
                )
                for yl in sorted(movie.youtube_links, key=lambda y: (not y.is_primary, -(y.view_count or 0)))
            ],
        )

    def _sort_col(self, sort_by: str):
        return {
            "title": Movie.title.asc(),
            "release_year": Movie.release_year.desc().nulls_last(),
            "tmdb_rating": Movie.tmdb_rating.desc().nulls_last(),
        }.get(sort_by, Movie.title.asc())

    async def _count(self, stmt) -> int:
        count_stmt = select(func.count()).select_from(stmt.subquery())
        result = await self.session.execute(count_stmt)
        return result.scalar_one()
