# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

The Loop — incident prevention platform. Monorepo with two apps:

- **`apps/web/`** — SvelteKit 2 + Svelte 5 (runes), Tailwind CSS 4, Firebase Firestore. English-only. Phase 0: landing page + waitlist. Phase 1: incident CRUD UI. Phase C.1: postmortem capture. Phase C.2: analytics dashboard.
- **`apps/api/`** — Python 3.12 FastAPI backend, SQLAlchemy 2.0 (async), Pydantic v2, PostgreSQL 16 + pgvector. Hexagonal architecture (domain/ports/adapters). Phase 1: incident CRUD. Phase C.1: postmortems API. Phase C.2: analytics API. Phase B: Semgrep rules distribution. Spec-016: API keys, scan history, admin rules.

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
- **asyncio_mode = "auto"** — all async test functions run without explicit `@pytest.mark.asyncio` decorator; configured in `pyproject.toml`.

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

**Alternatively: Cloud SQL Proxy (for cloud-based development)**
```bash
# Binary pre-built in repo root; use port 5433 to avoid Docker conflicts
./cloud-sql-proxy theloopoute:southamerica-east1:theloop-db --port=5433

# In another terminal:
cd apps/api
export DATABASE_URL="postgresql+asyncpg://theloop:theloop@localhost:5433/theloop"
alembic upgrade head
```

For CI tests, a temporary test database is created with the same setup.

## Architecture

### Frontend (`apps/web/src/`)

- **`routes/`** — File-based routing with plain paths. Trailing slashes enforced (`trailingSlash: 'always'` in `+layout.ts`). All routes use plain paths (`/`, `/incidents/`, `/analytics/`, `/constitution/`).
- **`routes/incidents/`** — Incident CRUD pages: list with filters/pagination, `[id]/` detail view, `[id]/edit/` edit form, `new/` create form. Client-side data loading via `+page.ts`.
- **`routes/analytics/`** — Product analytics dashboard. SSR disabled (`ssr = false`). `+page.ts` only parses URL filter params and returns null placeholders; all API calls happen client-side in a `$effect` on `+page.svelte` via `Promise.allSettled` across 7 endpoints (summary, byCategory, byTeam, byTeamAll, timeline, severityTrend, topRules). A generation counter guards against stale results on rapid filter changes.
- **`routes/constitution/`** — Public page rendering the 13 mandamentos (ConstitutionHero + MandatesGrid + TransparencySection components).
- **`routes/login/` and `routes/signup/`** — Firebase email/password auth pages. SSR disabled (client-side only) to avoid server-side Firebase Auth SDK usage.
- **`lib/ui/`** — Design system components (Button, Input, Card, Badge, Container, Section, Navbar, SkipLink, Tabs). Barrel-exported via `index.ts`. Consumes design tokens from `app.css`.
- **`lib/components/`** — Page section components (Hero, Problem, Layers, HowItWorks, Pricing, Footer, WaitlistForm, etc.). All text hardcoded in English.
- **`lib/components/incidents/`** — Incident CRUD components. `IncidentDetail.svelte` is the master incident view with 7 tabs:
  - Details, Operational, Postmortem (core incident fields)
  - Timeline, Responders, Action Items, Attachments (sub-resources with lazy loading)
- **`lib/components/incidents/tabs/`** — Individual tab components. Each implements lazy loading pattern (see "Lazy-Loading Tab Pattern" section).
- **`lib/components/analytics/`** — Analytics dashboard components: `DashboardGrid.svelte` (layout + data distribution to all sub-components), `SummaryCard.svelte` (8 KPI cards in 2×4 grid), `CategoryHeatmap.svelte`, `TeamHeatmap.svelte`, `PatternTimeline.svelte`, `SeverityTrendChart.svelte` (stacked SVG area chart, pure-SVG no charting lib), `RuleEffectivenessCard.svelte`, `AnalyticsFilters.svelte`, `MultiSelectDropdown.svelte` (accessible multi-select with click-outside dismiss; props: `id`, `label`, `options`, `selected[]`, `placeholder`, `onchange`).
- **`lib/server/`** — Server-only modules: `firebase.ts` (singleton init), `waitlist.ts` (Firestore write, returns `'created' | 'duplicate'`), `schemas.ts` (Zod with email normalization), `rateLimiter.ts` (5 req/60s per IP).
- **`lib/services/incidents.ts`** — API client for incident CRUD + sub-resources (timeline, responders, action items, attachments). Attaches Firebase Auth token to requests.
- **`lib/services/analytics.ts`** — API client for analytics endpoints (`/api/v1/incidents/analytics/*`). Returns `SummaryResponse`, `TimelinePoint[]`, `CategoryStats[]`, `TeamStats[]`, `SeverityTrendPoint[]`, `RuleEffectiveness[]`. Supports `AnalyticsFilter` (period, custom date range, team, category, severity).
- **`lib/stores/auth.ts`** — Svelte store wrapping Firebase `onAuthStateChanged`; exports a `user` store used across authenticated routes.

#### Import Path Aliases

Frontend uses SvelteKit path aliases (also configured in `tsconfig.json`):
- `$lib` — resolves to `src/lib/`
- `$app` — resolves to `@sveltejs/kit` (internal SvelteKit modules)

Always use these aliases. Never use relative imports (`../../../lib`). This keeps code portable if directory structure changes.

### Backend (`apps/api/src/`)

- **`domain/`** — Pure Python: Pydantic models (`StrEnum` for all enums), typed exceptions, domain services. Zero external dependencies.
- **`ports/`** — Protocol interfaces (e.g., `IncidentRepoPort`). Only create ports for real boundaries.
- **`adapters/postgres/`** — SQLAlchemy ORM row models (`*Row`) + repository implementations. Row models use `Mapped[T]` + `mapped_column()`. Enum values stored as `.value` in DB and reconstructed via `EnumType(row.column)` in the repo.
- **`adapters/firebase/auth.py`** — Firebase token verification. Non-UUID Firebase UIDs are deterministically mapped to UUID5 via `uuid5(NAMESPACE_URL, f"firebase:{uid}")`.
- **`api/`** — FastAPI routes, middleware, dependencies. `middleware.py` implements request ID injection (X-Request-ID header) and slowapi rate limiting. Structured logging via structlog.
- **`api/deps.py`** — Stacked `Depends()` chain: session → repository → service → authenticated user. Each route receives only its specific service. Auth tiers: `ApiKeyIdentity` (API key auth for scanner workflow), `get_optional_identity` (public endpoints that accept either Firebase or API key). New routes: `/api/v1/api-keys` (CRUD for API keys), `/api/v1/scans` (scan history ingestion and retrieval). Analytics: `get_analytics_cache()` injects a singleton `AnalyticsCache` instance; `get_analytics_service()` receives both the repo and cache.
- **`config.py`** — Configuration. **`main.py`** — App entrypoint with `GET /api/v1/health` check.
- **`domain/models.py`** — includes `ApiKey` and `Scan` domain models (Spec-016).

#### Auth Tiers (apply to every new endpoint)

Every new route must explicitly decide its auth tier — never leave it implicit:

| Tier | Dependency | Who calls it | What they get |
|---|---|---|---|
| Anonymous | none / `get_optional_identity` returning `None` | Public browsers | No extras (public read-only only) |
| API key (`tlp_…`) | `get_optional_identity` returning `ApiKeyContext` | Scanner CI workflow | Rule whitelist scoped to project |
| Firebase JWT | `get_firebase_token_data` | Authenticated users | Full access to their data |
| Admin | `require_admin` | Firebase user with `is_admin=True` | Admin operations (rule publishing, etc.) |

`get_optional_identity` in `api/deps.py` dispatches on token prefix: `tlp_` → API key path, `eyJ` → Firebase JWT path, no header → `None`. Routes that serve both scanner and browser traffic use this dependency and branch on the return type.

#### Rules Endpoints & Whitelist Filtering

Rules distribution endpoints follow a consistent pattern:

- **`GET /api/v1/rules/{VERSION}`** — Fetch specific rule version (JSON). Authenticating with API key filters to project whitelist; unauthenticated returns all rules.
- **`GET /api/v1/rules/latest`** — Fetch latest active version (JSON). Same filtering. **Cache requirement**: validates cache is populated before returning (prevents empty responses on cache miss).
- **`GET /api/v1/rules/active`** — List all active versions (JSON metadata). Admin-only endpoint.
- **Public rule browser**: `/rules/[version]/` renders rule details via client-side fetch to above endpoints (no auth required for read).

Whitelist filtering: API key context includes project ID; repository `get_rules()` filters `rules_allowed_in` list (Spec-016 feature). Always use `in` operator, not `not in`, to avoid false positives.

#### Repository Transaction Pattern

Always call `await session.commit()` after `await session.flush()` in repository write methods. `flush()` sends SQL to the DB within the transaction but does **not** persist — without `commit()`, data is silently lost on session close. This caused a production incident (PR #75).

#### `from __future__ import annotations` + slowapi Incompatibility

`from __future__ import annotations` makes all annotations strings at runtime (PEP 563), which breaks slowapi's decorator introspection. **Do not add this import to any file that uses `@limiter.limit()`** (route files). In `deps.py`, forward references that would trigger `UP037` (use `X | Y` instead of `"X | Y"`) are suppressed with `# noqa: UP037` on string-annotated dependencies — this is intentional. Integration tests require `NullPool` for asyncpg (`create_async_engine(..., poolclass=NullPool)`) to avoid connection reuse across test transactions.

#### Sub-Resource Hexagonal Pattern

All sub-resources (timeline events, responders, action items, attachments) follow the same layering:

1. **Domain model** (`domain/models.py`) — Pydantic model with StrEnum fields
2. **Typed exception** (`domain/exceptions.py`) — e.g., `TimelineEventNotFoundError(event_id: str)`
3. **Port** (`ports/`) — Protocol with 3–5 async methods
4. **ORM row** (`adapters/postgres/models.py`) — `*Row` dataclass with `DateTime(timezone=True)` timestamps and UTC lambda defaults
5. **Repository** (`adapters/postgres/*_repository.py`) — `_row_to_domain()` helper + async repo class
6. **Service** (`domain/services.py`) — thin orchestrator; raises domain exceptions, never HTTP errors
7. **Route** (`api/routes/*.py`) — `*CreateRequest`/`*UpdateRequest`/`*Response` Pydantic models; `Response.from_domain()` classmethod; `_get_incident_or_404()` helper validates parent before each operation; `@limiter.limit("60/minute")` on every endpoint

List endpoints return `{"items": [...], "total": N}` (no cursor/page for sub-resources). The incidents table uses soft deletes (`deleted_at`); sub-resource tables do not. Incident updates use optimistic locking via a `version` field (`OptimisticLockError` if mismatch).

#### Analytics Cache Pattern (Spec-019)

`AnalyticsCache` (`adapters/postgres/analytics_cache.py`) is an in-memory dict with 5-minute TTL, keyed by sorted parameter tuple. All 6 analytics service methods (`get_summary`, `get_by_category`, `get_by_team`, `get_timeline`, `get_severity_trend`, `get_top_rules`) wrap their repo calls with cache logic. Injected via `get_analytics_cache()` in `api/deps.py`, following the same pattern as `rule_version_cache_instance`.

#### Postmortem Sub-Resource (Spec-013)

Postmortems follow the same hexagonal pattern but with key differences:
- **1-per-incident** constraint: `PostmortumAlreadyExistsError` on duplicate create; use PUT to update
- **Locking**: `PostmortumLockedError` if attempting to edit after `locked_at` is set
- **Templates**: `adapters/postgres/postmortem_templates.py` ships hardcoded templates (e.g., "5-Whys", "Fishbone") returned by `GET /api/v1/incidents/{id}/postmortems/templates`
- **AI summary**: async-ready `summary` field (currently set manually); `RootCauseCategory` StrEnum drives categorization

### Other directories

- **`specs/`** — Feature specs at repo root. Each numbered directory (e.g., `007-incident-crud-v2/`) contains `spec.md`, `plan.md`, `tasks.md`, and related artifacts. The numeric prefix maps to branch names. Branch naming: `feat/{NUMBER}-{slug}` (e.g., `feat/017-rules-expansion`).
- **`.project/`** — Persistent project history: phase specs, decisions (ADRs), research. Files here are never deleted — obsolete docs go to `.project/archive/`.
- **`tests/unit/`** — Frontend: Vitest with jsdom environment and `$lib`/`$app` path aliases.
- **`apps/api/tests/`** — Backend: pytest with `unit/` (domain models/services) and `api/` (route tests with mocked services) suites. The `integration/` directory exists but is currently empty.
- **`apps/api/alembic/`** — Database migrations.
- **`scripts/`** — Utility scripts for deployment and build tasks (see "Scripts" section below).
- **`.semgrep/`** — Semgrep rules (YAML) and fallback bundles (`.bak` files).

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
- **Effects**: Use `$effect()` with guards to defer side effects (e.g., API calls) until conditions are met

## Lazy-Loading Tab Pattern (Spec-009)

Sub-resource tabs (Timeline, Responders, Action Items, Attachments) implement lazy loading to avoid unnecessary API calls:

**Parent component** (`IncidentDetail.svelte`):
```svelte
<TimelineTab incidentId={incident.id} active={activeTab === 'timeline'} />
```

**Tab component** (e.g., `TimelineTab.svelte`):
```svelte
let { incidentId, active } = $props();
let loaded = $state(false);

$effect(() => {
  if (active && !loaded) {
    load(); // Fetch data only when tab becomes active
  }
});
```

**Key patterns:**
- Parent passes `incidentId` (not full incident object) + `active={boolean}` prop
- Tab uses `$effect()` guard: only fetch if `active && !loaded`
- Prevents duplicate API calls and reduces initial page load time
- All error/empty states rendered in English with design tokens only

## Design Tokens (Tailwind 4)

`app.css` defines a `@theme` block with custom CSS variables consumed as Tailwind utility classes:

- **Backgrounds**: `bg-bg`, `bg-bg-surface`, `bg-bg-elevated`
- **Text colors**: `text-text`, `text-text-muted`
- **Semantic colors**: `text-accent`, `bg-accent`, `text-error`, `bg-error`, `text-success`, `bg-success`, `text-warning`, `bg-warning`
- **Chart palette**: `bg-chart-blue`, `bg-chart-purple`, `bg-chart-error`, `bg-chart-warning`, `bg-chart-green`
- **Utility**: `border-border` (for borders), `shadow-glow` (accent-colored glow)
- **Font**: Geist via CDN, with size scale defined as CSS variables (`--font-size-xs` through `--font-size-7xl`)

Badge variants: `default`, `accent`, `success`, `error`, `warning`.

All visual styling must use these tokens — no ad-hoc color/spacing values. Use opacity modifiers (`/20`, `/50`) for tinted backgrounds.

## Code Style

- **Frontend**: Prettier — tabs, single quotes, no trailing commas, 100 char print width. Run `npm run format` to fix.
- **Backend**: Ruff (strict rules) + mypy (strict mode). Run `ruff format` to fix.
  - **Ruff**: Enforces strict linting. Ignores `S101` (assertions in tests) and `B008` (FastAPI `Depends()` in default parameters — canonical pattern). The field `_Date` in `domain/models.py` uses leading underscore to avoid Pydantic 2.11 field-name shadowing.
  - **MyPy**: Strict mode enabled with Pydantic plugin (`init_forbid_extra = true`). Some dynamic typing is unavoidable in serialization layers—prefer explicit type casts over `# type: ignore` comments.

## Common Gotchas

- **Transaction commits** (PR #75 lesson): Always call `await session.commit()` after `await session.flush()` in repository write methods. Without `commit()`, data is silently lost on session close.
- **Rate limiting + slowapi**: Never add `from __future__ import annotations` to route files (`api/routes/*.py`) — it breaks slowapi's decorator introspection.
- **API key filtering**: Use `in` operator when filtering rules by whitelist (`if rule_id in allowed_rules`), not `not in` — prevents false positives.
- **Lazy-loading tabs**: Always pass `incidentId` (not full object) and `active` boolean to tab components — prevents unnecessary API calls and race conditions.
- **SSR window access in services**: Always guard `window` access in service modules (e.g., `lib/services/analytics.ts`) with `typeof window !== 'undefined'`. Services are imported in server contexts during build/rendering. Use explicit checks, not optional chaining on `window.location`.
- **$derived in load functions race conditions** (Spec-019): Do not use `$derived()` on values computed in `+page.ts` load functions. The race between server-side computation and client-side rune initialization can cause stale data. Pass computed values as props instead.
- **Async code in rune effects**: When wrapping async operations in `$effect()`, use an IIFE pattern to isolate the async scope and avoid dangling promises:
  ```svelte
  $effect(() => {
    (async () => {
      if (condition && !loaded) {
        data = await fetch(...);
        loaded = true;
      }
    })();
  });
  ```
  Avoids cleanup complications and simplifies cancellation logic.
- **AbortSignal.timeout vs shared AbortController in analytics**: Use `AbortSignal.timeout(ms)` (static, per-request, fire-and-forget) for fetch timeouts in `lib/services/analytics.ts`. Never use a shared `AbortController` across parallel requests — cancelling it aborts all in-flight fetches simultaneously, which breaks the page on filter changes. For stale-result protection, use a plain generation counter (`let gen = ++loadGeneration`) instead of AbortController.

## Scripts

Helper scripts for deployment, build, and rules management:

- **`scripts/json_to_semgrep_yaml.py`** — Converts API JSON rule format to YAML for local testing and bundling. Usage: `python3 scripts/json_to_semgrep_yaml.py --input rules.json --output output.yml`
- **`scripts/publish_v<VERSION>.py`** — Publishes a new rule version (e.g., `publish_v030.py` for v0.3.0). Inserts rules into database and marks version as active for CI use.
- **`scripts/generate-docs.sh`** — Generates API documentation from route docstrings. Required to pass CI `docs-check` gate. Run: `bash scripts/generate-docs.sh`

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
- **API Cloud Run URL:** `https://api.loop.oute.pro`

## Deployment

GitHub Actions CI gates (lint → type-check → test → build → Trivy scan → docs-check) must all pass before merge. Deploy to Cloud Run via Workload Identity Federation on push to `main`. Node 22 in CI.

- **Web CI**: lint + check + test + build + Trivy (`the-loop` Cloud Run)
- **API CI**: ruff + mypy strict + pytest (coverage ≥ 80%) + Docker build + Trivy (`theloop-api` Cloud Run)

## Semgrep Integration (Specs 010–011–016–017–018, Phases A, B, C & Multi-Language)

The Loop distributes Semgrep rules via API. The CI workflow (`.github/workflows/theloop-guard.yml`) runs on every PR: fetches rules from `GET /api/v1/rules/{VERSION}`, converts JSON → YAML via `scripts/json_to_semgrep_yaml.py`, then scans. Falls back to `.semgrep/theloop-rules.yml.bak` (Phase A, 6 base rules) on API timeout.

- **ERROR** findings block merge; **WARNING** findings are advisory only
- **Phase A (v0.1.0)**: 6 rules — SQL injection, eval, shell injection, hardcoded secrets, bare except, ReDoS
- **Phase B (v0.2.0)**: 14 additional rules — path traversal, XXE, weak crypto, TLS disabled, CORS wildcard, N+1, Docker root, DEBUG enabled, etc.
- **Phase C (v0.3.0)**: 25 new rules — 15 JS/TS + 10 Go (injection, crypto, security, performance, error handling). **Total: 45 rules.**
- **Spec-017/018 (Multi-Language)**: Expansion to Java, C#, PHP, Ruby, Kotlin, Rust, C/C++ (~78 additional rules, versioned as v0.4.0+)

### Version Pinning & Rules Lifecycle

- Version pinning: set GitHub Actions variable `THELOOP_RULES_VERSION=0.1.0` to pin to Phase A; default uses latest
- Rules database: each version stored in `api/adapters/postgres/models.py:RuleVersionRow` with `active` flag
- Publishing new version: run `python scripts/publish_v<VERSION>.py` to insert rules and set as active
- Never delete `.semgrep/theloop-rules.yml.bak` — it's the non-negotiable fallback
- API rate limiting: rules cache invalidates on new active version publish (see `api/services/rules_service.py`)

### Test Data Organization (Rules Expansion)

For Spec-017/018 multi-language coverage:
- **Bad examples:** `tests/test-data/bad/<lang>/` (e.g., `tests/test-data/bad/java/`, `tests/test-data/bad/rust/`)
- **Good examples:** `tests/test-data/good/<lang>/` (demonstrates correct patterns)
- Validate rules locally: `semgrep --validate --config rules.yml`
- Scan test data: `semgrep scan --config rules.yml tests/test-data/`

### Public Rule Browser & Scan History

- Public rule browser: `loop.oute.pro/rules/latest` (no auth required); filtered by API key whitelist if authenticated
- Scan history: each workflow run posts to `POST /api/v1/scans` (best-effort, `continue-on-error: true`)
- Cache management: `/api/v1/rules/latest` validates cache is populated before returning

```bash
# Local rule testing
semgrep --validate --config .semgrep/theloop-rules.yml
semgrep scan --config .semgrep/theloop-rules.yml
python3 scripts/json_to_semgrep_yaml.py --input rules.json --output .semgrep/theloop-rules.yml
```

## Speckit Workflow (Feature Specs)

Feature planning follows a structured spec → plan → tasks workflow. Each numbered spec directory contains three documents:

1. **`spec.md`** — Feature requirements, scope, acceptance criteria. Status field indicates kickoff readiness.
2. **`plan.md`** — Implementation strategy, architecture decisions, file/component changes, phases, dependencies.
3. **`tasks.md`** — Executable, dependency-ordered task list (T001, T002, etc.) with completion tracking.

Working on a spec:
- Create branch: `feat/{NUMBER}-{slug}` (e.g., `feat/017-rules-expansion`)
- Review all three docs before implementing
- Each task is claimed and tracked via `tasks.md` status
- On completion, commit all changes (spec artifacts + code) in a single PR
- Spec directory and branch name must stay synchronized

## Current Sprint

No active sprint. All specs complete.

### Phase Status (as of April 2026)

| Phase | Status | Key Deliverables |
|-------|--------|------------------|
| Phase 0 | ✅ Complete | Landing page, waitlist, constitution |
| Phase 1 | ✅ Complete | Incident CRUD (all auth + data flows) |
| Phase C.1 | ✅ Complete | Postmortem workflow + locking |
| Phase C.2 | ✅ Complete | Analytics dashboard (timeline, category, team stats) |
| Phase B | ✅ Complete | Semgrep integration (45 rules, v0.1.0 → v0.3.0) |
| Spec-015 | ✅ Complete | Nav/Dashboard/Profile (PR #70) |
| Spec-016 | ✅ Complete | Semgrep Platform (9 phases, PR #79) |
| Spec-017 | ✅ Complete | Rules Expansion (10 languages, 122 rules total, v0.4.0 deployed, PR #95) |
| Spec-018 | ✅ Complete | Consolidated into Spec-017 |
| Spec-019 | ✅ Complete | Product Analytics Dashboard (7 phases, PRs #101–#104) |

## Governance (CONSTITUTION.md)

- Trunk-based development: `main` only via PRs, branch prefixes `feat/`, `fix/`, `hotfix/`, `chore/`. Feature branches for specs use a numeric prefix matching their spec directory: `feat/017-rules-expansion` → `specs/017-rules-expansion/`. This ensures spec directory and branch name stay synchronized.
- Design system tokens are centralized in `lib/ui/` — no ad-hoc styling
- `main` = production (no dev environment — single environment)
- All merges controlled by @renatobardi — sole approver
- Hexagonal architecture applies from Phase 1 onward (backend only)
- Structural changes (new routes, components, architecture) require doc updates in the same PR
- **Mandamento XIII**: ALL dependencies (infra, APIs, backend, DB, secrets, CI/CD) MUST be explicit in the execution plan. Code without its dependencies is broken code.
