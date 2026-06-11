# Getting Started

## Base URL

```
https://api.etmdb.dev/api/v1
```

## Quick Start

1. Get an API key (see [Authentication](authentication.md))
2. Make your first request:

```bash
curl -H "X-Api-Key: YOUR_KEY" https://api.etmdb.dev/api/v1/movies
```

3. Search for a film:

```bash
curl -H "X-Api-Key: YOUR_KEY" "https://api.etmdb.dev/api/v1/search?q=Difret"
```

## Response Format

All list endpoints return paginated responses:

```json
{
  "page": 1,
  "per_page": 20,
  "total": 387,
  "total_pages": 20,
  "results": [...]
}
```

## Interactive API Reference

Visit `/reference` for the interactive Scalar API docs with a built-in playground.

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **Scalar**: `/reference`
- **OpenAPI Spec**: `/openapi.json`

## Data Sources

| Source | What it provides |
| --- | --- |
| TMDB | Posters, ratings, descriptions, release dates |
| Wikidata | Structured metadata, directors, IMDB cross-references |
| Wikipedia | Ethiopian film listings |
| YouTube | Links to full films, view counts, thumbnails |

## Python Example

```python
import httpx

client = httpx.Client(
    base_url="https://api.etmdb.dev/api/v1",
    headers={"X-Api-Key": "demo-key-etmdb-2026"},
)

movies = client.get("/movies", params={"per_page": 10}).json()
for movie in movies["results"]:
    print(f"{movie['title']} ({movie['release_year']})")
```

## JavaScript Example

```javascript
const res = await fetch("https://api.etmdb.dev/api/v1/movies?per_page=10", {
  headers: { "X-Api-Key": "demo-key-etmdb-2026" },
});
const data = await res.json();
data.results.forEach((m) => console.log(`${m.title} (${m.release_year})`));
```
