# Authentication

## API Keys

All endpoints except `/stats` require an API key via the `X-Api-Key` header.

```bash
curl -H "X-Api-Key: YOUR_KEY" https://api.etmdb.dev/api/v1/movies
```

## Demo Key

For development and testing:

```
demo-key-etmdb-2026
```

Rate limit: 10,000 requests per day.

## Error Responses

| Status | Meaning |
| --- | --- |
| 401 | Missing or invalid API key |
| 429 | Daily rate limit exceeded |

```json
{"detail": "Missing API key. Pass X-Api-Key header."}
```
