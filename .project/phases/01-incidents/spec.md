# Feature Specification: Incident Module — CRUD (Phase A, Revised)

**Feature Branch**: `007-incident-crud-v2`
**Created**: 2026-03-31
**Status**: Draft
**Input**: User description: "Revised incident CRUD spec: add backend/infra dependencies per Mandamento XIII, remove i18n (English-only), simplify frontend routing"
**Supersedes**: `006-incident-crud` — this revision adds missing infrastructure dependencies and removes i18n complexity.

## Clarifications

### Session 2026-03-31 (carried from 006)

- Q: Can any authenticated user edit/delete any incident, or only the creator? → A: Any authenticated user can create, read, update, and soft-delete any incident (no role checks in Phase A).
- Q: What happens when category is changed on an incident with an active semgrep_rule_id? → A: Block category change if semgrep_rule_id is set (return conflict error, same pattern as soft-delete block).
- Q: Should incident API endpoints have rate limiting? → A: Yes, basic rate limiting at 60 req/min per authenticated user.

### Session 2026-03-31 (this revision)

- Q: Should the application support multiple languages? → A: No. English-only. Remove all i18n/Paraglide references. Simplify routing by removing the `[lang=lang]` prefix.
- Q: Were infrastructure dependencies missing from the original spec? → A: Yes. All infrastructure (Cloud SQL, Cloud Run for API, Artifact Registry, Secret Manager, IAM, CI/CD) MUST be part of the execution plan per Mandamento XIII.
- Q: Does i18n removal apply to the entire app or just the incident module? → A: Entire app. Delete Paraglide, all message files (en.json, pt.json, es.json), and [lang=lang] routing. All routes become plain paths (/, /incidents/). Landing page included.
- Q: Should existing 006 code (already merged) be refactored or rewritten? → A: Refactor in-place. Move frontend routes to plain paths, strip i18n from components, keep backend as-is. Add infra provisioning tasks.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a New Incident (Priority: P1)

An authenticated user navigates to the incident creation form, fills in the required fields (title, category, severity, anti-pattern, remediation) and optional fields, then submits. The system validates the input, persists the incident, and returns the complete record. The user sees confirmation and is redirected to the incident detail view.

**Why this priority**: Creating incidents is the foundational operation — without it, no other CRUD operation has data to work with. This is the core input mechanism for building the incident knowledge base.

**Independent Test**: Can be fully tested by submitting the create form with valid data and verifying the incident appears in the detail view with all fields correctly persisted.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the create form, **When** they fill all required fields (title, category, severity, anti_pattern, remediation) and submit, **Then** the incident is created with a unique ID, version=1, created_at/updated_at timestamps, and the user is shown the incident detail.
2. **Given** an authenticated user on the create form, **When** they submit with a source_url that already exists in the system, **Then** the system rejects the submission with a clear error message indicating the URL is already registered.
3. **Given** an authenticated user on the create form, **When** they provide a semgrep_rule_id that does not match the `{category}-{NNN}` format, **Then** the system rejects the submission with a validation error.
4. **Given** an authenticated user on the create form, **When** they submit without filling a required field (e.g., missing title), **Then** the system shows field-level validation errors without losing the other filled data.

---

### User Story 2 - List and Filter Incidents (Priority: P1)

An authenticated user navigates to the incident list page. They see a paginated table of incidents sorted by creation date (newest first). They can filter by category and severity, and search by keyword across title, anti-pattern, and remediation fields. Soft-deleted incidents are excluded.

**Why this priority**: Equal to Create — the list is how users discover and navigate the knowledge base. Without a usable list, created incidents are inaccessible.

**Independent Test**: Can be tested by pre-seeding incidents and verifying the list displays them with correct pagination, filters narrow results, and keyword search matches expected records.

**Acceptance Scenarios**:

1. **Given** 50 incidents exist, **When** the user loads the list page with default settings, **Then** the first 20 incidents are shown sorted by created_at DESC, with total count of 50 and pagination controls.
2. **Given** incidents with mixed categories, **When** the user filters by category "injection", **Then** only incidents with category "injection" are shown, with an accurate total count.
3. **Given** incidents with mixed severities, **When** the user filters by severity "critical", **Then** only critical incidents are shown.
4. **Given** the user types "ReDoS" in the search box, **When** the search executes (with debounce), **Then** incidents matching "ReDoS" in title, anti_pattern, or remediation are shown.
5. **Given** a soft-deleted incident exists, **When** the user loads the list, **Then** the soft-deleted incident does not appear.
6. **Given** the user requests page 3 with per_page=10, **When** the results load, **Then** incidents 21-30 are displayed with correct pagination metadata.

---

### User Story 3 - View Incident Detail (Priority: P2)

An authenticated user clicks on an incident in the list to view its full detail. All fields are displayed in a structured, readable layout.

**Why this priority**: Essential for consuming the knowledge base, but depends on Create and List existing first.

**Independent Test**: Can be tested by navigating to a known incident ID and verifying all fields are rendered correctly.

**Acceptance Scenarios**:

1. **Given** an incident with a known ID exists, **When** the user navigates to its detail page, **Then** all fields (title, date, source_url, organization, category, subcategory, failure_mode, severity, affected_languages, anti_pattern, code_example, remediation, static_rule_possible, semgrep_rule_id, tags, version, created_at, updated_at) are displayed.
2. **Given** an incident that has been soft-deleted, **When** the user tries to access its detail page, **Then** they receive a "not found" response.

---

### User Story 4 - Update an Incident (Priority: P2)

An authenticated user opens an incident's edit form (pre-filled with current values), modifies fields, and submits. The system uses optimistic locking to prevent conflicting updates — the request must include the current version number. On success, the version is incremented atomically.

**Why this priority**: Updates are essential for maintaining data quality, but less frequent than creates and reads.

**Independent Test**: Can be tested by loading an incident, modifying fields, submitting with the correct version, and verifying the changes are persisted with version incremented.

**Acceptance Scenarios**:

1. **Given** an incident at version 3, **When** the user submits an update with version=3, **Then** the incident is updated and version becomes 4.
2. **Given** an incident at version 3, **When** the user submits an update with version=2 (stale), **Then** the system returns a conflict error with a message explaining the incident was modified by another process.
3. **Given** an incident being edited, **When** the user changes the title and submits, **Then** the updated_at timestamp is refreshed and the new title is persisted.
4. **Given** an incident being edited, **When** the user changes source_url to one that already exists on another incident, **Then** the system rejects with a duplicate source_url error.

---

### User Story 5 - Soft-Delete an Incident (Priority: P3)

An authenticated user requests deletion of an incident from the detail view. A confirmation dialog appears. On confirmation, the system marks the incident as soft-deleted (sets deleted_at timestamp). The incident disappears from the list but remains in the database.

**Why this priority**: Deletion is the least-used CRUD operation but necessary for data hygiene. Soft-delete protects against accidental data loss.

**Independent Test**: Can be tested by deleting an incident and verifying it disappears from the list and detail view, but still exists in the database with a deleted_at timestamp.

**Acceptance Scenarios**:

1. **Given** an incident without a semgrep_rule_id, **When** the user confirms deletion, **Then** the incident's deleted_at is set to the current timestamp and it no longer appears in list or detail views.
2. **Given** an incident with a semgrep_rule_id set, **When** the user requests deletion, **Then** the system returns a conflict error with a message explaining the incident cannot be deleted because it has an active Semgrep rule linked.
3. **Given** an already soft-deleted incident, **When** a deletion request is made for the same ID, **Then** the operation is a no-op (idempotent) and returns success.

---

### Edge Cases

- What happens when a user tries to create an incident with a title of exactly 500 characters? Should succeed (boundary value).
- What happens when a user provides a title of 501 characters? Should fail with validation error.
- What happens when the keyword search term matches across multiple fields of the same incident? Should appear once in results.
- What happens when the user requests a page beyond the total result set? Should return empty list with correct total count.
- What happens when per_page exceeds 100? Should be capped at 100.
- What happens when per_page is 0 or negative? Should fall back to default 20.
- What happens when multiple users try to update the same incident simultaneously? Optimistic locking ensures only the first write succeeds; subsequent writes receive a conflict error.
- What happens when source_url is provided as an empty string vs. null? Empty string should be treated as null/absent.
- What happens when a user updates the category of an incident that has a semgrep_rule_id? System blocks the change with a conflict error (user must clear the rule first).
- What happens when the user's auth session expires mid-operation? Should receive an authentication error without data loss on the client side.
- What happens when an authenticated user exceeds 60 requests per minute? Should receive a rate-limited response with a retry-after indication.
- What happens when the backend API is unreachable from the frontend? The frontend should display a clear connection error, not a blank page or unhandled crash (graceful degradation per Mandamento XIII).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authenticated users to create incidents with required fields: title (1-500 chars), category (one of 12 fixed values), severity (one of 4 fixed values), anti_pattern (min 1 char), and remediation (min 1 char).
- **FR-002**: System MUST auto-generate id (UUID), version (starting at 1), created_at, and updated_at on incident creation.
- **FR-003**: System MUST extract created_by from the authenticated user's session, never accepting it as user input.
- **FR-004**: System MUST enforce uniqueness on source_url across all non-deleted incidents when provided.
- **FR-005**: System MUST validate semgrep_rule_id against the format `{category}-{NNN}` (where category matches the incident's own category and NNN is a zero-padded 3-digit number) when provided.
- **FR-006**: System MUST set embedding to NULL on all incidents in Phase A.
- **FR-007**: System MUST return the complete incident record (all fields) on create, read, and update operations.
- **FR-008**: System MUST support reading a single incident by ID, excluding soft-deleted incidents by default.
- **FR-009**: System MUST support updating incidents with optimistic locking: the request includes the expected version, and the system rejects updates where the version does not match with a conflict response.
- **FR-010**: System MUST atomically increment the version field on successful updates.
- **FR-011**: System MUST support soft-delete by setting deleted_at to the current timestamp.
- **FR-012**: System MUST block soft-delete of incidents that have a non-null semgrep_rule_id, returning a conflict response with an explanatory message.
- **FR-013**: Soft-delete MUST be idempotent — deleting an already-deleted incident is a no-op returning success.
- **FR-014**: System MUST support listing incidents with pagination (page + per_page, default 20, max 100), ordered by created_at DESC, excluding soft-deleted records.
- **FR-015**: System MUST support filtering the list by category and severity (independently or combined).
- **FR-016**: System MUST support keyword search (case-insensitive partial match) across title, anti_pattern, and remediation fields (OR match — an incident appears if any one of the three fields contains the keyword).
- **FR-017**: System MUST return the real total count (not approximate) for paginated list results.
- **FR-018**: System MUST follow hexagonal architecture: pure domain layer (no external dependencies) with ports (interfaces) and adapters (implementations).
- **FR-019**: System MUST operate as single-tenant in Phase A (no tenant isolation).
- **FR-020**: All authenticated users MUST have equal permissions — any user can create, read, update, or soft-delete any incident. No role-based access control in Phase A.
- **FR-021**: System MUST block category changes on incidents that have a non-null semgrep_rule_id, returning a conflict response with an explanatory message (consistent with FR-012 soft-delete protection).
- **FR-022**: System MUST enforce rate limiting on incident API endpoints at 60 requests per minute per authenticated user, returning a rate-limited response when exceeded.
- **FR-023**: The application MUST be English-only across all pages (landing page and incident module). All i18n infrastructure (Paraglide, message files, locale-prefixed routing) MUST be removed. All UI text is hardcoded in English. Routes use plain paths (e.g., `/`, `/incidents/`).
- **FR-024**: The frontend MUST display a clear error state (not a blank page or 500) when the backend API is unreachable or returns an unexpected error (graceful degradation).

### Key Entities

- **Incident**: The core entity representing a production incident record. Contains descriptive fields (title, date, organization, failure_mode, code_example), classification fields (category, severity, subcategory, affected_languages, tags), remediation fields (anti_pattern, remediation, static_rule_possible, semgrep_rule_id), reference fields (source_url), and system fields (id, version, embedding, deleted_at, created_at, updated_at, created_by).
- **Category (enum)**: Fixed set of 12 technical classifications: unsafe-regex, injection, deployment-error, missing-safety-check, race-condition, unsafe-api-usage, resource-exhaustion, data-consistency, missing-error-handling, cascading-failure, authentication-bypass, configuration-drift.
- **Severity (enum)**: Fixed set of 4 impact levels: critical, high, medium, low.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a new incident (filling all required fields) and see it in the list within 5 seconds of submission.
- **SC-002**: The incident list page loads and displays results within 2 seconds for up to 10,000 incidents in the database.
- **SC-003**: Filtering by category or severity returns accurate results within 1 second.
- **SC-004**: Keyword search returns relevant results within 2 seconds for a database of 10,000 incidents.
- **SC-005**: Concurrent updates to the same incident are correctly handled — only one succeeds, the other receives a clear conflict error.
- **SC-006**: 100% of soft-deleted incidents are excluded from list and detail views without manual intervention.
- **SC-007**: Users can complete the full create-read-update-delete lifecycle for a single incident in under 3 minutes.
- **SC-008**: All form validation errors are displayed inline next to the relevant field, preserving previously entered data.
- **SC-009**: When the backend is unreachable, users see a meaningful error message instead of a blank page or unhandled error.

## Assumptions

- Users are authenticated via Firebase Auth with valid session cookies before accessing any incident operation. Authentication setup is out of scope for this spec.
- The system is single-tenant in Phase A — all authenticated users share the same incident pool. Multi-tenancy is a future concern.
- The embedding field exists in the data model from day one but is always NULL in Phase A. No embedding generation, vector indexing, or semantic search is built.
- The 12 categories and 4 severities are fixed enums — adding new values requires a code change, not a UI configuration.
- The frontend uses skeleton loading states during data fetches and a confirmation modal before soft-delete, consistent with patterns from the predecessor system (oute-muscle).
- Keyword search uses simple case-insensitive partial matching, not full-text search or semantic search.
- No audit trail or change history is implemented in Phase A.
- The backend and frontend stacks are defined by the user: FastAPI + SQLAlchemy + PostgreSQL 16 (backend), SvelteKit + Svelte 5 + Tailwind CSS v4 (frontend), GCP Cloud Run (infra).
- The predecessor system (oute-muscle) validated patterns for optimistic locking, soft-delete with rule-active blocking, typed domain exceptions, and Pydantic frozen models — these are carried forward.
- Total count in pagination is exact (not approximate), improving on the predecessor system.
- **The application is English-only across all pages** — Paraglide, message files (`en.json`, `pt.json`, `es.json`), and `[lang=lang]` routing are removed from the entire project (landing page included). All routes use plain paths (`/`, `/incidents/`, `/incidents/new/`). The execution plan includes tasks to strip i18n from the existing landing page code.
- **Existing 006 code is refactored, not rewritten** — Backend code (`apps/api/`) is kept as-is (already follows spec). Frontend incident routes are moved from `[lang=lang]/incidents/` to `/incidents/` and stripped of i18n. Landing page components are refactored to hardcode English text. Infra provisioning tasks are added to cover the missing dependencies.
- **All infrastructure dependencies** (Cloud SQL, Cloud Run for API, Artifact Registry, Secret Manager, IAM, CI/CD) MUST be provisioned before application code that depends on them, per Mandamento XIII.
- Infrastructure provisioning will use `gcloud` CLI commands, executed by @renatobardi. The execution plan documents every step.
