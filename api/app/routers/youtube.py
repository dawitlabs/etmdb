from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import verify_api_key
from app.exceptions import NotFoundError
from app.schemas.pagination import PaginatedResponse
from app.schemas.youtube import YouTubeLinkPublic
from app.services.youtube_service import YouTubeService

router = APIRouter(prefix="/youtube", tags=["YouTube"], dependencies=[Depends(verify_api_key)])


@router.get("", response_model=PaginatedResponse[YouTubeLinkPublic])
async def list_youtube_links(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    movie_id: int | None = None,
    linked_only: bool = False,
    session: AsyncSession = Depends(get_db),
):
    service = YouTubeService(session)
    return await service.list_links(
        page=page, per_page=per_page, movie_id=movie_id, linked_only=linked_only
    )


@router.get("/{video_id}", response_model=YouTubeLinkPublic)
async def get_youtube_link(video_id: str, session: AsyncSession = Depends(get_db)):
    service = YouTubeService(session)
    link = await service.get_by_video_id(video_id)
    if not link:
        raise NotFoundError("YouTube link")
    return link
