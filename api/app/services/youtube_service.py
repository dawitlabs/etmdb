from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.youtube_link import YouTubeLink
from app.schemas.pagination import PaginatedResponse
from app.schemas.youtube import YouTubeLinkPublic


class YouTubeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_links(
        self,
        page: int = 1,
        per_page: int = 20,
        movie_id: int | None = None,
        linked_only: bool = False,
    ) -> PaginatedResponse[YouTubeLinkPublic]:
        query = select(YouTubeLink).order_by(YouTubeLink.view_count.desc().nulls_last())

        if movie_id is not None:
            query = query.where(YouTubeLink.movie_id == movie_id)
        if linked_only:
            query = query.where(YouTubeLink.movie_id.is_not(None))

        total = await self._count(query)

        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await self.session.execute(query)
        links = result.scalars().all()

        return PaginatedResponse.create(
            results=[YouTubeLinkPublic.model_validate(yl) for yl in links],
            total=total,
            page=page,
            per_page=per_page,
        )

    async def get_by_video_id(self, video_id: str) -> YouTubeLinkPublic | None:
        query = select(YouTubeLink).where(YouTubeLink.video_id == video_id)
        result = await self.session.execute(query)
        link = result.scalars().first()
        if not link:
            return None
        return YouTubeLinkPublic.model_validate(link)

    async def _count(self, query) -> int:
        count_query = select(func.count()).select_from(query.subquery())
        result = await self.session.execute(count_query)
        return result.scalar_one()
