# Quickstart: Incident Module — CRUD (Phase A, Revised)

**Branch**: `007-incident-crud-v2` | **Date**: 2026-03-31

## Prerequisites

- Python 3.12+
- Node.js 22+
- PostgreSQL 16 with pgvector extension
- Firebase project (theloopoute) with Auth enabled
- Docker (for running PostgreSQL locally)

## Local PostgreSQL Setup

```bash
# Start PostgreSQL with pgvector via Docker
docker run -d \
  --name theloop-postgres \
  -e POSTGRES_DB=theloop \
  -e POSTGRES_USER=theloop \
  -e POSTGRES_PASSWORD=theloop \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Verify pgvector is available
docker exec theloop-postgres psql -U theloop -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## Backend Setup (apps/api/)

```bash
cd apps/api

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://theloop:theloop@localhost:5432/theloop"
export FIREBASE_SERVICE_ACCOUNT='<JSON from GCP Secret Manager>'

# Run database migrations
alembic upgrade head

# Start dev server
uvicorn src.main:app --reload --port 8000
```

## Frontend Setup (apps/web/)

```bash
cd apps/web

# Install dependencies
npm install

# Start dev server (Vite proxies /api/* to localhost:8000)
npm run dev
```

## Common Commands

### Backend (from apps/api/)

```bash
ruff check src/ tests/                # Lint
ruff format src/ tests/               # Format
mypy src/ --strict                    # Type check
pytest                                # Run all tests
pytest tests/unit/                    # Unit tests only
pytest --cov=src --cov-report=term-missing  # Tests with coverage
alembic revision --autogenerate -m "" # New migration
alembic upgrade head                  # Apply migrations
```

### Frontend (from apps/web/)

```bash
npm run dev          # Dev server at localhost:5173
npm run build        # Production build
npm run check        # TypeScript strict check
npm run lint         # ESLint + Prettier
npm run test         # Vitest watch mode
```

## Key URLs (Development)

| Service     | URL                                |
| ----------- | ---------------------------------- |
| Frontend    | http://localhost:5173/             |
| Incidents   | http://localhost:5173/incidents/   |
| API         | http://localhost:8000              |
| API docs    | http://localhost:8000/docs         |
| PostgreSQL  | localhost:5432                     |

## Verifying It Works

```bash
# 1. Check API health
curl http://localhost:8000/api/v1/health

# 2. Create an incident (requires valid Firebase token)
curl -X POST http://localhost:8000/api/v1/incidents \
  -H "Authorization: Bearer <firebase-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test incident",
    "category": "injection",
    "severity": "medium",
    "anti_pattern": "Direct string concatenation in SQL queries",
    "remediation": "Use parameterized queries"
  }'

# 3. List incidents
curl http://localhost:8000/api/v1/incidents \
  -H "Authorization: Bearer <firebase-token>"
```
