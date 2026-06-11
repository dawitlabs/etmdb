# Contributing to ETMDB

## Development Setup

### Prerequisites

- Python 3.13+
- Node.js 22+ and pnpm
- Git

### API Development

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload
```

### Docs Development

```bash
cd docs
pnpm install
pnpm dev
```

## Code Standards

This project follows Clean Code principles:

- **Meaningful names** — variables, functions, and classes describe their purpose
- **Small functions** — each function does one thing
- **DRY** — no duplicated logic
- **Self-documenting code** — comments only when the why is non-obvious
- **Proper error handling** — without obscuring main logic

### Python (API)

- Lint with `ruff check .`
- Type check with `mypy app/`
- Format with `ruff format .`
- Test with `pytest`

### TypeScript (Docs)

- Lint with `pnpm lint`
- Build check with `pnpm build`

## Project Structure

```
api/app/
  models/      SQLModel table definitions
  schemas/     Request/response Pydantic models
  routers/     Thin API route handlers
  services/    Business logic
```

**Routers** parse request parameters and delegate to services.
**Services** contain all query and business logic.
**Models** define database tables.
**Schemas** define API input/output shapes.

## Pull Requests

- One focused change per PR
- Include tests for new endpoints
- Run `ruff check . && mypy app/ && pytest` before submitting
- Write a clear description of what changed and why
