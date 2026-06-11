import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.database import get_db
from app.dependencies import hash_api_key
from app.main import create_app
from app.models.api_key import APIKey
from app.models.genre import Genre
from app.models.movie import Movie
from app.models.person import Person
from app.models.credit import Credit
from app.models.youtube_link import YouTubeLink

TEST_API_KEY = "test-key-12345"


@pytest.fixture
async def engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def session(engine):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def seeded_session(session):
    movie = Movie(
        title="Difret",
        original_title="ድፍረት",
        slug="difret",
        overview="A young Ethiopian girl fights against abduction.",
        poster_url="https://example.com/difret.jpg",
        release_year=2014,
        release_date="2014-06-13",
        spoken_languages=["am"],
        countries=["Ethiopia"],
        tmdb_id=99999,
        source="tmdb",
        tmdb_rating=7.2,
    )
    session.add(movie)

    movie2 = Movie(
        title="Lamb",
        slug="lamb",
        overview="A shepherd boy and his loyal friend.",
        release_year=2015,
        spoken_languages=["am"],
        countries=["Ethiopia"],
        source="wikidata",
    )
    session.add(movie2)
    await session.flush()

    genre = Genre(name="Drama", name_am="ድራማ", slug="drama")
    session.add(genre)

    person = Person(name="Zeresenay Mehari", slug="zeresenay-mehari")
    session.add(person)
    await session.flush()

    session.add(Credit(movie_id=movie.id, person_id=person.id, role="director"))

    link = YouTubeLink(
        video_id="abc123",
        title="Difret Full Movie",
        channel_title="Ethiopian Films",
        movie_id=movie.id,
        view_count=500000,
        duration_seconds=5400,
        is_primary=True,
    )
    session.add(link)

    link2 = YouTubeLink(
        video_id="xyz789",
        title="Random Ethiopian Music",
        channel_title="Music Channel",
        view_count=1000,
        duration_seconds=240,
    )
    session.add(link2)

    api_key = APIKey(
        key_hash=hash_api_key(TEST_API_KEY),
        key_prefix="test-key",
        name="Test Key",
        email="test@etmdb.dev",
        rate_limit=1000,
    )
    session.add(api_key)
    await session.commit()
    yield session


@pytest.fixture
async def client(seeded_session, engine):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with async_session() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def headers():
    return {"X-Api-Key": TEST_API_KEY}
