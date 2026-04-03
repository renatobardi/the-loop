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

## Phase B: Rule Versioning API

Phase B introduces **semantic versioning for Semgrep rules** with production-ready API endpoints:

### Features
- **Versioned rule releases** (semantic versioning X.Y.Z)
- **5-minute cache** on `/latest` for performance
- **Deprecation & rollback** (instant version rollback on discovery of issues)
- **Admin publishing** (Firebase-authenticated API for publishing new versions)
- **100% test coverage** (51 unit/integration tests, all CI gates pass)

### API Endpoints

```bash
# Public (no auth required)
GET    /api/v1/rules/latest                # Latest active version (cached)
GET    /api/v1/rules/{version}             # Specific version (e.g., 0.1.0)
GET    /api/v1/rules/versions              # List all versions
GET    /api/v1/rules/deprecated            # List deprecated versions

# Admin only (Firebase token required)
POST   /api/v1/rules/publish               # Publish new version
POST   /api/v1/rules/deprecate             # Deprecate a version
```

### Quick Start

```bash
# Fetch latest rules
curl https://theloop-api-1090621437043.us-central1.run.app/api/v1/rules/latest \
  | jq '.version'
# Output: "0.2.0"

# List all versions
curl https://theloop-api-1090621437043.us-central1.run.app/api/v1/rules/versions \
  | jq '.versions[] | {version, status, created_at}'

# Deprecate a version (admin only)
curl -X POST https://theloop-api.../api/v1/rules/deprecate \
  -H "Authorization: Bearer $FIREBASE_TOKEN" \
  -d '{"version": "0.1.0"}'
```

### Documentation

- **[API Reference](./specs/011-phase-b-api-integration/API.md)** — All endpoints, examples, error handling
- **[Versioning Strategy](./specs/011-phase-b-api-integration/VERSIONING.md)** — Semantic versioning, deprecation, rollback
- **[Migration Guide](./specs/011-phase-b-api-integration/MIGRATION.md)** — Upgrading from Phase A
- **[Troubleshooting](./specs/011-phase-b-api-integration/TROUBLESHOOTING.md)** — Common issues and fixes

### Current Versions

| Version | Status | Rules | Released |
|---------|--------|-------|----------|
| 0.2.0 | ACTIVE | 20 (6 Phase A + 14 Phase B) | 2026-04-03 |
| 0.1.0 | ACTIVE | 6 (Phase A) | 2026-02-01 |

## Constitution

This project is governed by 13 mandamentos defined in [CONSTITUTION.md](./CONSTITUTION.md). All contributions must comply.

## Links

- **Landing page**: https://loop.oute.pro
- **API**: https://theloop-api-1090621437043.us-central1.run.app
- **Contact**: loop@oute.pro
