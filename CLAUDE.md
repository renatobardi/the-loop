# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

The Loop — incident prevention platform. Monorepo with two apps:

- **`apps/web/`** — SvelteKit 2 + Svelte 5 (runes), Tailwind CSS 4, Firebase Firestore. English-only. Phase 0 landing page + waitlist, Phase 1 incident CRUD UI.
- **`apps/api/`** — Python 3.12 FastAPI backend, SQLAlchemy 2.0 (async), Pydantic v2, PostgreSQL 16 + pgvector. Hexagonal architecture (domain/ports/adapters). Phase 1 incident CRUD API.

Deployed to GCP Cloud Run. Single environment: `main` = production.

## Commands

### Frontend (`apps/web/`)

```bash
npm run dev          # Dev server at localhost:5173
npm run build        # Production build (adapter-node → build/)
npm run check        # svelte-kit sync + svelte-check (TypeScript strict)
npm run lint         # ESLint + Prettier check
npm run format       # Prettier write
npm run test         # vitest watch mode (unit tests in tests/unit/)
npm run test -- --run                         # Single run (CI mode)
npm run test -- --run tests/unit/server.test.ts  # Run a single test file
```

### Backend (`apps/api/`)

```bash
pip install -r requirements.txt       # Install dependencies
uvicorn src.main:app --reload         # Dev server
ruff check src/ tests/                # Lint (strict rules)
ruff format src/ tests/               # Format
mypy src/                             # Type check (strict mode)
pytest tests/                         # Run all tests
pytest tests/unit/                    # Unit tests only
alembic upgrade head                  # Apply database migrations
alembic revision --autogenerate -m "" # Generate new migration
python scripts/seed.py --count 10000  # Seed 10k test records for performance testing
```

### Docs gate

If the `docs-check` CI gate fails, run locally and commit the result:
```bash
bash scripts/generate-docs.sh
```

### Backend Testing Specifics

pytest supports targeted test execution:
- `pytest tests/unit/domain/test_incident.py::test_create_incident` — run single test
- `pytest tests/ -k incident` — run all tests matching keyword
- `pytest --cov=src --cov-report=html` — generate HTML coverage report
- Tests run against a real PostgreSQL database (see "Local PostgreSQL Setup" below). Migrations are applied before each test suite and rolled back after via `conftest.py` fixtures.

### Local PostgreSQL Setup

Backend development requires PostgreSQL 16 with pgvector extension.

**Docker (recommended)**
```bash
docker run --name theloop-db \
  -e POSTGRES_USER=theloop \
  -e POSTGRES_PASSWORD=theloop \
  -e POSTGRES_DB=theloop \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# In another terminal, apply migrations:
cd apps/api
export DATABASE_URL="postgresql+asyncpg://theloop:theloop@localhost:5432/theloop"
alembic upgrade head
```

For CI tests, a temporary test database is created with the same setup.

## Architecture

### Frontend (`apps/web/src/`)

- **`routes/`** — File-based routing with plain paths. Trailing slashes enforced (`trailingSlash: 'always'` in `+layout.ts`). All routes use plain paths (`/`, `/incidents/`, `/constitution/`).
- **`routes/incidents/`** — Incident CRUD pages: list with filters/pagination, `[id]/` detail view, `[id]/edit/` edit form, `new/` create form. Client-side data loading via `+page.ts`.
- **`lib/ui/`** — Design system components (Button, Input, Card, Badge, Container, Section, Navbar, SkipLink). Barrel-exported via `index.ts`. Consumes design tokens from `app.css`.
- **`lib/components/`** — Page section components (Hero, Problem, Layers, HowItWorks, Pricing, Footer, WaitlistForm, etc.). All text hardcoded in English.
- **`lib/server/`** — Server-only modules: `firebase.ts` (singleton init), `waitlist.ts` (Firestore write, returns `'created' | 'duplicate'`), `schemas.ts` (Zod with email normalization), `rateLimiter.ts` (5 req/60s per IP).
- **`lib/services/incidents.ts`** — API client for incident CRUD. Attaches Firebase Auth token to requests.

#### Import Path Aliases

Frontend uses SvelteKit path aliases:
- `$lib` — resolves to `src/lib/`
- `$app` — resolves to `@sveltejs/kit` (internal SvelteKit modules)

Use these in all imports for cleaner, import-agnostic code.

### Backend (`apps/api/src/`)

- **`domain/`** — Pure Python: Pydantic models, exceptions, domain services. Zero external dependencies.
- **`ports/`** — Protocol interfaces (e.g., `IncidentRepoPort`). Only create ports for real boundaries.
- **`adapters/`** — PostgreSQL (SQLAlchemy), Firebase Auth implementations.
- **`api/`** — FastAPI routes, middleware, dependencies.
- **`config.py`** — Configuration. **`main.py`** — App entrypoint.

### Other directories

- **`specs/`** — Feature specs at repo root. Each numbered directory (e.g., `007-incident-crud-v2/`) contains `spec.md`, `plan.md`, `tasks.md`, and related artifacts. The numeric prefix maps to branch names.
- **`.project/`** — Persistent project history: phase specs, decisions (ADRs), research. Files here are never deleted — obsolete docs go to `.project/archive/`.
- **`tests/unit/`** — Frontend: Vitest with jsdom environment and `$lib`/`$app` path aliases.
- **`apps/api/tests/`** — Backend: pytest with unit, integration, and API test suites.
- **`apps/api/alembic/`** — Database migrations.

### Key files

- `src/hooks.ts` — SvelteKit reroute handler (empty — no i18n)
- `src/hooks.server.ts` — Security headers (HSTS, CSP, X-Frame-Options, Permissions-Policy)
- `src/routes/+page.server.ts` — Server actions (waitlist form: rate limit → Zod validation → Firestore write)
- `src/lib/firebase.ts` — Firebase client SDK init (Auth only, uses `PUBLIC_FIREBASE_*` env vars)
- `src/lib/services/incidents.ts` — Incident API client; uses Firebase Auth token, points to `PUBLIC_API_BASE_URL`
- `src/app.css` — Tailwind 4 `@theme` block with all design tokens (colors, fonts, spacing, shadows)
- `svelte.config.js` — SvelteKit config; adapter-node outputs to `build/` directory (not `dist/`)

## Svelte 5 Conventions

This project uses Svelte 5 runes exclusively (enforced in `svelte.config.js`):

- **Props**: `let { variant = 'primary', children, ...rest } = $props()` — no `export let`
- **State**: `let value = $state('')` — no `$:` reactive declarations
- **Derived**: `let computedVal = $derived(expression)` — replaces `$: computedVal = ...`
- **Children**: Use `{@render children?.()}` snippet pattern, not `<slot />`

## Design Tokens (Tailwind 4)

`app.css` defines a `@theme` block with custom CSS variables consumed as Tailwind utility classes:

- Colors: `bg-bg`, `bg-bg-surface`, `bg-bg-elevated`, `text-text`, `text-text-muted`, `text-accent`, `bg-accent`
- Glow effect: `shadow-glow` token for accent-colored shadows
- Font: Geist via CDN, with size scale defined as CSS variables (`--font-size-xs` through `--font-size-7xl`)

All visual styling must use these tokens — no ad-hoc color/spacing values.

## Code Style

- **Frontend**: Prettier — tabs, single quotes, no trailing commas, 100 char print width. Run `npm run format` to fix.
- **Backend**: Ruff (strict rules) + mypy (strict mode). Run `ruff format` to fix.

## Form Handling Pattern

Server Actions flow: `+page.server.ts` → rate limit check → Zod validation (with email normalization) → Firestore write. Server functions return semantic status codes (`'created'`, `'duplicate'`) rather than throwing. Frontend uses `use:enhance` for progressive enhancement with a state machine (`idle → submitting → success | error | duplicate | rate_limited`).

Adding a new waitlist source (e.g., a new CTA button) requires updating `VALID_SOURCES` in `src/lib/server/schemas.ts` **and** the corresponding test in `tests/unit/server.test.ts`.

## Environment

- **Web runtime:** `FIREBASE_SERVICE_ACCOUNT` (JSON string via GCP Secret Manager), `PORT=3000`
- **Web public env vars (Cloud Run env_vars):** `PUBLIC_API_BASE_URL`, `PUBLIC_FIREBASE_API_KEY`, `PUBLIC_FIREBASE_AUTH_DOMAIN`, `PUBLIC_FIREBASE_PROJECT_ID`, `PUBLIC_FIREBASE_STORAGE_BUCKET`, `PUBLIC_FIREBASE_MESSAGING_SENDER_ID`, `PUBLIC_FIREBASE_APP_ID`
- **API runtime:** `DATABASE_URL` (via Secret Manager secret `THELOOP_API_DATABASE_URL`), `FIREBASE_SERVICE_ACCOUNT`, `CORS_ORIGINS`
- **No `.env` in repo** — all secrets via GCP Secret Manager / GitHub Actions secrets
- **Firestore/Firebase project:** `theloopoute`
- **Cloud SQL instance:** `theloopoute:southamerica-east1:theloop-db` (PostgreSQL 16 + pgvector + pg_trgm)
- **API Cloud Run URL:** `https://theloop-api-1090621437043.us-central1.run.app`

## Deployment

GitHub Actions CI gates (lint → type-check → test → build → Trivy scan → SonarCloud → docs-check) must all pass before merge. Deploy to Cloud Run via Workload Identity Federation on push to `main`. Node 22 in CI.

- **Web CI**: lint + check + test + build + Trivy (`the-loop` Cloud Run)
- **API CI**: ruff + mypy strict + pytest (coverage ≥ 80%) + Docker build + Trivy + SonarCloud (`theloop-api` Cloud Run)

### Code Quality

- **SonarCloud** — Code quality and security scanning integrated in CI pipeline
  - API: Project key `renatobardi_the-loop_api`, organization `renatobardi`
  - Configuration via `sonar-project.properties` in `apps/api/`

## Governance (CONSTITUTION.md)

- Trunk-based development: `main` only via PRs, branch prefixes `feat/`, `fix/`, `hotfix/`, `chore/`. Feature branches for specs use a numeric prefix matching their spec directory (e.g., branch `007-incident-crud-v2` → `specs/007-incident-crud-v2/`)
- Design system tokens are centralized in `lib/ui/` — no ad-hoc styling
- `main` = production (no dev environment — single environment)
- All merges controlled by @renatobardi — sole approver
- Hexagonal architecture applies from Phase 1 onward (backend only)
- Structural changes (new routes, components, architecture) require doc updates in the same PR
- **Mandamento XIII**: ALL dependencies (infra, APIs, backend, DB, secrets, CI/CD) MUST be explicit in the execution plan. Code without its dependencies is broken code.
