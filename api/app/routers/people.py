from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import verify_api_key
from app.exceptions import NotFoundError
from app.schemas.pagination import PaginatedResponse
from app.schemas.person import PersonDetail, PersonPublic
from app.services.person_service import PersonService

router = APIRouter(prefix="/people", tags=["People"], dependencies=[Depends(verify_api_key)])


@router.get("", response_model=PaginatedResponse[PersonPublic])
async def list_people(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    service = PersonService(session)
    return await service.list_people(page=page, per_page=per_page)


@router.get("/{slug}", response_model=PersonDetail)
async def get_person(slug: str, session: AsyncSession = Depends(get_db)):
    service = PersonService(session)
    person = await service.get_by_slug(slug)
    if not person:
        raise NotFoundError("Person")
    return person
