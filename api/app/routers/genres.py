from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.database import get_db
from app.dependencies import verify_api_key
from app.exceptions import NotFoundError
from app.models.genre import Genre
from app.schemas.movie import GenrePublic, MoviePublic
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/genres", tags=["Genres"], dependencies=[Depends(verify_api_key)])


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
    query = select(Genre).where(Genre.slug == slug).options(selectinload(Genre.movies))
    result = await session.execute(query)
    genre = result.scalars().first()
    if not genre:
        raise NotFoundError("Genre")

    movies = genre.movies
    total = len(movies)
    start = (page - 1) * per_page
    page_movies = movies[start : start + per_page]

    return PaginatedResponse.create(
        results=[MoviePublic.model_validate(m) for m in page_movies],
        total=total,
        page=page,
        per_page=per_page,
    )
