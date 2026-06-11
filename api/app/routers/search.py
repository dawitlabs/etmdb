from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.movie import MoviePublic, MultiSearchResponse
from app.schemas.pagination import PaginatedResponse
from app.schemas.person import PersonPublic
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/multi", response_model=MultiSearchResponse)
async def multi_search(
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(5, ge=1, le=20),
    session: AsyncSession = Depends(get_db),
):
    """Search movies, series, and people in a single request."""
    return await SearchService(session).multi_search(query=q, limit=limit)


@router.get("/movies", response_model=PaginatedResponse[MoviePublic])
async def search_movies(
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    year: int | None = None,
    language: str | None = None,
    session: AsyncSession = Depends(get_db),
):
    return await SearchService(session).search_media(
        query=q, media_type="movie", page=page, per_page=per_page, year=year, language=language,
    )


@router.get("/series", response_model=PaginatedResponse[MoviePublic])
async def search_series(
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    year: int | None = None,
    language: str | None = None,
    session: AsyncSession = Depends(get_db),
):
    return await SearchService(session).search_media(
        query=q, media_type="series", page=page, per_page=per_page, year=year, language=language,
    )


@router.get("/people", response_model=PaginatedResponse[PersonPublic])
async def search_people(
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    return await SearchService(session).search_people(query=q, page=page, per_page=per_page)


@router.get("", response_model=PaginatedResponse[MoviePublic])
async def search(
    q: str = Query(..., min_length=1, max_length=200),
    type: str | None = Query(None, pattern="^(movie|series)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    year: int | None = None,
    language: str | None = None,
    session: AsyncSession = Depends(get_db),
):
    """Search all titles (movies + series). Use `type` to filter."""
    return await SearchService(session).search_media(
        query=q, media_type=type, page=page, per_page=per_page, year=year, language=language,
    )
