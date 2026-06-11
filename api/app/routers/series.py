from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import NotFoundError
from app.schemas.movie import MovieDetail, MoviePublic, YouTubeLinkBrief
from app.schemas.pagination import PaginatedResponse
from app.services.movie_service import MovieService

router = APIRouter(prefix="/series", tags=["Series"])


@router.get("", response_model=PaginatedResponse[MoviePublic])
async def list_series(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("title", pattern="^(title|release_year|tmdb_rating)$"),
    year: int | None = None,
    language: str | None = None,
    country: str | None = None,
    session: AsyncSession = Depends(get_db),
):
    return await MovieService(session).list_media(
        media_type="series", page=page, per_page=per_page,
        sort_by=sort_by, year=year, language=language, country=country,
    )


@router.get("/popular", response_model=PaginatedResponse[MoviePublic])
async def popular_series(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    return await MovieService(session).popular(media_type="series", page=page, per_page=per_page)


@router.get("/top-rated", response_model=PaginatedResponse[MoviePublic])
async def top_rated_series(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    return await MovieService(session).top_rated(media_type="series", page=page, per_page=per_page)


@router.get("/recent", response_model=PaginatedResponse[MoviePublic])
async def recent_series(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    return await MovieService(session).recent(media_type="series", page=page, per_page=per_page)


@router.get("/{slug}", response_model=MovieDetail)
async def get_series(slug: str, session: AsyncSession = Depends(get_db)):
    series = await MovieService(session).get_by_slug(slug)
    if not series or series.type != "series":
        raise NotFoundError("Series")
    return series


@router.get("/{slug}/similar", response_model=list[MoviePublic])
async def similar_series(
    slug: str,
    limit: int = Query(12, ge=1, le=30),
    session: AsyncSession = Depends(get_db),
):
    return await MovieService(session).similar(slug=slug, limit=limit)


@router.get("/{slug}/videos", response_model=list[YouTubeLinkBrief])
async def series_videos(slug: str, session: AsyncSession = Depends(get_db)):
    return await MovieService(session).videos(slug=slug)
