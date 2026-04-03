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
- **`routes/login/` and `routes/signup/`** — Firebase email/password auth pages. SSR disabled (client-side only) to avoid server-side Firebase Auth SDK usage.
- **`lib/ui/`** — Design system components (Button, Input, Card, Badge, Container, Section, Navbar, SkipLink, Tabs). Barrel-exported via `index.ts`. Consumes design tokens from `app.css`.
- **`lib/components/`** — Page section components (Hero, Problem, Layers, HowItWorks, Pricing, Footer, WaitlistForm, etc.). All text hardcoded in English.
- **`lib/components/incidents/`** — Incident CRUD components. `IncidentDetail.svelte` is the master incident view with 7 tabs:
  - Details, Operational, Postmortem (core incident fields)
  - Timeline, Responders, Action Items, Attachments (sub-resources with lazy loading)
- **`lib/components/incidents/tabs/`** — Individual tab components. Each implements lazy loading pattern (see "Lazy-Loading Tab Pattern" section).
- **`lib/server/`** — Server-only modules: `firebase.ts` (singleton init), `waitlist.ts` (Firestore write, returns `'created' | 'duplicate'`), `schemas.ts` (Zod with email normalization), `rateLimiter.ts` (5 req/60s per IP).
- **`lib/services/incidents.ts`** — API client for incident CRUD + sub-resources (timeline, responders, action items, attachments). Attaches Firebase Auth token to requests.
- **`lib/stores/auth.ts`** — Svelte store wrapping Firebase `onAuthStateChanged`; exports a `user` store used across authenticated routes.

#### Import Path Aliases

Frontend uses SvelteKit path aliases:
- `$lib` — resolves to `src/lib/`
- `$app` — resolves to `@sveltejs/kit` (internal SvelteKit modules)

Use these in all imports for cleaner, import-agnostic code.

### Backend (`apps/api/src/`)

- **`domain/`** — Pure Python: Pydantic models (`StrEnum` for all enums), typed exceptions, domain services. Zero external dependencies.
- **`ports/`** — Protocol interfaces (e.g., `IncidentRepoPort`). Only create ports for real boundaries.
- **`adapters/postgres/`** — SQLAlchemy ORM row models (`*Row`) + repository implementations. Row models use `Mapped[T]` + `mapped_column()`. Enum values stored as `.value` in DB and reconstructed via `EnumType(row.column)` in the repo.
- **`adapters/firebase/auth.py`** — Firebase token verification. Non-UUID Firebase UIDs are deterministically mapped to UUID5 via `uuid5(NAMESPACE_URL, f"firebase:{uid}")`.
- **`api/`** — FastAPI routes, middleware, dependencies. `middleware.py` implements request ID injection (X-Request-ID header) and slowapi rate limiting. Structured logging via structlog.
- **`api/deps.py`** — Stacked `Depends()` chain: session → repository → service → authenticated user. Each route receives only its specific service.
- **`config.py`** — Configuration. **`main.py`** — App entrypoint with `GET /api/v1/health` check.

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

### Other directories

- **`specs/`** — Feature specs at repo root. Each numbered directory (e.g., `007-incident-crud-v2/`) contains `spec.md`, `plan.md`, `tasks.md`, and related artifacts. The numeric prefix maps to branch names.
- **`.project/`** — Persistent project history: phase specs, decisions (ADRs), research. Files here are never deleted — obsolete docs go to `.project/archive/`.
- **`tests/unit/`** — Frontend: Vitest with jsdom environment and `$lib`/`$app` path aliases.
- **`apps/api/tests/`** — Backend: pytest with `unit/` (domain models/services) and `api/` (route tests with mocked services) suites. The `integration/` directory exists but is currently empty.
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
- **Semantic colors**: `text-accent`, `bg-accent`, `text-error`, `bg-error`, `text-success`, `bg-success`
- **Utility**: `border-border` (for borders), `shadow-glow` (accent-colored glow)
- **Font**: Geist via CDN, with size scale defined as CSS variables (`--font-size-xs` through `--font-size-7xl`)

All visual styling must use these tokens — no ad-hoc color/spacing values. Use opacity modifiers (`/20`, `/50`) for tinted backgrounds.

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

GitHub Actions CI gates (lint → type-check → test → build → Trivy scan → docs-check) must all pass before merge. Deploy to Cloud Run via Workload Identity Federation on push to `main`. Node 22 in CI.

- **Web CI**: lint + check + test + build + Trivy (`the-loop` Cloud Run)
- **API CI**: ruff + mypy strict + pytest (coverage ≥ 80%) + Docker build + Trivy (`theloop-api` Cloud Run)

## Semgrep Integration (Spec-010, Phase A)

The Loop distributes static Semgrep rules (`.semgrep/theloop-rules.yml`) via GitHub Actions workflow. Any project can adopt the rules in minutes by copying two files and running the workflow on each PR.

### GitHub Actions Workflow (`.github/workflows/theloop-guard.yml`)

The workflow executes in 9 steps on every PR to `main`/`master`/`develop`:

**Step 1: Checkout** — Clone PR code with full history (`fetch-depth: 0`)

**Step 2–3: Fetch Rules from API**
- Curl with 5s max-time, 2s connect-timeout to `https://theloop-api-1090621437043.us-central1.run.app/api/v1/rules/{VERSION}`
- `VERSION` defaults to `latest` or reads from GitHub Actions variable `THELOOP_RULES_VERSION`
- On timeout/error: silent fallback to `.semgrep/theloop-rules.yml.bak` (Phase A backup, 6 base rules)
- Output: `/tmp/rules.json` (JSON format from API)

**Step 4: Verify Backup Rules File** — Ensure `.semgrep/theloop-rules.yml.bak` exists (fail if missing; backup is non-negotiable)

**Step 5: Convert JSON to YAML** — Run `python3 scripts/json_to_semgrep_yaml.py` to convert API JSON → Semgrep YAML
- Input: `/tmp/rules.json`
- Output: `.semgrep/theloop-rules.yml` (committed to repo, used by scan)
- Validates schema: checks for 'rules' key, required fields per rule (id, languages, message, severity, patterns)

**Step 6: Validate Semgrep YAML** — Run `semgrep --validate --config .semgrep/theloop-rules.yml` to ensure YAML is well-formed

**Step 7: Run Semgrep Scan** — Execute `semgrep scan --config .semgrep/theloop-rules.yml --json --output /tmp/semgrep-results.json`
- Exit code 0 = no findings; >0 = findings detected (errors OR warnings)
- Results logged to JSON for PR comment

**Step 8: Comment PR with Findings** — GitHub Script to:
- Parse `/tmp/semgrep-results.json`
- Render table: Severity | Rule ID | File | Line | Incident Link
- Count ERROR (critical, blocks merge) vs WARNING (advisory, non-blocking)
- Update existing comment if already present (avoid spam)

**Step 9: Fail on Critical Errors** — If `semgrep_exit != 0`, fail the job
- ERROR findings block merge
- WARNING findings are advisory only

### Rule Set Versions

**Phase A (v0.1.0)** — 6 base rules, multilingual:
- `injection-001-sql-string-concat` (ERROR)
- `injection-002-eval-dynamic-input` (ERROR)
- `unsafe-api-usage-001-shell-injection` (ERROR, Python only)
- `missing-safety-check-001-hardcoded-secret` (ERROR, generic)
- `missing-error-handling-001-bare-except` (WARNING, Python only)
- `unsafe-regex-001-redos-pattern` (WARNING)

**Phase B (v0.2.0)** — 14 additional rules:
- Injection (3): path-traversal, XXE, unsafe deserialization
- Crypto (2): weak MD5, weak random
- Security (3): TLS verify disabled, hardcoded JWT secret, CORS wildcard
- Performance (2): SQL timeout missing, N+1 patterns
- Infrastructure (1): Docker runs as root
- Config (2): hardcoded URLs, DEBUG enabled
- Dependencies (1): known vulnerable dependency

All rules stored in `.semgrep/theloop-rules.yml.bak` (Phase A backup); Phase B rules added on-demand from API.

### Version Pinning

To use a specific version instead of `latest`:

```bash
# GitHub Actions variable (project level)
THELOOP_RULES_VERSION = 0.1.0    # Pins workflow to Phase A rules

# Environment variable (local dev)
THELOOP_RULES_VERSION=0.1.0 python3 scripts/json_to_semgrep_yaml.py --input rules.json --output rules.yml
```

If version not found or API unavailable, automatic fallback to Phase A backup (v0.1.0) ensures continuity.

### JSON→YAML Conversion (`scripts/json_to_semgrep_yaml.py`)

Utility to convert API JSON rules to Semgrep YAML format. Used by the workflow and can be run locally.

**Schema validation** — Checks:
- `rules` key exists + is non-empty list
- Each rule has required fields: `id`, `languages`, `message`, `severity`, `patterns`
- All rule IDs are unique
- Metadata preserved (incident_id, category, CWE, remediation URL)

**Pattern handling**:
- `pattern` — literal string match
- `pattern-either` — list of alternative patterns (OR)
- `pattern-not` — negative patterns (exclude matches)
- `pattern-regex` — regex patterns for generic language rules
- `paths.exclude` — paths to skip (tests, examples, etc.)

**Error handling**:
- `ValueError` — schema validation failure (missing field, duplicate ID)
- `json.JSONDecodeError` — malformed JSON input
- `FileNotFoundError` — input file missing

### Adding New Rules

1. **Define rule in API** — Create incident record in The Loop with:
   - Category (injection, crypto, security, etc.)
   - Pattern (multilingual if possible)
   - Remediation guidance
   - CWE mapping (OWASP reference)

2. **Publish rules** — API endpoint `/api/v1/rules/latest` returns full rule set

3. **Workflow picks up rule** — On next PR:
   - Fetch from API
   - Convert to YAML
   - Scan uses new rule automatically

4. **Rollback (if needed)** — Deprecate bad version:
   - POST `/api/v1/rules/deprecate?version=0.2.0`
   - Workflow fallbacks to last active version (Phase A by default)
   - No merge required; automatic on next PR

### Troubleshooting

**Workflow fails at "Verify backup rules file"**
- `.semgrep/theloop-rules.yml.bak` missing or corrupted
- Restore from repo: `git checkout HEAD~1 .semgrep/theloop-rules.yml.bak`
- Never delete Phase A backup; it's the fallback guarantee

**Workflow fails at "Convert JSON to YAML"**
- API returned invalid JSON (rare, but check API logs)
- Fallback to Phase A kicked in; scan used backup rules
- If persistent, revert to previous version using `THELOOP_RULES_VERSION` variable

**Semgrep finds false positives**
- Add path exclusion to rule (e.g., exclude `*.test.py`)
- Report to The Loop: https://loop.oute.pro/feedback
- Temporarily suppress via `# nosemgrep` comment (not recommended for incidents)

**"Critical findings detected" but code is correct**
- Review Incident metadata in rule (click link in PR comment)
- File GitHub issue with false positive evidence
- Use version pinning to temporarily revert to Phase A

### Local Development

Test rules locally before commit:

```bash
# Install Semgrep
pip install semgrep

# Validate YAML syntax
semgrep --validate --config .semgrep/theloop-rules.yml

# Run scan on codebase
semgrep scan --config .semgrep/theloop-rules.yml

# Convert API JSON to YAML (if updating rules)
python3 scripts/json_to_semgrep_yaml.py --input rules.json --output .semgrep/theloop-rules.yml
```

## Governance (CONSTITUTION.md)

- Trunk-based development: `main` only via PRs, branch prefixes `feat/`, `fix/`, `hotfix/`, `chore/`. Feature branches for specs use a numeric prefix matching their spec directory (e.g., branch `007-incident-crud-v2` → `specs/007-incident-crud-v2/`)
- Design system tokens are centralized in `lib/ui/` — no ad-hoc styling
- `main` = production (no dev environment — single environment)
- All merges controlled by @renatobardi — sole approver
- Hexagonal architecture applies from Phase 1 onward (backend only)
- Structural changes (new routes, components, architecture) require doc updates in the same PR
- **Mandamento XIII**: ALL dependencies (infra, APIs, backend, DB, secrets, CI/CD) MUST be explicit in the execution plan. Code without its dependencies is broken code.
