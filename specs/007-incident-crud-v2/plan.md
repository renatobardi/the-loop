# Implementation Plan: Incident Module — CRUD (Phase A, Revised)

**Branch**: `007-incident-crud-v2` | **Date**: 2026-03-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/007-incident-crud-v2/spec.md`
**Supersedes**: `006-incident-crud/plan.md` — adds infrastructure tasks (Mandamento XIII), removes i18n, refactors existing code.

## Summary

Deliver the incident CRUD module to production by addressing the gaps from 006: (1) provision all GCP infrastructure (Cloud SQL, Cloud Run for API, Artifact Registry, Secret Manager, IAM), (2) update CI/CD pipelines for the Python backend, (3) remove Paraglide i18n from the entire app (English-only), (4) refactor existing frontend code to plain English with simplified routing.

> **Phase mapping (plan → tasks)**: This plan has 5 phases. tasks.md expands plan Phase 3 into three separate task phases for granularity: tasks Phase 3 = i18n infra/config, tasks Phase 4 = landing page components, tasks Phase 5 = incident components. plan Phase 4 maps to tasks Phase 6; plan Phase 5 maps to tasks Phase 7.

> **Backend changes made during implementation**: Although the original plan stated "backend code requires ZERO changes," the following were necessary during CI validation: (1) removed `from __future__ import annotations` from `routes/incidents.py` — slowapi's decorator wrapper was causing FastAPI to see ForwardRef strings instead of resolved types, misclassifying Pydantic body params as query params; (2) changed `request: object` → `request: Request` in all route handlers (required by FastAPI 0.128.5); (3) upgraded fastapi 0.115.12→0.128.5 and pinned starlette≥0.49.1 to fix CVE-2025-62727; (4) added pytest-cov and new tests (test_services.py, test_incidents.py) to reach the 80% coverage threshold. These changes do not affect the domain model or API contract.

## Technical Context

**Language/Version**: Python 3.12 (backend — already implemented), TypeScript 5.x (frontend — refactor only)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, asyncpg (backend); SvelteKit 2.50, Svelte 5, Tailwind CSS 4 (frontend)
**Storage**: PostgreSQL 16 + pgvector extension (embedding column nullable, no HNSW index in Phase A)
**Testing**: pytest + pytest-asyncio (backend), vitest (frontend unit)
**Target Platform**: GCP Cloud Run (two services: web + api)
**Project Type**: Web application (API + SPA frontend)
**Performance Goals**: List page < 2s for 10k incidents, create-to-visible < 5s, keyword search < 2s
**Constraints**: Single-tenant, no role-based auth, 60 req/min per user rate limit, English-only
**Scale/Scope**: Up to 10,000 incidents in Phase A, single Cloud Run instance per service

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Mandamento | Status | Notes |
| ---------- | ------ | ----- |
| I. Trunk-Based Development | PASS | Feature branch `007-incident-crud-v2`, will merge to `main` via PR |
| II. Design System Imutável | PASS | Frontend uses existing design tokens from `apps/web/src/lib/ui/` and `app.css` |
| III. Taxonomia de Branches | PASS | Branch `007-incident-crud-v2` uses numeric spec prefix convention instead of the `feat/fix/hotfix/chore/` taxonomy. Exception explicitly documented in CLAUDE.md: "Feature branches for specs use a numeric prefix matching their spec directory (e.g., branch `007-incident-crud-v2` → `specs/007-incident-crud-v2/`)." Governance decision by @renatobardi. The constitution taxonomy governs all non-spec branches. A formal exception clause in the constitution (MINOR amendment) is recommended for future versions. |
| IV. Main Protegida | PASS | PR required, @renatobardi sole approver |
| V. Merge Controlado | PASS | @renatobardi merges |
| VI. Sem Ambiente de Dev | PASS | Single environment (production), no staging |
| VII. CI Rigoroso | PASS | New `api-quality` CI job with ruff, mypy strict, pytest, Docker build, Trivy. Existing web quality job updated (remove Paraglide step) |
| VIII. Segurança Mandatória | PASS | Firebase Auth, rate limiting, input validation (Pydantic+Zod), no hardcoded secrets, Workload Identity Federation, IAM least privilege |
| IX. Clean Code | PASS | Small functions, typed exceptions, descriptive names, tests as docs |
| X. Arquitetura Hexagonal | PASS | Domain (Pydantic) → Port (Protocol) → Adapter (SQLAlchemy). See Complexity Tracking for boundary justification |
| XI. Pasta .project/ | PASS | Phase docs in `specs/007-incident-crud-v2/`, historical copy to `.project/phases/01-incidents/` on merge |
| XII. Documentação e Código | PASS | README updates, API docs (FastAPI auto-generated), docs-check gate updated |
| **XIII. Dependências no Plano** | **PASS** | **Infrastructure provisioning (Cloud SQL, Cloud Run, Artifact Registry, Secret Manager, IAM) explicitly in Phase 1 tasks BEFORE code deployment. CI/CD updates in Phase 2. This was the critical gap in 006.** |

## Project Structure

### Documentation (this feature)

```text
specs/007-incident-crud-v2/
├── spec.md
├── plan.md              # This file
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Generated by /speckit.tasks
```

### Source Code (repository root)

```text
apps/api/                          # EXISTING — FastAPI backend (no code changes needed)
├── alembic/
│   ├── versions/
│   │   └── 001_create_incidents_table.py
│   └── env.py
├── src/
│   ├── domain/
│   │   ├── models.py              # Incident (frozen Pydantic), Category, Severity enums
│   │   ├── exceptions.py          # IncidentNotFoundError, DuplicateSourceUrlError, etc.
│   │   └── services.py            # IncidentService (orchestrates domain logic)
│   ├── ports/
│   │   └── incident_repo.py       # IncidentRepoPort (Protocol)
│   ├── adapters/
│   │   ├── postgres/
│   │   │   ├── models.py          # SQLAlchemy ORM model
│   │   │   ├── repository.py      # IncidentRepoPort implementation
│   │   │   └── session.py         # AsyncSession factory
│   │   └── firebase/
│   │       └── auth.py            # Firebase token verification
│   ├── api/
│   │   ├── routes/
│   │   │   └── incidents.py       # CRUD route handlers
│   │   ├── deps.py                # Shared FastAPI dependencies
│   │   └── middleware.py          # Rate limiting, request ID, logging
│   ├── config.py                  # Pydantic BaseSettings
│   └── main.py                    # App factory
├── tests/
│   ├── unit/                      # Domain logic (no DB)
│   ├── integration/               # Repo adapter (real PostgreSQL)
│   ├── api/                       # FastAPI TestClient
│   └── conftest.py                # Shared fixtures
├── alembic.ini
├── pyproject.toml
├── requirements.txt
├── README.md
└── Dockerfile

apps/web/                          # EXISTING — SvelteKit frontend (REFACTOR: strip i18n)
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   ├── incidents/         # EXISTING — strip i18n imports, hardcode English
│   │   │   │   ├── IncidentDetail.svelte
│   │   │   │   ├── IncidentForm.svelte
│   │   │   │   ├── IncidentFilters.svelte
│   │   │   │   ├── IncidentCard.svelte
│   │   │   │   ├── DeleteConfirmModal.svelte
│   │   │   │   └── Pagination.svelte
│   │   │   ├── Hero.svelte        # REFACTOR — hardcode English
│   │   │   ├── Problem.svelte     # REFACTOR — hardcode English
│   │   │   ├── Layers.svelte      # REFACTOR — hardcode English
│   │   │   ├── HowItWorks.svelte  # REFACTOR — hardcode English
│   │   │   ├── Pricing.svelte     # REFACTOR — hardcode English
│   │   │   ├── Footer.svelte      # REFACTOR — hardcode English
│   │   │   ├── WaitlistForm.svelte # REFACTOR — hardcode English
│   │   │   ├── WaitlistCta.svelte  # REFACTOR — hardcode English
│   │   │   └── LanguageSelector.svelte  # DELETE — no longer needed
│   │   ├── services/
│   │   │   └── incidents.ts       # EXISTING — wire Firebase Auth token
│   │   └── types/
│   │       └── incident.ts        # EXISTING — no changes needed
│   ├── routes/
│   │   ├── +layout.svelte         # REFACTOR — remove ParaglideJS wrapper
│   │   ├── +layout.ts             # Keep — trailingSlash: 'always'
│   │   ├── +page.server.ts        # Keep — waitlist form actions
│   │   ├── +page.svelte           # Keep — landing page
│   │   ├── constitution/          # REFACTOR — strip i18n
│   │   └── incidents/             # EXISTING — strip i18n, already plain paths
│   │       ├── +layout.svelte
│   │       ├── +layout.ts
│   │       ├── +page.svelte       # List page
│   │       ├── +page.ts
│   │       ├── new/
│   │       │   └── +page.svelte   # Create form
│   │       └── [id]/
│   │           ├── +page.svelte   # Detail view
│   │           ├── +page.ts
│   │           └── edit/
│   │               ├── +page.svelte # Edit form
│   │               └── +page.ts
│   ├── hooks.ts                   # REFACTOR — remove Paraglide reroute
│   └── hooks.server.ts            # Keep — security headers
├── messages/                      # DELETE — all 3 JSON files
├── project.inlang/                # DELETE — Paraglide config
└── ...

FILES TO DELETE:
├── apps/web/messages/en.json
├── apps/web/messages/pt.json
├── apps/web/messages/es.json
├── apps/web/src/lib/i18n.ts
├── apps/web/src/lib/paraglide/    # Auto-generated, gitignored but clean up
├── apps/web/src/lib/components/LanguageSelector.svelte
├── apps/web/project.inlang/       # Paraglide project config
└── apps/web/src/params/lang.ts    # If exists (param matcher)
```

**Structure Decision**: Two-app monorepo (`apps/api/` + `apps/web/`). Backend is a separate FastAPI service with its own Dockerfile, deployed as a second Cloud Run service. Frontend calls API via Vite dev proxy (development) or Cloud Run service URL (production).

## Complexity Tracking

| Boundary | Why Needed | Simpler Alternative Rejected Because |
|----------|-----------|--------------------------------------|
| IncidentRepoPort (Protocol) | Isolates domain logic from PostgreSQL. Enables pure unit tests for validation, optimistic locking, soft-delete rules without a database. | Direct SQLAlchemy in service — violates Mandamento X, makes domain logic untestable without DB. Predecessor (oute-muscle) validated this exact port pattern. |

## Execution Phases

### Phase 1: Infrastructure Provisioning (Mandamento XIII)

**Purpose**: Provision all GCP resources BEFORE any code deployment. Executed by @renatobardi via `gcloud` CLI.

**Dependency chain**: Cloud SQL → Secrets → Artifact Registry → IAM → Cloud Run → CI/CD

1. **Cloud SQL**: Create PostgreSQL 16 instance with pgvector, create database, run Alembic migration
2. **Secret Manager**: Store `DATABASE_URL` (Cloud SQL connection string) and `FIREBASE_SERVICE_ACCOUNT`
3. **Artifact Registry**: Create repository for API Docker images
4. **IAM**: Create service account `theloop-api-sa` with Cloud SQL Client + Secret Manager Accessor roles
5. **Cloud Run**: Deploy API service with service account, Cloud SQL connection, secret mounts

### Phase 2: CI/CD Pipeline Updates

**Purpose**: Ensure both services have quality gates and automated deployment.

1. **ci.yml**: Add `api-quality` job (ruff, mypy, pytest with PostgreSQL service container, Docker build, Trivy). Remove Paraglide compile from web quality job.
2. **deploy.yml**: Add API Docker build → Artifact Registry push → Cloud Run deploy for `theloop-api`.
3. **docs-check**: Update `scripts/generate-docs.sh` to remove i18n-related checks, add API checks.

### Phase 3: i18n Removal (Entire App)

**Purpose**: Strip all Paraglide/i18n infrastructure and hardcode English text.

1. **Delete i18n infrastructure**: message files, Paraglide config, i18n.ts, LanguageSelector component
2. **Update build config**: Remove Paraglide Vite plugin, remove `@inlang/paraglide-sveltekit` dependency
3. **Refactor root layout**: Remove `<ParaglideJS>` wrapper, remove Paraglide imports
4. **Refactor hooks**: Remove `reroute` export from `hooks.ts`
5. **Refactor landing page components** (~13 files): Replace `message_key()` calls with English strings from `en.json`
6. **Refactor incident components** (~6 files): Replace `message_key()` calls with English strings
7. **Refactor constitution components**: Strip i18n imports
8. **Remove `resolveRoute` calls**: Replace with plain `href` paths throughout

### Phase 4: Frontend Fixes & Auth Wiring

**Purpose**: Fix the broken frontend (blank page) and wire Firebase Auth for API calls.

1. **Wire Firebase Auth client-side**: Initialize Firebase client SDK, implement `getAuthToken()` in `incidents.ts` service
2. **Evaluate `ssr = false`** in incidents layout: Consider if SSR is needed for graceful degradation (FR-024)
3. **Add error boundaries**: Frontend must show clear error state when API is unreachable (FR-024, SC-009)
4. **Test CRUD flow end-to-end**: Verify create → list → detail → edit → delete works against running API

### Phase 5: Documentation & Polish

**Purpose**: Update all docs, run CI gates, validate production readiness.

1. **Update CLAUDE.md**: Remove i18n sections, update routing docs, update commands (remove Paraglide compile)
2. **Update root README.md**: Remove i18n references, update architecture section
3. **Update `apps/api/README.md`**: Verify accuracy
4. **Update `apps/web/README.md`**: Remove i18n references if present
5. **Run `scripts/generate-docs.sh`**: Ensure docs-check gate passes
6. **Run all CI gates locally**: Backend (ruff, mypy, pytest) + Frontend (lint, check, test, build)
7. **Validate quickstart.md**: Follow steps end-to-end

## Dependencies & Execution Order

### Phase Dependencies (STRICT — Mandamento XIII)

```
Phase 1: Infrastructure ──► Phase 2: CI/CD ──► Phase 3: i18n Removal ──► Phase 4: Frontend Fixes ──► Phase 5: Docs
     │                           │                    │                         │
     │                           │                    │                         └─ Depends on i18n removal + infra
     │                           │                    └─ Can start after CI/CD (independent of infra for code changes)
     │                           └─ Depends on infra (PostgreSQL service container needs Cloud SQL config reference)
     └─ No dependencies — start here
```

### Critical Path

1. **Infrastructure MUST be provisioned first** — no API deploy without Cloud SQL, secrets, IAM
2. **CI/CD MUST be updated before merging code** — no code merges without all quality gates
3. **i18n removal can proceed in parallel with infra** (code-only, no infra dependency) but MUST be complete before merge
4. **Frontend fixes depend on working API** — needs infra + backend deployed to test e2e

### Parallel Opportunities

- Phase 1 (infra) and Phase 3 (i18n removal) can proceed in parallel — different workstreams
- Within Phase 3: landing page refactoring and incident component refactoring are independent
- Phase 5 (docs) can start partially during Phase 3/4 (CLAUDE.md, README updates)

## Implementation Strategy

### PR Structure

Given the scope (infra + i18n removal + frontend fixes), this could be split into 2-3 PRs:

1. **PR 1: Infrastructure + CI/CD** (Phases 1-2) — @renatobardi provisions infra, updates workflows
2. **PR 2: i18n Removal + Frontend Fixes + Docs** (Phases 3-5) — Code changes: strip i18n, wire auth, fix frontend, update docs

Or as a single PR if @renatobardi prefers bundling (validated approach from past feedback).

### Validation Checkpoints

- **After Phase 1**: API deploys to Cloud Run and `/api/v1/health` returns 200
- **After Phase 2**: CI pipeline runs both web and API quality gates on PRs
- **After Phase 3**: `npm run build` succeeds with zero Paraglide references, all routes work as plain paths
- **After Phase 4**: Full CRUD lifecycle works in browser against production API
- **After Phase 5**: All CI gates pass, docs-check passes, quickstart verified

## Notes

- The 006 incident revealed that code without infrastructure is broken code. This plan ensures the full chain: infra → CI/CD → deploy → code → validation.
- i18n removal is mechanical but touches ~20 files. Each component gets its English text extracted from `en.json` values.
- The `LanguageSelector.svelte` component is deleted entirely (no purpose in English-only app).
- Frontend auth token (`getAuthToken()` in `incidents.ts`) is currently a stub returning empty string — this MUST be fixed for any authenticated API call to work.
- **CORS**: `apps/api/` `CORSMiddleware` reads `CORS_ORIGINS` from env. This env var MUST be set in the Cloud Run service (T007) to include the web domain (`https://loop.oute.pro`). Wildcard `*` is prohibited by Mandamento VIII. Verify during T008 that the frontend can reach the API (not just the health endpoint).
- **Integration tests**: `apps/api/tests/integration/` directory exists in the project structure but contains no tests. Integration tests (real PostgreSQL via Cloud SQL) are deferred to a future phase. Phase A coverage is achieved by mocked unit + API tests (83%). This is an acceptable trade-off for Phase A scope.
- **Backend changes made during implementation**: See Summary section above for full details. The domain model and API contract are unchanged.
