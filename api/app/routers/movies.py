from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import verify_api_key
from app.exceptions import NotFoundError
from app.schemas.movie import MovieDetail, MoviePublic
from app.schemas.pagination import PaginatedResponse
from app.services.movie_service import MovieService

router = APIRouter(prefix="/movies", tags=["Movies"], dependencies=[Depends(verify_api_key)])


@router.get("", response_model=PaginatedResponse[MoviePublic])
async def list_movies(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("title", pattern="^(title|release_year|tmdb_rating)$"),
    year: int | None = None,
    language: str | None = None,
    session: AsyncSession = Depends(get_db),
):
    service = MovieService(session)
    return await service.list_movies(
        page=page, per_page=per_page, sort_by=sort_by, year=year, language=language
    )


@router.get("/{slug}", response_model=MovieDetail)
async def get_movie(slug: str, session: AsyncSession = Depends(get_db)):
    service = MovieService(session)
    movie = await service.get_by_slug(slug)
    if not movie:
        raise NotFoundError("Movie")
    return movie
