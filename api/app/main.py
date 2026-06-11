from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from app.config import settings
from app.database import create_tables
from app.routers import genres, movies, people, search, stats, youtube


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await create_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="ETMDB — Ethiopian Movie Database",
        description=(
            "Public REST API for Ethiopian and Amharic-language films. "
            "Browse metadata from TMDB, Wikidata, Wikipedia, and YouTube."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    app.include_router(movies.router, prefix="/api/v1")
    app.include_router(people.router, prefix="/api/v1")
    app.include_router(genres.router, prefix="/api/v1")
    app.include_router(search.router, prefix="/api/v1")
    app.include_router(youtube.router, prefix="/api/v1")
    app.include_router(stats.router, prefix="/api/v1")

    @app.get("/reference", include_in_schema=False)
    async def scalar_docs():
        return get_scalar_api_reference(
            openapi_url=app.openapi_url,
            title="ETMDB API Reference",
        )

    return app


app = create_app()
