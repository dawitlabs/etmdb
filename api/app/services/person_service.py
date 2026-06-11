from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.models.person import Person
from app.schemas.pagination import PaginatedResponse
from app.schemas.person import FilmographyEntry, PersonDetail, PersonPublic


class PersonService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_people(
        self, page: int = 1, per_page: int = 20
    ) -> PaginatedResponse[PersonPublic]:
        query = select(Person).order_by(Person.name.asc())

        total = await self._count(query)

        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await self.session.execute(query)
        people = result.scalars().all()

        return PaginatedResponse.create(
            results=[PersonPublic.model_validate(p) for p in people],
            total=total,
            page=page,
            per_page=per_page,
        )

    async def get_by_slug(self, slug: str) -> PersonDetail | None:
        query = (
            select(Person)
            .where(Person.slug == slug)
            .options(selectinload(Person.credits))
        )
        result = await self.session.execute(query)
        person = result.scalars().first()
        if not person:
            return None

        filmography = [
            FilmographyEntry(
                movie_id=c.movie.id,
                movie_title=c.movie.title,
                movie_slug=c.movie.slug,
                movie_poster_url=c.movie.poster_url,
                role=c.role,
                character_name=c.character_name,
                release_year=c.movie.release_year,
            )
            for c in person.credits
            if c.movie
        ]

        return PersonDetail(
            id=person.id,
            name=person.name,
            name_am=person.name_am,
            slug=person.slug,
            photo_url=person.photo_url,
            bio=person.bio,
            tmdb_id=person.tmdb_id,
            filmography=filmography,
        )

    async def _count(self, query) -> int:
        count_query = select(func.count()).select_from(query.subquery())
        result = await self.session.execute(count_query)
        return result.scalar_one()
