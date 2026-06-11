from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.database import get_db
from app.exceptions import NotFoundError
from app.models.genre import Genre
from app.schemas.movie import GenrePublic, MoviePublic
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/genres", tags=["Genres"])


@router.get("", response_model=list[GenrePublic])
async def list_genres(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(Genre).order_by(Genre.name.asc()))
    return [GenrePublic.model_validate(g) for g in result.scalars().all()]


@router.get("/{slug}/movies", response_model=PaginatedResponse[MoviePublic])
async def movies_by_genre(
    slug: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Genre).where(Genre.slug == slug).options(selectinload(Genre.movies))
    )
    genre = result.scalars().first()
    if not genre:
        raise NotFoundError("Genre")

    movies = [m for m in genre.movies if m.type == "movie"]
    total = len(movies)
    page_movies = movies[(page - 1) * per_page : page * per_page]

    return PaginatedResponse.create(
        results=[MoviePublic.model_validate(m) for m in page_movies],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{slug}/series", response_model=PaginatedResponse[MoviePublic])
async def series_by_genre(
    slug: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Genre).where(Genre.slug == slug).options(selectinload(Genre.movies))
    )
    genre = result.scalars().first()
    if not genre:
        raise NotFoundError("Genre")

    series = [m for m in genre.movies if m.type == "series"]
    total = len(series)
    page_series = series[(page - 1) * per_page : page * per_page]

    return PaginatedResponse.create(
        results=[MoviePublic.model_validate(m) for m in page_series],
        total=total,
        page=page,
        per_page=per_page,
    )
