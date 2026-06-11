# ETMDB — Ethiopian Movie Database

A public, open-source API for Ethiopian and Amharic-language films. Think TMDB, but focused entirely on Ethiopian cinema.

## What's Inside

```
api/    FastAPI backend — REST API serving film metadata
docs/   Fumadocs site — interactive API documentation
```

## Data Sources

ETMDB aggregates film metadata from multiple open sources:

- **TMDB** — posters, ratings, descriptions, release dates
- **Wikidata** — structured film metadata, director information, IMDB cross-references
- **Wikipedia** — Ethiopian film listings and context
- **YouTube** — links to full films, view counts, thumbnails

## Quick Start

### API

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. Swagger docs at `/docs`, OpenAPI spec at `/openapi.json`.

### Documentation Site

```bash
cd docs
pnpm install
pnpm dev
```

Docs site runs at `http://localhost:3000`.

## API Usage

```bash
# Get all movies
curl -H "X-Api-Key: YOUR_KEY" http://localhost:8000/api/v1/movies

# Search for a film
curl -H "X-Api-Key: YOUR_KEY" "http://localhost:8000/api/v1/search?q=ፔንዱለም"

# Get movie details
curl -H "X-Api-Key: YOUR_KEY" http://localhost:8000/api/v1/movies/pendulum
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT
