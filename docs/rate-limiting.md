# Rate Limiting

## Limits

| Key Type | Daily Limit |
| --- | --- |
| Default | 1,000 requests |
| Demo key | 10,000 requests |

Limits reset at midnight UTC.

## Best Practices

- Cache responses locally
- Use pagination efficiently
- Use filters (`year`, `language`) to narrow results
- `/stats` is unauthenticated and unlimited
