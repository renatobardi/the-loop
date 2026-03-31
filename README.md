# The Loop

**Eliminate production incidents before they happen.**

The Loop closes the gap between post-mortems and code by transforming incident knowledge into active guardrails in your CI/CD pipeline.

## Architecture

```
apps/
├── web/          # SvelteKit frontend (adapter-node)
│   ├── src/
│   │   ├── routes/        # Plain path routing (/, /incidents/, /constitution/)
│   │   ├── lib/ui/        # Design system (tokens + components)
│   │   ├── lib/components/ # Page sections
│   │   ├── lib/server/    # Firebase admin, waitlist, rate limiter
│   │   └── lib/services/  # API clients (incidents)
│   └── Dockerfile         # Multi-stage, non-root (Cloud Run)
└── api/          # FastAPI backend (hexagonal architecture)
    ├── src/
    │   ├── domain/        # Pure Python models and services
    │   ├── ports/         # Protocol interfaces
    │   ├── adapters/      # PostgreSQL, Firebase Auth
    │   └── api/           # FastAPI routes, middleware
    └── Dockerfile         # Multi-stage, non-root (Cloud Run)
```

## Tech Stack

**Frontend**
- **Framework**: SvelteKit 2 + Svelte 5 runes, adapter-node
- **Styling**: Tailwind CSS 4
- **Auth**: Firebase (client SDK, Auth only)
- **Waitlist**: Firebase Firestore (project: theloopoute)
- **Deployment**: GCP Cloud Run via GitHub Actions

**Backend**
- **Framework**: FastAPI + SQLAlchemy 2.0 async + Pydantic v2
- **Database**: PostgreSQL 16 + pgvector + pg_trgm (Cloud SQL)
- **Auth**: Firebase Admin SDK (token verification)
- **Deployment**: GCP Cloud Run via GitHub Actions

## Development

```bash
# Frontend
cd apps/web
npm install
npm run dev           # http://localhost:5173/

# Backend
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql+asyncpg://theloop:theloop@localhost:5432/theloop"
alembic upgrade head
uvicorn src.main:app --reload --port 8000   # http://localhost:8000/docs
```

## Quality Checks

```bash
# Frontend
npm run lint       # ESLint + Prettier
npm run check      # TypeScript + svelte-check
npm run test       # vitest
npm run build      # Production build

# Backend
ruff check src/ tests/        # Lint
mypy src/ --strict             # Type check
pytest --cov=src               # Tests with coverage
```

## Deployment

Automatic on merge to `main` via GitHub Actions:
1. CI gates (lint, type-check, test, build, vulnerability scan, docs-check)
2. Docker build → Artifact Registry
3. Cloud Run deploy (web: `the-loop`, api: `theloop-api`)

## Constitution

This project is governed by 13 mandamentos defined in [CONSTITUTION.md](./CONSTITUTION.md). All contributions must comply.

## Links

- **Landing page**: https://loop.oute.pro
- **API**: https://theloop-api-1090621437043.us-central1.run.app
- **Contact**: loop@oute.pro
