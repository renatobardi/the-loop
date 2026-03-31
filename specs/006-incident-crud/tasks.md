# Tasks: Incident Module — CRUD (Phase A)

**Input**: Design documents from `/specs/006-incident-crud/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

**Tests**: Included — Mandamento VII (CI Rigoroso) requires pytest passing in CI for merge. Tests follow the three-layer strategy from research.md: unit (domain), integration (repo adapter), API (FastAPI TestClient).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `apps/api/` (FastAPI service)
- **Frontend**: `apps/web/` (SvelteKit app)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Python backend project and configure tooling

- [x] T001 Create `apps/api/` project structure with `__init__.py` in all packages: `src/`, `src/domain/`, `src/ports/`, `src/adapters/`, `src/adapters/postgres/`, `src/adapters/firebase/`, `src/api/`, `src/api/routes/`, `tests/`, `tests/unit/`, `tests/integration/`, `tests/api/`
- [x] T002 Create `apps/api/pyproject.toml` with project metadata, Python 3.12 requirement, and dependency groups (main, dev, test)
- [x] T003 Create `apps/api/requirements.txt` with pinned dependencies: fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, pydantic, pydantic-settings, firebase-admin, alembic, slowapi, structlog, pgvector
- [x] T004 [P] Configure ruff in `apps/api/pyproject.toml` — strict rules matching Mandamento VII (Python lint gate)
- [x] T005 [P] Configure mypy strict mode in `apps/api/pyproject.toml` — matching Mandamento VII (type-check gate)
- [x] T006 [P] Configure pytest + pytest-asyncio in `apps/api/pyproject.toml` with test paths and async mode
- [x] T007 Create `apps/api/Dockerfile` — multi-stage build (deps → build → runner), Python 3.12 slim base, non-root user, port 8000

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core domain, database, auth, and app infrastructure that MUST be complete before ANY user story

**CRITICAL**: No user story work can begin until this phase is complete

### Backend Domain Layer

- [x] T008 [P] Create Category and Severity enums in `apps/api/src/domain/models.py` — 12 categories, 4 severities as string enums
- [x] T009 [P] Create domain exceptions in `apps/api/src/domain/exceptions.py` — IncidentNotFoundError, DuplicateSourceUrlError, OptimisticLockError, IncidentHasActiveRuleError
- [x] T010 Create Incident domain model (frozen Pydantic) in `apps/api/src/domain/models.py` — all 22 fields with validation (title 1-500 chars, semgrep_rule_id format, etc.) per data-model.md
- [x] T011 Create IncidentRepoPort Protocol in `apps/api/src/ports/incident_repo.py` — define async methods: create, get_by_id, update, soft_delete, list_incidents (with filters, pagination, keyword search)

### Backend Database Layer

- [x] T012 Create Pydantic BaseSettings config in `apps/api/src/config.py` — DATABASE_URL, FIREBASE_SERVICE_ACCOUNT, RATE_LIMIT (default "60/minute")
- [x] T013 Create AsyncSession factory in `apps/api/src/adapters/postgres/session.py` — async_sessionmaker with asyncpg engine
- [x] T014 Create SQLAlchemy ORM model in `apps/api/src/adapters/postgres/models.py` — incidents table with all columns, JSONB for affected_languages/tags, pgvector for embedding
- [x] T015 Initialize Alembic in `apps/api/` — create `alembic.ini` and `alembic/env.py` with async runner
- [x] T016 Create first migration `apps/api/alembic/versions/001_create_incidents_table.py` — CREATE EXTENSION IF NOT EXISTS pgvector + pg_trgm, incidents table, all indexes per data-model.md (partial unique on source_url, trigram GIN for keyword search)
- [x] T017 Implement IncidentRepoPort in `apps/api/src/adapters/postgres/repository.py` — PostgresIncidentRepository with all CRUD methods, optimistic locking (WHERE version = ?), soft-delete filter, ILIKE keyword search, real COUNT for pagination

### Backend Auth & Middleware

- [x] T018 [P] Create Firebase Auth dependency in `apps/api/src/adapters/firebase/auth.py` — verify Bearer token, extract user UID, return as created_by
- [x] T019 [P] Create middleware in `apps/api/src/api/middleware.py` — rate limiting (slowapi, 60/min per user UID), request ID (UUID per request), structured logging (structlog)

### Backend App Factory

- [x] T020 Create shared FastAPI dependencies in `apps/api/src/api/deps.py` — get_session, get_repository, get_current_user, get_incident_service
- [x] T021 Create IncidentService in `apps/api/src/domain/services.py` — orchestrates domain logic, receives IncidentRepoPort via constructor, delegates to repo after validation
- [x] T022 Create FastAPI app factory in `apps/api/src/main.py` — lifespan (init DB engine, Firebase), include routers, add middleware, CORS with explicit origin allowlist (Mandamento VIII — never wildcard `*`), health endpoint at `/api/v1/health`

### Backend Foundational Tests

- [x] T023 [P] Create test fixtures in `apps/api/tests/conftest.py` — async session factory (test DB), test client, auth override (mock Firebase returning test UID)
- [x] T024 [P] Unit tests for domain models in `apps/api/tests/unit/test_models.py` — Incident creation, enum validation, semgrep_rule_id format validation, title length boundaries
- [x] T025 [P] Unit tests for domain exceptions in `apps/api/tests/unit/test_exceptions.py` — verify all 4 exception types instantiate with correct messages

### Frontend Foundation

- [x] T026 [P] Create TypeScript types in `apps/web/src/lib/types/incident.ts` — Incident, IncidentListItem, IncidentCreate, IncidentUpdate, PaginatedResponse, Category enum, Severity enum (matching API contract)
- [x] T027 [P] Create API client service in `apps/web/src/lib/services/incidents.ts` — typed fetch wrapper for all 5 endpoints (create, list, getById, update, delete), inject Firebase Auth Bearer token from client session, handle 401 (redirect to login), 429 (show rate-limit message with Retry-After), and domain errors (409, 422)
- [x] T028 [P] Configure Vite dev proxy in `apps/web/vite.config.ts` — proxy `/api/*` to `http://localhost:8000`
- [x] T029 [P] Create incident route layout in `apps/web/src/routes/[lang=lang]/incidents/+layout.svelte` — shared layout for incident pages (nav breadcrumb, container)

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 — Create a New Incident (Priority: P1) MVP

**Goal**: Authenticated user fills a form with required fields (title, category, severity, anti_pattern, remediation) + optional fields, submits, and sees the created incident.

**Independent Test**: Submit create form with valid data → incident appears in detail view with all fields persisted.

### Implementation for User Story 1

- [x] T030 [US1] Implement create method in IncidentService in `apps/api/src/domain/services.py` — validate fields, check source_url uniqueness via repo, set embedding=NULL, delegate to repo.create
- [x] T031 [US1] Implement POST /api/v1/incidents route in `apps/api/src/api/routes/incidents.py` — request validation (Pydantic), call service.create, return 201 with full incident, handle DuplicateSourceUrlError→409, ValidationError→422
- [x] T032 [P] [US1] Unit test for create in `apps/api/tests/unit/test_services.py` — valid create, duplicate source_url rejection, invalid semgrep_rule_id rejection, missing required fields
- [x] T033 [P] [US1] API test for POST /incidents in `apps/api/tests/api/test_create_incident.py` — 201 success, 409 duplicate URL, 422 validation errors, 401 unauthenticated
- [x] T034 [P] [US1] Add i18n keys for incident create form in `apps/web/messages/en.json`, `pt.json`, `es.json` — form labels, placeholders, validation messages, submit button, success/error messages, rate-limit message
- [x] T035 [US1] Create IncidentForm component in `apps/web/src/lib/components/incidents/IncidentForm.svelte` — Svelte 5 runes, all fields (required highlighted), category/severity dropdowns, field-level validation, form state machine (idle→submitting→success|error), use design tokens
- [x] T036 [US1] Create create page in `apps/web/src/routes/[lang=lang]/incidents/new/+page.svelte` — render IncidentForm, on success redirect to detail view

**Checkpoint**: User Story 1 fully functional — create an incident via form

---

## Phase 4: User Story 2 — List and Filter Incidents (Priority: P1)

**Goal**: Authenticated user sees a paginated, filterable, searchable list of incidents sorted by creation date (newest first). Soft-deleted excluded.

**Independent Test**: Pre-seed incidents → list displays correct pagination, filters narrow results, keyword search matches expected records.

### Implementation for User Story 2

- [x] T037 [US2] Implement list method in IncidentService in `apps/api/src/domain/services.py` — delegate to repo.list_incidents with filters (category, severity), keyword search (q), pagination (page, per_page with defaults/caps)
- [x] T038 [US2] Implement GET /api/v1/incidents route in `apps/api/src/api/routes/incidents.py` — query params parsing, call service.list, return paginated response with items + total + page + per_page
- [x] T039 [P] [US2] Integration test for list in `apps/api/tests/integration/test_list_incidents.py` — pagination (default, custom per_page, beyond-range page), category filter, severity filter, combined filters, keyword search (ILIKE across 3 fields), soft-deleted exclusion, ordering by created_at DESC, real total count
- [x] T040 [P] [US2] API test for GET /incidents in `apps/api/tests/api/test_list_incidents.py` — 200 with pagination metadata, filter params, keyword search, per_page capping at 100, empty results
- [x] T041 [P] [US2] Add i18n keys for incident list page in `apps/web/messages/en.json`, `pt.json`, `es.json` — page title, filter labels, search placeholder, empty state, pagination labels, column headers
- [x] T042 [P] [US2] Create IncidentFilters component in `apps/web/src/lib/components/incidents/IncidentFilters.svelte` — category dropdown, severity dropdown, keyword search input with debounce (300ms), clear filters button
- [x] T043 [P] [US2] Create IncidentCard component in `apps/web/src/lib/components/incidents/IncidentCard.svelte` — compact card showing title, category badge, severity badge, organization, created_at, link to detail
- [x] T044 [P] [US2] Create Pagination component in `apps/web/src/lib/components/incidents/Pagination.svelte` — page navigation, per_page selector, total count display
- [x] T045 [US2] Create list page in `apps/web/src/routes/[lang=lang]/incidents/+page.svelte` and `+page.ts` — SSR load function fetching incidents, render IncidentFilters + IncidentCard list + Pagination, skeleton loading state, empty state

**Checkpoint**: User Stories 1 AND 2 functional — create incidents and see them in the list with filters

---

## Phase 5: User Story 3 — View Incident Detail (Priority: P2)

**Goal**: Authenticated user clicks an incident in the list to view all fields in a structured, readable layout. Soft-deleted incidents return 404.

**Independent Test**: Navigate to a known incident ID → all fields rendered correctly.

### Implementation for User Story 3

- [x] T046 [US3] Implement get_by_id method in IncidentService in `apps/api/src/domain/services.py` — delegate to repo.get_by_id, raise IncidentNotFoundError if not found or soft-deleted
- [x] T047 [US3] Implement GET /api/v1/incidents/{id} route in `apps/api/src/api/routes/incidents.py` — call service.get_by_id, return 200 with full incident, handle IncidentNotFoundError→404
- [x] T048 [P] [US3] API test for GET /incidents/{id} in `apps/api/tests/api/test_get_incident.py` — 200 success with all fields, 404 for non-existent ID, 404 for soft-deleted
- [x] T049 [P] [US3] Add i18n keys for incident detail page in `apps/web/messages/en.json`, `pt.json`, `es.json` — field labels, section headers, edit/delete button labels, not-found message
- [x] T050 [US3] Create IncidentDetail component in `apps/web/src/lib/components/incidents/IncidentDetail.svelte` — structured display of all fields (grouped: descriptive, classification, remediation, system metadata), code_example with monospace styling, tags as badges, severity/category color-coded badges
- [x] T051 [US3] Create detail page in `apps/web/src/routes/[lang=lang]/incidents/[id]/+page.svelte` and `+page.ts` — SSR load fetching incident by ID, render IncidentDetail, skeleton loading, 404 handling, edit/delete action buttons

**Checkpoint**: User Stories 1, 2, AND 3 functional — full create → list → view detail flow

---

## Phase 6: User Story 4 — Update an Incident (Priority: P2)

**Goal**: Authenticated user edits an incident via pre-filled form. Optimistic locking prevents conflicting concurrent updates. Version incremented atomically on success.

**Independent Test**: Load incident → modify fields → submit with correct version → changes persisted, version incremented.

### Implementation for User Story 4

- [x] T052 [US4] Implement update method in IncidentService in `apps/api/src/domain/services.py` — validate version match, check category-change block (FR-021: if semgrep_rule_id set, reject category change), check source_url uniqueness, delegate to repo.update (atomic version increment)
- [x] T053 [US4] Implement PUT /api/v1/incidents/{id} route in `apps/api/src/api/routes/incidents.py` — request validation with required version field, call service.update, return 200, handle OptimisticLockError→409, IncidentHasActiveRuleError→409, DuplicateSourceUrlError→409, IncidentNotFoundError→404
- [x] T054 [P] [US4] Unit test for update in `apps/api/tests/unit/test_services.py` — version match success, version mismatch rejection, category-change block with semgrep_rule_id, immutable fields (id, created_at, created_by) ignored
- [x] T055 [P] [US4] API test for PUT /incidents/{id} in `apps/api/tests/api/test_update_incident.py` — 200 with incremented version, 409 stale version, 409 category change blocked, 409 duplicate source_url, 404 not found, 422 validation errors
- [x] T056 [P] [US4] Add i18n keys for incident edit form in `apps/web/messages/en.json`, `pt.json`, `es.json` — edit page title, conflict error message, save button label
- [x] T057 [US4] Create edit page in `apps/web/src/routes/[lang=lang]/incidents/[id]/edit/+page.svelte` and `+page.ts` — SSR load fetching incident, render IncidentForm pre-filled with current values, include hidden version field, on conflict error show message with option to reload

**Checkpoint**: User Stories 1-4 functional — full create → list → view → edit flow with conflict protection

---

## Phase 7: User Story 5 — Soft-Delete an Incident (Priority: P3)

**Goal**: Authenticated user soft-deletes an incident from detail view after confirmation dialog. Blocked if semgrep_rule_id is set. Idempotent.

**Independent Test**: Delete incident → disappears from list and detail, DB record has deleted_at set.

### Implementation for User Story 5

- [x] T058 [US5] Implement soft_delete method in IncidentService in `apps/api/src/domain/services.py` — check semgrep_rule_id block (FR-012), check already-deleted (no-op), delegate to repo.soft_delete
- [x] T059 [US5] Implement DELETE /api/v1/incidents/{id} route in `apps/api/src/api/routes/incidents.py` — call service.soft_delete, return 200, handle IncidentHasActiveRuleError→409, IncidentNotFoundError→404
- [x] T060 [P] [US5] Unit test for soft_delete in `apps/api/tests/unit/test_services.py` — successful delete, blocked by active rule, idempotent re-delete
- [x] T061 [P] [US5] API test for DELETE /incidents/{id} in `apps/api/tests/api/test_delete_incident.py` — 200 success, 200 idempotent, 409 active rule, 404 non-existent
- [x] T062 [P] [US5] Add i18n keys for delete confirmation in `apps/web/messages/en.json`, `pt.json`, `es.json` — confirmation dialog title/body/buttons, success message, active-rule error message
- [x] T063 [US5] Create DeleteConfirmModal component in `apps/web/src/lib/components/incidents/DeleteConfirmModal.svelte` — confirmation dialog with warning text, cancel/confirm buttons, loading state during delete, error display for active-rule conflict
- [x] T064 [US5] Wire delete button on detail page `apps/web/src/routes/[lang=lang]/incidents/[id]/+page.svelte` — opens DeleteConfirmModal, on success redirect to list page

**Checkpoint**: All 5 user stories functional — complete CRUD lifecycle

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: CI integration, documentation, and production readiness

- [x] T065 [P] Update CI workflow `.github/workflows/ci.yml` — add `api-quality` job (ruff, mypy strict, pytest, Docker build, Trivy scan) parallel to existing `quality` job; add PostgreSQL service container for integration tests
- [x] T066 [P] Update deploy workflow `.github/workflows/deploy.yml` — add API service Docker build, push to Artifact Registry, deploy to Cloud Run as second service (port 8000)
- [x] T067 [P] Update `apps/web/src/lib/components/Navbar.svelte` — add "Incidents" navigation link; add nav i18n key in `apps/web/messages/en.json`, `pt.json`, `es.json`
- [x] T068 [P] Update `scripts/generate-docs.sh` — add validation for `apps/api/` README existence
- [x] T069 [P] Create `apps/api/README.md` — project overview, setup instructions, architecture diagram reference
- [x] T070 Integration test for full CRUD lifecycle in `apps/api/tests/integration/test_incident_lifecycle.py` — create → list (verify present) → get by ID → update (version bump) → soft-delete → list (verify absent) → get by ID (404)
- [x] T071 Run `apps/api/` linting, type-check, and all tests to verify CI gates pass locally
- [x] T072 Run `apps/web/` lint, check, and vitest to verify frontend CI gates pass with new incident code
- [x] T073 [P] Frontend unit tests in `apps/web/tests/unit/incidents.test.ts` — test TypeScript types validation, API client error mapping (401→redirect, 409→conflict message, 429→rate-limit), category/severity enum completeness
- [x] T074 Validate quickstart.md — follow steps end-to-end, verify all commands work, include performance spot-check (list page <2s with seeded data)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (Create) and US2 (List) can proceed in parallel
  - US3 (Detail) can proceed in parallel with US1/US2
  - US4 (Update) depends on US3 (reuses detail page load)
  - US5 (Delete) depends on US3 (reuses detail page, adds button)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1 — Create)**: Can start after Foundational — no story dependencies
- **US2 (P1 — List)**: Can start after Foundational — no story dependencies
- **US3 (P2 — Detail)**: Can start after Foundational — no story dependencies (backend independent)
- **US4 (P2 — Update)**: Backend can start after Foundational; frontend reuses IncidentForm from US1 and detail page load from US3
- **US5 (P3 — Delete)**: Backend can start after Foundational; frontend adds to detail page from US3

### Within Each User Story

- Backend service method → backend route handler (sequential)
- Backend tests can run in parallel with each other
- Frontend i18n keys can run in parallel with backend work
- Frontend components → page assembly (sequential)
- Backend should be complete before frontend integration testing

### Parallel Opportunities

- T004/T005/T006 (lint/type/test config) — all parallel
- T008/T009 (enums/exceptions) — parallel
- T018/T019 (auth/middleware) — parallel
- T023/T024/T025 (test fixtures/domain tests) — parallel
- T026/T027/T028/T029 (frontend foundation) — all parallel
- US1 and US2 backend work — parallel (different service methods and routes)
- US3 backend — parallel with US1/US2 frontend
- All i18n tasks — parallel with their story's backend work
- All test tasks within a story — parallel with each other

---

## Parallel Example: Phase 2 Foundational

```
# Backend domain (parallel):
T008: Create enums in apps/api/src/domain/models.py
T009: Create exceptions in apps/api/src/domain/exceptions.py

# After T008+T009 complete:
T010: Create Incident model (depends on enums)
T011: Create IncidentRepoPort (depends on Incident model)

# Backend infra (parallel):
T012: Config (apps/api/src/config.py)
T013: Session factory (apps/api/src/adapters/postgres/session.py)
T018: Firebase auth (apps/api/src/adapters/firebase/auth.py)
T019: Middleware (apps/api/src/api/middleware.py)

# Frontend foundation (all parallel):
T026: TypeScript types
T027: API client service
T028: Vite proxy config
T029: Incident route layout
```

---

## Parallel Example: User Story 1 + User Story 2

```
# US1 and US2 backend can start simultaneously after Phase 2:

# Developer A (US1):
T030: Service create method
T031: POST route
T032+T033: Tests (parallel)

# Developer B (US2):
T037: Service list method
T038: GET list route
T039+T040: Tests (parallel)

# Frontend for both stories can follow independently
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: US1 — Create Incident
4. Complete Phase 4: US2 — List & Filter
5. **STOP and VALIDATE**: Can create incidents and see them in a list
6. Deploy/demo if ready — this is a usable MVP

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 (Create) + US2 (List) → Usable knowledge base input + browsing (MVP!)
3. US3 (Detail) → Full incident viewing experience
4. US4 (Update) → Data quality maintenance
5. US5 (Delete) → Data hygiene
6. Polish → CI/CD integration, production deployment
7. Each increment adds value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend hexagonal flow: Route → Service → Port (Protocol) → Adapter (Repository)
- Frontend pattern: +page.ts (load) → +page.svelte (render) → component (interaction)
- All Svelte components use Svelte 5 runes ($props, $state, $derived) and design tokens from app.css
