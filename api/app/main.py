from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from app.config import settings
from app.database import create_tables
from app.routers import auth, discover, genres, movies, people, search, series, stats, trending, youtube


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await create_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="ETMDB — Ethiopian Movie Database",
        description=(
            "Public REST API for Ethiopian and Amharic-language films and series. "
            "Discover, search, and explore metadata from TMDB, Wikidata, Wikipedia, and YouTube.\n\n"
            "**Free to use.** Register at `POST /api/v1/auth/register` to get an API key."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    prefix = "/api/v1"
    app.include_router(movies.router, prefix=prefix)
    app.include_router(series.router, prefix=prefix)
    app.include_router(search.router, prefix=prefix)
    app.include_router(discover.router, prefix=prefix)
    app.include_router(trending.router, prefix=prefix)
    app.include_router(genres.router, prefix=prefix)
    app.include_router(people.router, prefix=prefix)
    app.include_router(youtube.router, prefix=prefix)
    app.include_router(stats.router, prefix=prefix)
    app.include_router(auth.router, prefix=prefix)

    @app.get("/health", include_in_schema=False)
    async def health():
        return {"status": "ok"}

    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "name": "ETMDB API",
            "version": "1.0.0",
            "description": "Ethiopian Movie Database — open API for Ethiopian cinema",
            "docs": "/reference",
            "openapi": "/openapi.json",
        }

    @app.get("/reference", include_in_schema=False)
    async def scalar_docs():
        return get_scalar_api_reference(
            openapi_url=app.openapi_url,
            title="ETMDB API Reference",
        )

    return app


app = create_app()
