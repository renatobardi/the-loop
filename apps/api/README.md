# The Loop — Incident API

FastAPI backend service. Hexagonal architecture with PostgreSQL + pgvector.

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
├── ports/       # Protocol interfaces
├── adapters/    # PostgreSQL (SQLAlchemy), Firebase Auth
└── api/         # FastAPI routes, middleware, dependencies
```

## API Endpoints

```
# Incidents
GET    /api/v1/incidents
POST   /api/v1/incidents
GET    /api/v1/incidents/{id}
PUT    /api/v1/incidents/{id}
DELETE /api/v1/incidents/{id}

# Sub-resources (timeline, responders, action items, attachments)
GET    /api/v1/incidents/{id}/timeline
GET    /api/v1/incidents/{id}/responders
GET    /api/v1/incidents/{id}/action-items
PUT    /api/v1/incidents/{id}/action-items/{item_id}
GET    /api/v1/incidents/{id}/attachments

# Postmortems
POST   /api/v1/incidents/{id}/postmortem
GET    /api/v1/incidents/{id}/postmortem
GET    /api/v1/postmortems
GET    /api/v1/postmortems/{id}
PUT    /api/v1/postmortems/{id}
POST   /api/v1/postmortems/{id}/lock
GET    /api/v1/postmortem-templates

# Analytics (all require auth)
GET    /api/v1/incidents/analytics/summary
GET    /api/v1/incidents/analytics/by-category
GET    /api/v1/incidents/analytics/by-team
GET    /api/v1/incidents/analytics/timeline

# Rules (versioning)
GET    /api/v1/rules/latest
GET    /api/v1/rules/{version}
GET    /api/v1/rules/versions
GET    /api/v1/rules/deprecated
POST   /api/v1/rules/publish
POST   /api/v1/rules/deprecate
```

## Testing

```bash
pytest                              # All tests
pytest tests/unit/                  # Domain logic only
pytest tests/integration/           # Requires PostgreSQL
pytest tests/api/                   # FastAPI TestClient
pytest --cov=src --cov-fail-under=80
```

## CI Gates

- `ruff check src/ tests/` — lint
- `mypy src/ --strict` — type check
- `pytest --cov=src --cov-fail-under=80` — tests with coverage
- Docker build + Trivy scan — security
