from datetime import UTC, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.movie import Movie
from app.models.youtube_link import YouTubeLink
from app.schemas.movie import MoviePublic
from app.schemas.pagination import PaginatedResponse


class TrendingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def trending(
        self,
        media_type: str | None = None,
        time_window: str = "week",
        page: int = 1,
        per_page: int = 20,
    ) -> PaginatedResponse[MoviePublic]:
        now = datetime.now(UTC)
        cutoff = {
            "day": now - timedelta(days=1),
            "week": now - timedelta(weeks=1),
            "month": now - timedelta(days=30),
        }.get(time_window)

        views_sub_stmt = (
            select(YouTubeLink.movie_id, func.sum(YouTubeLink.view_count).label("trend_views"))
            .where(YouTubeLink.movie_id.is_not(None))
        )
        if cutoff:
            views_sub_stmt = views_sub_stmt.where(YouTubeLink.published_at >= cutoff)
        views_sub = views_sub_stmt.group_by(YouTubeLink.movie_id).subquery()

        stmt = (
            select(Movie, func.coalesce(views_sub.c.trend_views, 0).label("trend_score"))
            .join(views_sub, views_sub.c.movie_id == Movie.id)
        )
        if media_type and media_type != "all":
            stmt = stmt.where(Movie.type == media_type)
        stmt = stmt.order_by(func.coalesce(views_sub.c.trend_views, 0).desc())

        count_stmt = select(func.count(func.distinct(Movie.id))).join(
            views_sub, views_sub.c.movie_id == Movie.id
        )
        if media_type and media_type != "all":
            count_stmt = count_stmt.where(Movie.type == media_type)
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        # Fall back to all-time if window returns too few results
        if total < per_page and cutoff:
            return await self.trending(media_type=media_type, time_window="all", page=page, per_page=per_page)

        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        result = await self.session.execute(stmt)
        movies = [row[0] for row in result.all()]

        return PaginatedResponse.create(
            results=[MoviePublic.model_validate(m) for m in movies],
            total=total,
            page=page,
            per_page=per_page,
        )
