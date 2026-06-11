from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.movie import MoviePublic
from app.schemas.pagination import PaginatedResponse
from app.services.discover_service import DiscoverService

router = APIRouter(prefix="/discover", tags=["Discover"])

SORT_OPTIONS = "^(popularity\\.desc|rating\\.desc|rating\\.asc|year\\.desc|year\\.asc|title\\.asc|title\\.desc)$"


@router.get("", response_model=PaginatedResponse[MoviePublic])
async def discover(
    type: str | None = Query(None, pattern="^(movie|series|all)$"),
    genre: str | None = None,
    year: int | None = None,
    year_gte: int | None = None,
    year_lte: int | None = None,
    rating_gte: float | None = Query(None, ge=0, le=10),
    rating_lte: float | None = Query(None, ge=0, le=10),
    language: str | None = None,
    country: str | None = None,
    sort_by: str = Query("popularity.desc", pattern=SORT_OPTIONS),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    return await DiscoverService(session).discover(
        media_type=type,
        genre=genre,
        year=year,
        year_gte=year_gte,
        year_lte=year_lte,
        rating_gte=rating_gte,
        rating_lte=rating_lte,
        language=language,
        country=country,
        sort_by=sort_by,
        page=page,
        per_page=per_page,
    )
