# Tasks: Incident Module — CRUD (Phase A, Revised)

**Input**: Design documents from `/specs/007-incident-crud-v2/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

**Tests**: Not explicitly requested. Backend tests already exist from 006. Frontend tests updated only where i18n removal breaks existing tests.

**Organization**: Tasks are organized by execution phase per Mandamento XIII: infrastructure BEFORE CI/CD BEFORE code changes BEFORE documentation. Within code changes, incident component tasks are tagged with user story labels (US1-US5) for traceability. Backend code requires ZERO changes — all tasks are infra, CI/CD, frontend refactoring, and docs.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions
- **`b`-suffix IDs** (e.g., T019b): tasks inserted during revision between sequential IDs — functionally equivalent to a numbered task

## Path Conventions

- **Backend**: `apps/api/` (FastAPI service — no changes needed)
- **Frontend**: `apps/web/` (SvelteKit app — refactoring target)
- **CI/CD**: `.github/workflows/`

---

## Phase 1: Infrastructure Provisioning (Mandamento XIII)

**Purpose**: Provision all GCP resources BEFORE any code deployment. Executed by @renatobardi via `gcloud` CLI. No code changes — pure infrastructure.

**Dependency chain**: Cloud SQL → Secrets → Artifact Registry → IAM → Cloud Run

- [ ] T001 Create Cloud SQL PostgreSQL 16 instance `theloop-db` in project `theloopoute` (region `southamerica-east1`, db-f1-micro tier for Phase A, with pgvector extension enabled). Note: Artifact Registry (T004) uses `us-central1` because Artifact Registry is not available in `southamerica-east1` — cross-region latency is negligible (image pull at deploy time only).
- [ ] T002 Create database `theloop` on the Cloud SQL instance and enable `pgvector` and `pg_trgm` extensions. Note: `pg_trgm` is required to support efficient GIN-indexed ILIKE queries for keyword search (FR-016); without it, full-table scans degrade at 10k+ records.
- [ ] T003 Run Alembic migration against Cloud SQL to create the `incidents` table: `cd apps/api && alembic upgrade head`. Construct `DATABASE_URL` locally from T001/T002 output before T005 stores it in Secret Manager: `postgresql+asyncpg://<db-user>:<password>@/<database>?host=/cloudsql/theloopoute:southamerica-east1:theloop-db` — use the Cloud SQL user and password created during T001 instance setup. Set as env var: `export DATABASE_URL="<url>"` before running alembic.
- [ ] T004 [P] Create Artifact Registry repository `theloop-api` in `us-central1-docker.pkg.dev/theloopoute/` for API Docker images
- [ ] T005 [P] Create Secret Manager secrets: `THELOOP_API_DATABASE_URL` (Cloud SQL async connection string via Unix socket) and verify existing `FIREBASE_SERVICE_ACCOUNT` secret is accessible
- [ ] T006 Create IAM service account `theloop-api-sa@theloopoute.iam.gserviceaccount.com` with roles: Cloud SQL Client, Secret Manager Secret Accessor, Cloud Run Invoker
- [ ] T007 Deploy `theloop-api` Cloud Run service (initial deploy from `apps/api/Dockerfile`): bind service account `theloop-api-sa`, mount secrets, add Cloud SQL connection (`theloopoute:southamerica-east1:theloop-db`), port 8000, 512Mi memory, 1 CPU, 0-10 instances
- [ ] T008 Validate API deployment: `curl https://<theloop-api-url>/api/v1/health` returns 200

**Checkpoint**: API is live in production with database. Infrastructure chain complete.

---

## Phase 2: CI/CD Pipeline Updates

**Purpose**: Ensure both services have quality gates and automated deployment before merging code changes.

- [ ] T009 Add `api-quality` job to `.github/workflows/ci.yml` — runs in parallel with existing `quality` job, path-filtered to `apps/api/**`: ruff check, mypy strict, pytest with coverage (`pytest --cov=src --cov-fail-under=80` with PostgreSQL 16 service container + pgvector), Docker build. Phase A minimum coverage threshold: 80% (Mandamento VII).
- [ ] T010 [P] Add `api-security` job to `.github/workflows/ci.yml` — Docker build `apps/api/Dockerfile` + Trivy vulnerability scan (CRITICAL/HIGH fail) for API image, parallel with existing web `security` job (mirrors web security pattern)
- [ ] T011 Add API deploy job to `.github/workflows/deploy.yml` — Docker build `apps/api/` → push to `us-central1-docker.pkg.dev/theloopoute/theloop-api/api` → Cloud Run deploy to `theloop-api` service (runs after web deploy or in parallel)
- [ ] T012 [P] Remove Paraglide compile step (`npx paraglide-js compile`) from the existing `quality` job in `.github/workflows/ci.yml` (will be deleted in Phase 3, but CI must not depend on it)
- [ ] T013 Validate CI pipeline: open a test PR touching `apps/api/` and verify `api-quality` job runs and passes

**Checkpoint**: CI/CD runs quality gates for both web and API. Automated deploy for both services on merge to main.

---

## Phase 3: i18n Removal — Infrastructure & Config

**Purpose**: Remove all Paraglide/i18n infrastructure files and build configuration. This MUST be done before component refactoring.

- [ ] T014 Reference English values for component hardcoding: run `git show main:apps/web/messages/en.json` to retrieve the file from git history (it was deleted on this branch). Keep these values open during T025–T054 as the source of truth for all hardcoded English strings. No file to commit — this is a local reference step.
- [ ] T015 Delete i18n message files: `apps/web/messages/en.json`, `apps/web/messages/pt.json`, `apps/web/messages/es.json`, and the `apps/web/messages/` directory
- [ ] T016 [P] Delete Paraglide config directory: `apps/web/project.inlang/` (settings.json and related files)
- [ ] T017 [P] Delete `apps/web/src/lib/i18n.ts` (Paraglide setup: prefixDefaultLanguage, locales, pathnames)
- [ ] T018 [P] Delete `apps/web/src/lib/components/LanguageSelector.svelte` (no purpose in English-only app)
- [ ] T019 [P] Delete `apps/web/src/params/lang.ts` if it exists (locale parameter matcher)
- [ ] T019b [P] Delete `apps/web/src/lib/paraglide/` directory if present (auto-generated Paraglide output: messages.js, runtime.js). Verify if committed or gitignored — if committed, delete and commit removal.
- [ ] T020 Remove `@inlang/paraglide-sveltekit` from `apps/web/package.json` dependencies and run `npm install` to update lockfile
- [ ] T021 Remove Paraglide Vite plugin from `apps/web/vite.config.ts` — remove the paraglide plugin import and its entry in the plugins array
- [ ] T022 Update `apps/web/src/hooks.ts` — remove the Paraglide `reroute` export (or delete file if that's the only export)
- [ ] T023 Update `apps/web/src/routes/+layout.svelte` — remove `<ParaglideJS {i18n}>` wrapper, remove imports from `$lib/paraglide/runtime.js` and `$lib/i18n`, keep the layout markup
- [ ] T024 Remove any `hreflang` link tags from `apps/web/src/app.html` or layout files that reference locale variants

**Checkpoint**: Paraglide is fully removed from build config. `npm run build` will fail until components are refactored (Phase 4/5) because they still import from `$lib/paraglide/messages.js`.

---

## Phase 4: i18n Removal — Landing Page Components

**Purpose**: Refactor all landing page components to hardcode English text. Each component: remove `$lib/paraglide/messages.js` imports, replace `message_key()` calls with English string values from en.json.

- [ ] T025 [P] Refactor `apps/web/src/lib/components/Hero.svelte` — replace all paraglide message calls with English strings, remove paraglide imports
- [ ] T026 [P] Refactor `apps/web/src/lib/components/Problem.svelte` — replace all paraglide message calls with English strings, remove paraglide imports
- [ ] T027 [P] Refactor `apps/web/src/lib/components/Layers.svelte` — replace all paraglide message calls with English strings, remove paraglide imports
- [ ] T028 [P] Refactor `apps/web/src/lib/components/HowItWorks.svelte` — replace all paraglide message calls with English strings, remove paraglide imports
- [ ] T029 [P] Refactor `apps/web/src/lib/components/Pricing.svelte` — replace all paraglide message calls with English strings, remove paraglide imports
- [ ] T030 [P] Refactor `apps/web/src/lib/components/Footer.svelte` — replace all paraglide message calls with English strings, remove paraglide imports
- [ ] T031 [P] Refactor `apps/web/src/lib/components/WaitlistForm.svelte` — replace all paraglide message calls with English strings, remove paraglide imports
- [ ] T032 [P] Refactor `apps/web/src/lib/components/WaitlistCta.svelte` — replace all paraglide message calls with English strings, remove paraglide imports
- [ ] T033 [P] Refactor `apps/web/src/lib/components/Integrations.svelte` — replace all paraglide message calls with English strings (if any), remove paraglide imports
- [ ] T034 [P] Refactor `apps/web/src/lib/components/TransparencySection.svelte` — replace all paraglide message calls with English strings, remove paraglide imports
- [ ] T035 [P] Refactor `apps/web/src/lib/components/ConstitutionHero.svelte` — replace all paraglide message calls with English strings, remove paraglide imports
- [ ] T036 [P] Refactor `apps/web/src/lib/components/MandateCard.svelte` — replace all paraglide message calls with English strings, remove paraglide imports
- [ ] T037 [P] Refactor `apps/web/src/lib/components/MandatesGrid.svelte` — replace all paraglide message calls with English strings, remove paraglide imports
- [ ] T038 [P] Refactor `apps/web/src/lib/ui/Navbar.svelte` (or wherever Navbar is) — remove LanguageSelector usage, remove paraglide imports, hardcode English nav text. Verify "Incidents" navigation link exists (href="/incidents/") — add it if missing.
- [ ] T039 [P] Refactor any remaining components that import from `$lib/paraglide/` — run `grep -r "paraglide" apps/web/src/` to find stragglers, refactor each
- [ ] T040 Remove all `i18n.resolveRoute()` calls from landing page and constitution route files — replace with plain `href` paths (e.g., `href="/"`, `href="/constitution/"`)
- [ ] T041 Update `apps/web/src/routes/+page.server.ts` — if waitlist form actions reference i18n, strip those references
- [ ] T042 Verify `npm run build` succeeds with zero Paraglide references and landing page renders correctly at `http://localhost:5173/`

**Checkpoint**: Landing page is fully English-only, all routes work as plain paths, build passes.

---

## Phase 5: i18n Removal — Incident Components (US1-US5)

**Purpose**: Refactor all incident-related components to hardcode English text. Remove `resolveRoute` and paraglide imports. Each component maps to its user story.

### User Story 1 — Create Incident

- [ ] T043 [P] [US1] Refactor `apps/web/src/lib/components/incidents/IncidentForm.svelte` — replace all paraglide message calls with English strings (form labels, placeholders, validation messages, submit button text), remove paraglide imports
- [ ] T044 [P] [US1] Refactor `apps/web/src/routes/incidents/new/+page.svelte` — remove paraglide imports, hardcode page title, remove resolveRoute calls

### User Story 2 — List & Filter Incidents

- [ ] T045 [P] [US2] Refactor `apps/web/src/lib/components/incidents/IncidentFilters.svelte` — replace paraglide message calls with English strings (filter labels, search placeholder, clear button), remove imports
- [ ] T046 [P] [US2] Refactor `apps/web/src/lib/components/incidents/IncidentCard.svelte` — replace paraglide message calls with English strings, remove imports
- [ ] T047 [P] [US2] Refactor `apps/web/src/lib/components/incidents/Pagination.svelte` — replace paraglide message calls with English strings, remove imports
- [ ] T048 [P] [US2] Refactor `apps/web/src/routes/incidents/+page.svelte` — remove paraglide imports, hardcode page title and empty state text, replace resolveRoute with plain `href="/incidents/new/"`

### User Story 3 — View Incident Detail

- [ ] T049 [P] [US3] Refactor `apps/web/src/lib/components/incidents/IncidentDetail.svelte` — replace paraglide message calls with English strings (field labels, section headers), remove imports
- [ ] T050 [P] [US3] Refactor `apps/web/src/routes/incidents/[id]/+page.svelte` — remove paraglide imports, hardcode text, replace resolveRoute with plain href paths

### User Story 4 — Update Incident

- [ ] T051 [P] [US4] Refactor `apps/web/src/routes/incidents/[id]/edit/+page.svelte` — remove paraglide imports, hardcode page title ("Edit Incident"), replace resolveRoute calls

### User Story 5 — Soft-Delete Incident

- [ ] T052 [P] [US5] Refactor `apps/web/src/lib/components/incidents/DeleteConfirmModal.svelte` — replace paraglide message calls with English strings (dialog title, body, buttons, error messages), remove imports

### Incident Layout & Shared

- [ ] T053 [P] Refactor `apps/web/src/routes/incidents/+layout.svelte` — remove paraglide imports if any, hardcode breadcrumb text
- [ ] T054 Remove all `i18n.resolveRoute()` calls from incident route files — replace with plain `href` paths throughout
- [ ] T055 Verify `npm run build` succeeds and all incident routes work: `/incidents/`, `/incidents/new/`, `/incidents/<id>/`, `/incidents/<id>/edit/`

**Checkpoint**: All incident components are English-only. Frontend builds cleanly. All routes work as plain paths.

---

## Phase 6: Frontend Fixes & Auth Wiring (US1-US5)

**Purpose**: Fix the broken frontend — wire Firebase Auth for API calls and add error handling for graceful degradation (FR-024, SC-009).

### Auth Wiring

- [ ] T056 Add Firebase client SDK to `apps/web/package.json` (`firebase` package) if not already present, run `npm install`
- [ ] T057 Create Firebase client initialization in `apps/web/src/lib/firebase.ts` — initialize Firebase app with public config (apiKey, authDomain, projectId from `theloopoute`), export `auth` instance
- [ ] T058 Implement `getAuthToken()` in `apps/web/src/lib/services/incidents.ts` — replace empty string stub with `auth.currentUser?.getIdToken()`. If `auth.currentUser` is null, redirect to the landing page (`/`) with query param `?auth=required` (no `/login` route exists). Never redirect to `/login`.
- [ ] T059 Add API base URL configuration — use environment variable or Vite define for production API URL (Cloud Run URL from T007 output), keep `/api` proxy for development. Depends on T007.

### Error Handling (FR-024)

- [ ] T060 [P] [US2] Add error boundary to `apps/web/src/routes/incidents/+page.svelte` — catch API fetch failures, show "Unable to connect to the server" message instead of blank page
- [ ] T061 [P] [US3] Add error handling to `apps/web/src/routes/incidents/[id]/+page.svelte` — handle 404 (show "Incident not found"), handle connection errors (show error state)
- [ ] T062 [P] [US1] Add error handling to `apps/web/src/routes/incidents/new/+page.svelte` — handle API errors during create (show error message, preserve form data)
- [ ] T063 [P] [US4] Add error handling to `apps/web/src/routes/incidents/[id]/edit/+page.svelte` — handle conflict errors (409): optimistic lock conflict ("Incident was modified by another process — reload and try again") and FR-021 category-change conflict ("Cannot change category while a Semgrep rule is linked — clear semgrep_rule_id first"). Also handle connection errors.
- [ ] T064 [P] [US5] Add error handling to `apps/web/src/lib/components/incidents/DeleteConfirmModal.svelte` — handle 409 (active rule), connection errors

### SSR Evaluation

- [ ] T065 Review `apps/web/src/routes/incidents/+layout.ts` — if `ssr = false`, keep CSR (incident pages require authenticated API calls, no server-side rendering benefit). Add a code comment explaining the CSR-only decision: `// CSR-only: incident routes require client-side Firebase Auth token for API calls`.

### End-to-End Validation

- [ ] T066 Test full CRUD lifecycle against running API: create incident → see it in list → view detail → edit (verify version bump) → soft-delete → verify excluded from list
- [ ] T066b Seed 10,000 test incidents into the database for performance validation (required by T067). Run `cd apps/api && python scripts/seed.py --count 10000` — create `apps/api/scripts/seed.py` using SQLAlchemy bulk insert with randomized field values covering all categories and severities. Depends on T007 (Cloud Run + DB live).
- [ ] T067 Test error scenarios: API unreachable → error message shown (not blank page); rate limit exceeded (429) → verify `incidents.ts` shows retry-after message (FR-022); auth expired → redirect to `/`. Performance validation against 10k seed (T066b): list page loads in <2s (SC-002), keyword search returns in <2s (SC-004), category/severity filter returns in <1s (SC-003).

**Checkpoint**: Full CRUD lifecycle works in browser against production API. Graceful degradation verified.

---

## Phase 7: Documentation & Polish

**Purpose**: Update all documentation to reflect i18n removal and new architecture. Run all CI gates.

- [ ] T068 [P] Update `CLAUDE.md` — remove i18n sections (Paraglide-SvelteKit, message imports, locale routing), update routing docs (plain paths), update commands (remove Paraglide compile), remove i18n references from Architecture section
- [ ] T069 [P] Update root `README.md` — remove i18n/multi-language references, update tech stack description, update route examples to plain paths
- [ ] T070 [P] Verify `apps/api/README.md` is accurate (should need no changes since backend is untouched)
- [ ] T071 [P] Update `scripts/generate-docs.sh` — remove any i18n-related validation checks, ensure it validates `apps/api/` README existence
- [ ] T072 Run `bash scripts/generate-docs.sh` and commit any generated changes to pass the docs-check CI gate
- [ ] T073 Run `apps/api/` quality gates locally: `cd apps/api && ruff check src/ tests/ && mypy src/ && pytest` — verify all pass
- [ ] T074 Run `apps/web/` quality gates locally: `cd apps/web && npm run lint && npm run check && npm run test -- --run && npm run build` — verify all pass
- [ ] T075 [P] Update existing frontend tests in `apps/web/tests/unit/` — fix any tests that import from paraglide or reference i18n
- [ ] T076 Validate quickstart.md — follow all steps end-to-end, verify URLs work (no locale prefix)
- [ ] T077 Copy `specs/007-incident-crud-v2/` to `.project/phases/01-incidents/` as required by Mandamento XI (project history archive). Run on merge or immediately before opening the final PR.

**Checkpoint**: All CI gates pass locally. Documentation is up to date. Phase docs archived. Ready for PR.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Infrastructure)**: No dependencies — start here. Executed by @renatobardi via gcloud CLI.
- **Phase 2 (CI/CD)**: T011 (deploy job) depends on Phase 1 (Artifact Registry + Cloud Run service must exist). T009, T010, T012 can start in parallel with Phase 1 — they use GitHub Actions Docker service containers, not the production Cloud SQL instance.
- **Phase 3 (i18n Infra)**: Can start in parallel with Phase 1 — pure file deletions and config changes, no infra dependency.
- **Phase 4 (i18n Landing)**: Depends on Phase 3 (Paraglide removed from config before components can be refactored).
- **Phase 5 (i18n Incidents)**: Depends on Phase 3. Can run in parallel with Phase 4 (different files).
- **Phase 6 (Frontend Fixes)**: Depends on Phase 1 (API must be deployed), Phase 4 & 5 (i18n removed).
- **Phase 7 (Docs)**: Depends on Phases 3-6 being complete. Some tasks (T068, T069) can start during Phase 4/5.

### Parallel Opportunities

- **Phase 1 + Phase 3**: Infrastructure provisioning and i18n file deletion can happen simultaneously
- **Phase 4 + Phase 5**: Landing page refactoring and incident component refactoring are fully independent (different files)
- **All [P] tasks within any phase**: Different files, no dependencies between them
- **T025-T039** (Phase 4): All 15 component refactoring tasks are independent and parallelizable
- **T043-T054** (Phase 5): All 12 incident component tasks are independent and parallelizable
- **T060-T064** (Phase 6): Error handling tasks for each route are independent
- **T066b** depends on T007 (DB + Cloud Run live); **T067** depends on T066b (seeding must complete before performance validation)

### Critical Path

```
T001 (Cloud SQL) → T002 (DB) → T003 (Migration) → T005 (Secrets) → T006 (IAM) → T007 (Cloud Run) → T008 (Validate)
         │                                                                                ↓
         │                                                               T011 (Deploy workflow) → T013 (Validate CI)
         │
         ├─ T009 (CI api-quality) [parallel — uses Docker service container, not Cloud SQL]
         ├─ T010 (CI api-security) [parallel]
         └─ T012 (remove Paraglide step) [parallel]

Phase 3 (i18n infra) → Phase 4+5 (components) → Phase 6 (auth + errors) → Phase 7 (docs)
                                                         ↑
                                               (also depends on T007)
```

---

## Implementation Strategy

### MVP Scope

Phases 1-5 deliver the minimum: infrastructure provisioned, CI/CD working, i18n removed, incident pages functional (without auth, against API). Phase 6 adds auth + error handling. Phase 7 finalizes docs.

### PR Structure (Suggested)

1. **PR 1: Infrastructure + CI/CD** (T001-T013) — @renatobardi provisions infra, updates workflows
2. **PR 2: i18n Removal + Frontend Fixes + Docs** (T014-T077) — Strip i18n, wire auth, fix errors, update docs

### Incremental Delivery

1. Phase 1 → API live in production, health check passes
2. Phase 2 → CI gates both services, deploy automated
3. Phase 3+4+5 → App is English-only, all routes work, build passes
4. Phase 6 → Full CRUD lifecycle works with auth, errors handled gracefully
5. Phase 7 → Docs updated, all CI gates pass, ready for merge

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability (US1-US5)
- Backend code (`apps/api/`) requires ZERO changes — all tasks are infra, CI/CD, and frontend
- Phase 1 tasks (T001-T008) are executed via `gcloud` CLI by @renatobardi, not code commits
- The en.json values retrieved in T014 (via `git show main:apps/web/messages/en.json`) are the source of truth for hardcoded English strings in T025-T054
- T066b (seeding script `apps/api/scripts/seed.py`) is a new code artifact; backend "ZERO changes" refers to production application code only — scripts are allowed
- After i18n removal, the `apps/web/src/lib/paraglide/` directory (auto-generated, should be gitignored) can be cleaned up
- `getAuthToken()` stub returning empty string is the root cause of the blank page — T058 is the critical fix
- Mandamento XIII compliance: T001-T008 (infra) execute BEFORE T056-T067 (code that depends on running API)
