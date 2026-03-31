# Research: Incident Module — CRUD (Phase A, Revised)

**Branch**: `007-incident-crud-v2` | **Date**: 2026-03-31

This research builds on `006-incident-crud/research.md`. Decisions unchanged from 006 (monorepo structure, FastAPI+SQLAlchemy, hexagonal layout, Firebase Auth, Alembic, frontend-backend integration, CI/CD multi-service, rate limiting, testing, observability) are carried forward without repetition. This document covers **new decisions** specific to the revision.

## 1. i18n Removal Strategy

**Decision**: Full removal of Paraglide i18n infrastructure from the entire project. All text hardcoded in English.

**Rationale**: The user wants to simplify the application. Paraglide is deeply integrated (24 files import from `$lib/paraglide/`, 3 message files with ~100 keys each, `ParaglideJS` wrapper in root layout, `i18n.resolveRoute()` in components, `reroute` in hooks). Removing it simplifies routing, eliminates build-time codegen, reduces bundle size, and removes the `[lang=lang]` routing indirection.

**Scope of changes**:
- Delete `apps/web/messages/` (en.json, pt.json, es.json)
- Delete `apps/web/src/lib/paraglide/` (auto-generated)
- Delete `apps/web/src/lib/i18n.ts`
- Delete `apps/web/project.inlang/` (Paraglide config)
- Remove `@inlang/paraglide-sveltekit` from package.json
- Remove Paraglide Vite plugin from `vite.config.ts`
- Update `apps/web/src/hooks.ts` — remove reroute export
- Update `apps/web/src/routes/+layout.svelte` — remove `<ParaglideJS>` wrapper
- Refactor ~13 landing page components — replace message function calls with hardcoded English strings
- Refactor ~6 incident components — replace message function calls with hardcoded English strings
- Delete `LanguageSelector.svelte` component entirely
- Remove Paraglide compile step from CI workflow
- Update `scripts/generate-docs.sh` if it references i18n files

**Approach**: Extract English values from `en.json`, then find-and-replace each `message_key()` call with its English string value in each component.

**Alternatives considered**:
- Keep Paraglide with only English locale: Rejected — adds unnecessary build complexity and codegen for zero benefit.
- Gradual removal (incidents first, landing later): Rejected — creates inconsistency, and the work is mechanical.

## 2. Existing 006 Code Disposition

**Decision**: Refactor in-place. Backend is kept as-is. Frontend incident routes (already at `/incidents/`, not `[lang=lang]/incidents/`) are stripped of i18n imports. Landing page routes stay at `/` but lose locale prefix.

**Current state** (discovered via codebase exploration):
- `apps/api/` — Fully implemented FastAPI backend with hexagonal architecture. All domain models, ports, adapters, routes, tests, Dockerfile, and Alembic migrations in place. **No changes needed** to backend code.
- `apps/web/src/routes/incidents/` — CRUD pages exist (list, detail, edit, new). Already NOT under `[lang=lang]` path. Use `i18n.resolveRoute()` for navigation — needs removal.
- `apps/web/src/lib/components/incidents/` — 6 components (IncidentForm, IncidentDetail, IncidentCard, IncidentFilters, Pagination, DeleteConfirmModal). Import Paraglide messages — needs refactoring.
- `apps/web/src/lib/services/incidents.ts` — API client. Auth token returns empty string — needs Firebase Auth wiring.
- `apps/web/src/routes/incidents/+layout.ts` — Has `ssr = false`. This should be evaluated (may need SSR for SEO/graceful degradation).

**Rationale**: The backend code was written to spec and passed review. Rewriting it would waste effort. The frontend refactoring is mechanical (swap i18n calls for English strings, remove `resolveRoute` wrappers).

## 3. Infrastructure Provisioning (Mandamento XIII)

**Decision**: All infrastructure must be provisioned BEFORE code deployment. The execution plan includes explicit `gcloud` commands for each resource.

**Required resources** (none currently exist for the API service):

| Resource | Service | Purpose |
|----------|---------|---------|
| Cloud SQL instance | `theloop-db` | PostgreSQL 16 with pgvector |
| Cloud SQL database | `theloop` | Application database |
| Cloud Run service | `theloop-api` | FastAPI backend |
| Artifact Registry repo | `theloop-api` | API Docker images |
| Secret Manager secrets | `DATABASE_URL`, `FIREBASE_SERVICE_ACCOUNT` | API runtime secrets |
| IAM service account | `theloop-api-sa` | Cloud Run → Cloud SQL, Secret Manager access |
| VPC connector or Cloud SQL Auth Proxy | — | Cloud Run ↔ Cloud SQL connectivity |

**Execution order** (strict dependency chain):
1. Cloud SQL instance + database + pgvector extension
2. Secret Manager entries (DATABASE_URL with Cloud SQL connection string)
3. Artifact Registry repository for API images
4. IAM service account with Cloud SQL Client + Secret Manager Accessor roles
5. Cloud Run service deployment with service account binding
6. CI workflow updates (api-quality job with PostgreSQL service container)
7. Deploy workflow updates (API build + push + deploy)
8. DNS/networking (if needed — Cloud Run internal URL sufficient for Phase A)

**Alternatives considered**:
- Terraform: Rejected — adds complexity for a small number of resources. `gcloud` CLI is simpler for initial provisioning by @renatobardi.
- Cloud SQL Auth Proxy sidecar: Preferred over VPC connector for Cloud Run ↔ Cloud SQL. Cloud Run supports Cloud SQL connections natively via `/cloudsql/` socket.

## 4. CI/CD for API Service

**Decision**: Add `api-quality` job to CI and API deploy step to deploy workflow.

**Current state**:
- `ci.yml` has: `quality` (web lint/type-check/test/build), `security` (Docker/Trivy), `docs` (generate-docs check). No Python CI.
- `deploy.yml` has: web Docker build → Artifact Registry push → Cloud Run deploy. No API deploy.

**Changes needed**:
- **ci.yml**: Add `api-quality` job (ruff, mypy strict, pytest with PostgreSQL service container, Docker build, Trivy scan). Runs in parallel with existing `quality` job. Path-filtered to `apps/api/**`.
- **deploy.yml**: Add API Docker build → push to `us-central1-docker.pkg.dev/theloopoute/theloop-api/api` → Cloud Run deploy to `theloop-api` service.
- **ci.yml**: Remove Paraglide compile step from existing `quality` job (since i18n is removed).

## 5. Routing Simplification

**Decision**: Remove `[lang=lang]` parameter matcher from all routes. Routes become plain paths.

**Current route structure**:
```
src/routes/
├── +layout.svelte       # ParaglideJS wrapper → remove wrapper
├── +layout.ts            # trailingSlash: 'always' → keep
├── +page.server.ts       # Waitlist form actions → keep
├── +page.svelte          # Landing page → keep, strip i18n
├── constitution/         # Already NOT under [lang=lang]
├── incidents/            # Already NOT under [lang=lang]
```

**Finding**: The incident and constitution routes are already at top-level (not under `[lang=lang]`). The landing page root route also appears to be at `/`, with Paraglide handling the locale prefix transparently. After removing Paraglide, routes will simply work as plain paths.

**Key change**: Remove `src/hooks.ts` reroute export (Paraglide's locale-aware routing). Ensure `href` attributes in components use plain paths (no `resolveRoute` wrappers).

## 6. Frontend Auth Token

**Decision**: Defer Firebase Auth client-side token acquisition to this spec's scope. The existing `incidents.ts` service returns an empty Bearer token.

**Current state**: `apps/web/src/lib/services/incidents.ts` has `getAuthToken()` returning empty string. This means no authenticated requests can succeed.

**Resolution**: This needs to be addressed in the frontend refactoring tasks. Firebase client-side SDK initialization + token retrieval must be wired into the API client service.
