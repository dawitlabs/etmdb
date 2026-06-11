# ETMDB — Ethiopian Movie Database

A public, open-source API for Ethiopian and Amharic-language films. Think TMDB, but focused entirely on Ethiopian cinema.

- **Docs:** https://etmdb.dawit.dev
- **API:** https://api.etmdb.dawit.dev
- **Reference:** https://api.etmdb.dawit.dev/reference

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

No API key required for read access. Use the demo key below for testing authenticated endpoints.

```bash
# Popular movies (no key needed)
curl https://api.etmdb.dawit.dev/api/v1/movies/popular

# Search
curl "https://api.etmdb.dawit.dev/api/v1/search/multi?q=Difret"

# With demo key
curl -H "X-Api-Key: etmdb_ku9T6l0y2YiHvOgMB2EdT4Zqr4xFRB_W-jdbKvVyETo" \
  https://api.etmdb.dawit.dev/api/v1/movies
```

Register your own free key:

```bash
curl -X POST https://api.etmdb.dawit.dev/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Your Name", "email": "you@example.com"}'
```

## Local Development

### API

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### Documentation Site

```bash
cd docs
pnpm install
pnpm dev
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT
