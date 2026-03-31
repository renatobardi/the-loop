# The Loop — Incident API

FastAPI backend service for the incident CRUD module. Hexagonal architecture with PostgreSQL + pgvector.

## Quick Start

```bash
# Prerequisites: Python 3.12+, PostgreSQL 16 with pgvector

# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Database
export DATABASE_URL="postgresql+asyncpg://theloop:theloop@localhost:5432/theloop"
alembic upgrade head

# Run
uvicorn src.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`.

## Architecture

```
src/
├── domain/      # Pure Python: models (Pydantic), exceptions, services
├── ports/       # Protocol interfaces (IncidentRepoPort)
├── adapters/    # PostgreSQL (SQLAlchemy), Firebase Auth
└── api/         # FastAPI routes, middleware, dependencies
```

## Testing

```bash
pytest                              # All tests
pytest tests/unit/                  # Domain logic only
pytest tests/integration/           # Requires PostgreSQL
pytest tests/api/                   # FastAPI TestClient
```

## CI Gates

- `ruff check src/ tests/` — lint
- `mypy src/ --strict` — type check
- `pytest` — tests
- Docker build + Trivy scan — security
