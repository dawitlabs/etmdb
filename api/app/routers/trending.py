from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.movie import MoviePublic
from app.schemas.pagination import PaginatedResponse
from app.services.trending_service import TrendingService

router = APIRouter(prefix="/trending", tags=["Trending"])


@router.get("/{media_type}/{time_window}", response_model=PaginatedResponse[MoviePublic])
async def trending(
    media_type: str,
    time_window: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """
    Get trending titles ranked by YouTube view counts.

    - **media_type**: `movie`, `series`, or `all`
    - **time_window**: `day`, `week`, `month`, or `all`
    """
    if media_type not in ("movie", "series", "all"):
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="media_type must be movie, series, or all")
    if time_window not in ("day", "week", "month", "all"):
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="time_window must be day, week, month, or all")

    resolved_type = None if media_type == "all" else media_type
    return await TrendingService(session).trending(
        media_type=resolved_type,
        time_window=time_window,
        page=page,
        per_page=per_page,
    )
