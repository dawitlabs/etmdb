from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import verify_api_key
from app.schemas.movie import MoviePublic
from app.schemas.pagination import PaginatedResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"], dependencies=[Depends(verify_api_key)])


@router.get("", response_model=PaginatedResponse[MoviePublic])
async def search_movies(
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    year: int | None = None,
    language: str | None = None,
    session: AsyncSession = Depends(get_db),
):
    service = SearchService(session)
    return await service.search_movies(
        query=q, page=page, per_page=per_page, year=year, language=language
    )
