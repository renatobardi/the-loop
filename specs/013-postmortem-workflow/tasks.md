# Tasks-013: Postmortem Workflow

**Total Tasks**: 62  
**Timeline**: 1-2 weeks (9 days intense)  
**Phases**: 6 sequential phases

---

## Phase 1: Domain & Database Setup (T001–T010)

**Goal**: Create domain models, Alembic migration, test locally.

- [ ] T001 Create `domain/models.py` additions: `RootCauseCategory`, `PostmortumSeverity` enums
- [ ] T002 Create `domain/models.py` addition: `Postmortem` Pydantic model (frozen)
- [ ] T003 Create `domain/models.py` addition: `RootCauseTemplate` Pydantic model (frozen)
- [ ] T004 [P] Create domain exceptions: `PostmortumNotFoundError`, `PostmortumAlreadyExistsError`, `PostmortumLockedError`
- [ ] T005 Create `adapters/postgres/models.py` addition: `PostmortumRow` SQLAlchemy ORM model
- [ ] T006 [P] Create Alembic migration `008_create_postmortems_table.py` with constraints
- [ ] T007 Run migration locally: `alembic upgrade head`
- [ ] T008 [P] Create `adapters/postgres/postmortem_templates.py` with 15 hardcoded templates
- [ ] T009 Verify templates data structure (all 15 load, no errors)
- [ ] T010 Commit Phase 1: models + migration + templates

---

## Phase 2: Repository & Service (T011–T025)

**Goal**: Implement data access layer and business logic.

### Repository
- [ ] T011 Create `ports/postmortem_repository.py` protocol with 5 methods
- [ ] T012 [P] Create `adapters/postgres/postmortem_repository.py`: `get_by_incident_id()`
- [ ] T013 [P] Implement `create()` method (insert + return Postmortem domain model)
- [ ] T014 [P] Implement `update()` method (only if not locked)
- [ ] T015 [P] Implement `get_summary()` method (aggregations: count by category, by team)
- [ ] T016 Add `_row_to_domain()` helper (ORM → domain model conversion)

### Service
- [ ] T017 Create `domain/services.py` addition: `PostmortumService`
- [ ] T018 [P] Implement `create_postmortem()` (validation, DB write)
- [ ] T019 [P] Implement `update_postmortem()` (check locked status, update)
- [ ] T020 Implement `get_postmortem()` (read, handle not found)
- [ ] T021 [P] Implement `lock_postmortem()` (prevent edits after incident resolved)
- [ ] T022 Implement `get_templates()` (return hardcoded template list)

### Unit Tests
- [ ] T023 [P] Create `tests/unit/domain/test_postmortem_models.py`
  - Test Postmortem validation (description length, category enum)
  - Test frozen model (immutability)
- [ ] T024 [P] Create `tests/unit/adapters/test_postmortem_repository.py`
  - Mock DB, test CRUD operations
- [ ] T025 Create `tests/unit/domain/test_postmortem_service.py`
  - Test validation, locking, error handling

---

## Phase 3: API Routes (T026–T045)

**Goal**: Expose postmortem endpoints with full error handling.

### Models
- [ ] T026 Create `api/models/postmortems.py`: request models (CreatePostmortumRequest, UpdatePostmortumRequest)
- [ ] T027 [P] Create response models: `PostmortumResponse`, `TemplatesResponse`

### Routes
- [ ] T028 Create `api/routes/postmortems.py` file structure
- [ ] T029 [P] Implement `POST /api/v1/incidents/{id}/postmortems`
  - Validate incident exists
  - Create postmortem
  - Return 201 + response
- [ ] T030 [P] Implement `GET /api/v1/incidents/{id}/postmortem`
  - Handle not found → 404
  - Return postmortem (even if locked)
- [ ] T031 [P] Implement `PUT /api/v1/incidents/{id}/postmortem`
  - Check if locked → 403
  - Update fields
  - Return 200

### Additional Endpoints
- [ ] T032 [P] Implement `GET /api/v1/postmortem/templates`
  - Return list of 15 hardcoded templates
  - No DB call, return from code
- [ ] T033 Implement `GET /api/v1/postmortems/summary` (for Spec-014)
  - Count by category
  - Count by team
  - Total count
- [ ] T034 [P] Implement `GET /api/v1/postmortems/summary?team=backend` (filtered)

### Error Handling
- [ ] T035 [P] Add error handlers for all endpoints
  - PostmortumNotFoundError → 404
  - PostmortumLockedError → 403
  - Validation errors → 422
- [ ] T036 Add proper status codes + error messages

### Dependencies
- [ ] T037 [P] Add to `api/deps.py`: `get_postmortem_service()`, `get_postmortem_repository()`
- [ ] T038 Register routes in `api/main.py`: `app.include_router(postmortem_router)`

### API Tests
- [ ] T039 [P] Create `tests/api/test_postmortems.py`
  - Test POST success → 201
  - Test POST with invalid data → 422
  - Test GET → 200
  - Test PUT → 200
- [ ] T040 [P] Test PUT on locked postmortem → 403
- [ ] T041 [P] Test GET templates → 200 + 15 templates
- [ ] T042 [P] Test summary endpoint → aggregations correct
- [ ] T043 Test 404 cases (incident not found, postmortem not found)
- [ ] T044 [P] Test error messages are user-friendly
- [ ] T045 Test rate limiting (if applicable, 60/min for GET, 10/min for POST)

---

## Phase 4: Incident Integration (T046–T050)

**Goal**: Enforce postmortem requirement before incident resolution.

### Backend Changes
- [ ] T046 Modify `api/routes/incidents.py`: Update PATCH handler
  - Check if new status == 'resolved'
  - Validate postmortem exists
  - Return 400 if missing
- [ ] T047 [P] Add `lock_postmortem()` call when incident transitions to resolved
- [ ] T048 Add tests: Try to resolve without postmortem → 400
- [ ] T049 [P] Add test: Successful resolve with postmortem → 200 + locked

### Frontend Changes (Incident Detail)
- [ ] T050 Update incident detail view to show postmortem status badge
  - "Postmortem: Pending" (red)
  - "Postmortem: Completed" (green, locked)

---

## Phase 5: Frontend UI (T051–T062)

**Goal**: Build postmortem form + template picker.

### Components
- [ ] T051 Create `lib/components/incidents/PostmortumForm.svelte`
  - Form with all fields (category, description, pattern, team, severity, rule_id)
  - Template picker dropdown
  - Real-time validation
  - Submit button
- [ ] T052 [P] Create `lib/components/incidents/PostmortumReadOnly.svelte`
  - Show all fields locked/disabled
  - Display "Locked after resolution" badge
  - Show created_by, created_at, updated_at
- [ ] T053 [P] Create `lib/components/incidents/PostmortumTemplate Picker.svelte`
  - Dropdown with 15 templates
  - Preview of template fields
  - "Apply" button to auto-fill form

### Routes
- [ ] T054 Update `/incidents/{id}/` route
  - Add postmortem section (form or read-only)
- [ ] T055 Create `/incidents/{id}/postmortem/` sub-route if needed
  - Or embed in detail view

### Form Logic
- [ ] T056 [P] Implement template selection logic
  - Fetch templates from API on mount
  - Apply template → auto-fill form
- [ ] T057 Implement form validation
  - Min/max length for description
  - Category required
  - Team required
  - Pattern validation (regex, if provided)
- [ ] T058 [P] Implement error message display
  - Field-level errors under each input
  - Character counter for description
- [ ] T059 Implement submit handler
  - POST to API
  - Show loading state
  - Handle 400/422 errors
  - Success message + redirect or close

### Styling
- [ ] T060 [P] Add Tailwind classes + design tokens
  - Use bg-bg, text-text, input styles
  - Match design system
- [ ] T061 Add accessibility features
  - Label associations
  - ARIA attributes
  - Keyboard navigation

### Integration Tests (E2E)
- [ ] T062 [P] Test flow: Create incident → Fill postmortem → Resolve
  - Create incident via UI
  - See "Postmortem: Pending"
  - Fill form with template
  - Submit
  - Try to resolve → success
  - See "Postmortem: Completed (locked)"

---

## Phase 6: Testing & Docs (T063–T068)

**Goal**: Full coverage, documentation, production-ready.

### Testing
- [ ] T063 Run full test suite: `pytest tests/ --cov=src -k postmortem`
- [ ] T064 [P] Verify coverage ≥80% for postmortem code
- [ ] T065 [P] Run Ruff: `ruff check src/ tests/` → 0 errors
- [ ] T066 [P] Run mypy: `mypy src/ --strict` → 0 errors

### Documentation
- [ ] T067 Create `specs/013-postmortem-workflow/CLAUDE.md`
  - Patterns: domain models, repository, service
  - API contract notes
  - Frontend component patterns
  - Common errors + solutions
- [ ] T068 Update project `CLAUDE.md` (root) with Spec-013 notes
  - Postmortem workflow brief
  - Hardcoded templates location
  - Link to Spec-013/CLAUDE.md

### Finalization
- [ ] T069 Commit all changes
  - Message: "feat(spec-013): postmortem workflow — incident root cause capture"
- [ ] T070 Create PR to `chore/spec-013-postmortem` branch
- [ ] T071 [P] Self-review: Check security, performance, consistency
- [ ] T072 [P] Wait for code review + approve
- [ ] T073 Merge PR (or mark ready for merge)

---

## Parallelization Opportunities

### Phase 1 (Setup)
- T004 + T006 + T008: Exceptions, migration, templates can be done in parallel

### Phase 2 (Repository & Service)
- T012-T015: All repository methods can be coded in parallel
- T018-T022: All service methods can be coded in parallel
- T023-T025: All unit tests can be run in parallel (independent fixtures)

### Phase 3 (API)
- T029-T034: All endpoints can be coded in parallel
- T035-T038: Error handling + dependencies can be done in parallel
- T039-T045: All API tests can be run in parallel

### Phase 5 (Frontend)
- T051-T053: Components can be built in parallel
- T056-T062: All form logic + tests can be parallelized

---

## Checkpoint Validations

### After T010 (Phase 1)
- [ ] Migration runs successfully
- [ ] 15 templates load without errors
- [ ] No database conflicts

### After T025 (Phase 2)
- [ ] All unit tests pass
- [ ] Coverage ≥80% for domain + adapters
- [ ] No mypy/ruff errors

### After T045 (Phase 3)
- [ ] All 5 endpoints return correct responses
- [ ] Error cases handled (404, 403, 422)
- [ ] 10+ API tests passing

### After T050 (Phase 4)
- [ ] Cannot resolve incident without postmortem
- [ ] Postmortem locked after resolution
- [ ] Tests pass for incident integration

### After T062 (Phase 5)
- [ ] Form displays all fields correctly
- [ ] Template picker works
- [ ] Form submission succeeds
- [ ] E2E test passes

### After T073 (Phase 6)
- [ ] Coverage ≥80%
- [ ] Ruff: 0 errors
- [ ] MyPy: 0 errors
- [ ] PR created + ready to merge

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Test coverage | ≥80% |
| API latency | POST <500ms, GET <200ms |
| Ruff/mypy | 0 errors |
| Form completion | <2 min (with templates) |
| E2E tests | 100% passing |
| Documentation | CLAUDE.md + inline comments |

---

## References

- **Spec-001**: Incident CRUD (foundation)
- **Spec-012**: Semgrep Phase B (rules to prevent patterns)
- **Spec-014**: Analytics (reads postmortem summaries)
- **CLAUDE.md**: Project patterns (hexagonal, Pydantic, FastAPI, SvelteKit)

---

**Status**: Ready for implementation  
**Estimated effort**: 50-70 hours (intense 1-2 week sprint)  
**Next phases**: Spec-014 (Analytics), Spec-015 (Webhooks)
