# Tasks: Product Releases Notification

**Input**: Design documents from `/specs/022-product-releases-notification/`  
**Prerequisites**: spec.md (requirements, user stories), plan.md (technical context, architecture)

**Tests**: Unit tests included for backend services and frontend components (following pytest/vitest patterns in The Loop)

**Organization**: Tasks grouped by user story to enable independent implementation and parallel delivery.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in all descriptions
- Follow existing The Loop code patterns (hexagonal backend, Svelte 5 runes frontend)

## Path Conventions

- **Backend**: `apps/api/src/` (domain → ports → adapters → api)
- **Frontend**: `apps/web/src/` (lib → components, services, stores)
- **Database**: `apps/api/alembic/versions/` (Alembic migrations)
- **Tests**: `apps/api/tests/` (unit, api), `apps/web/tests/unit/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Database schema and API project initialization

- [ ] T001 [P] Create Alembic migration for Release and ReleaseNotificationStatus tables in `apps/api/alembic/versions/00XX_add_release_tables.py` with columns: Release (id, title, version, published_date, summary, changelog_html, breaking_changes_flag, documentation_url), ReleaseNotificationStatus (id, release_id, user_id, read_at, created_at)
- [ ] T002 [P] Create Release and ReleaseNotificationStatus Pydantic models in `apps/api/src/domain/models.py` (StrEnum for any enums, immutable, validated)
- [ ] T003 [P] Create domain exceptions for releases in `apps/api/src/domain/exceptions.py` (ReleaseNotFoundError, ReleaseAlreadyExistsError, NotificationAlreadyReadError)
- [ ] T004 [P] Create ReleaseRow and ReleaseNotificationStatusRow ORM models in `apps/api/src/adapters/postgres/models.py` using SQLAlchemy 2.0 patterns (DateTime with timezone=True, UUID primary keys, default UTC lambdas)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core services and repositories that all user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create ReleaseRepository in `apps/api/src/adapters/postgres/release_repository.py` with async methods: `get_all()`, `get_by_id()`, `create()`, `update_read_status()` (implement `_row_to_domain()` converter pattern)
- [ ] T006 Create ReleaseNotificationStatusRepository in `apps/api/src/adapters/postgres/notification_repository.py` with async methods: `get_by_user_and_release()`, `get_unread_count()`, `mark_as_read()`, `get_recent_by_user()`
- [ ] T007 Create ReleaseNotificationService in `apps/api/src/domain/services.py` with async methods: `get_unread_releases()`, `get_release_detail()`, `mark_as_read()` (uses repository DI, raises domain exceptions)
- [ ] T008 Create GitHub API client in `apps/api/src/adapters/github/releases_api.py` with async method `fetch_latest_releases()` that calls GitHub REST API, handles rate limiting, parses release data to Release domain model
- [ ] T009 Create/update release_repository endpoints in `apps/api/src/api/routes/releases.py`: `GET /api/v1/releases` (returns recent releases for user), `PATCH /api/v1/releases/{id}/status` (marks as read), follow existing route patterns (auth check, error mapping, response models)
- [ ] T010 [P] Update `apps/api/src/api/deps.py` to add `get_release_service()` dependency injector
- [ ] T011 [P] Create Svelte store for releases state in `apps/web/src/lib/stores/releases.ts` with Svelte 5 runes: unread count, recent releases list, detail panel state, loading/error states
- [ ] T012 [P] Create API service client in `apps/web/src/lib/services/releases.ts` with: `fetchReleases()`, `markAsRead()` methods, auth token attachment, error handling (401/429 retry logic following existing patterns)
- [ ] T013 [P] Create BellIcon base component in `apps/web/src/lib/components/releases/BellIcon.svelte` with Svelte 5 runes: badge visibility based on unread count, click handler to open/close dropdown, accessibility (aria-label, role="button")

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - See Unread Release Badge (Priority: P1) 🎯 MVP

**Goal**: Authenticated users see a visual badge on the bell icon when unread releases exist

**Independent Test**: 
- Badge appears when unread releases exist
- Badge disappears when all releases are marked read
- Badge persists across page refresh
- No badge appears when zero releases exist

### Tests for User Story 1

- [ ] T014 [P] [US1] Unit test for `ReleaseNotificationService.get_unread_releases()` in `apps/api/tests/unit/domain/test_release_notification_service.py` (mock repository, test filtering by user_id, count > 0 cases)
- [ ] T015 [P] [US1] API test for `GET /api/v1/releases` endpoint in `apps/api/tests/api/test_releases_routes.py` (auth required, returns releases with unread status, pagination limit)
- [ ] T016 [P] [US1] Component test for BellIcon badge visibility in `apps/web/tests/unit/components/test_bell_icon.svelte` (vitest with jsdom, test unread count binding, badge class conditionals)

### Implementation for User Story 1

- [ ] T017 [US1] Implement `get_unread_count()` method in ReleaseNotificationStatusRepository that returns count of read_at IS NULL records for user
- [ ] T018 [US1] Update BellIcon component to fetch releases on mount and display badge count in `apps/web/src/lib/components/releases/BellIcon.svelte` (use Svelte 5 $effect with guard for unread count > 0)
- [ ] T019 [US1] Add 120-second polling to BellIcon component using setInterval (cleanup on component destroy) to refresh unread count
- [ ] T020 [US1] Integrate BellIcon into Navbar in `apps/web/src/lib/components/Navbar.svelte` (follow existing nav item spacing and accessibility patterns)
- [ ] T021 [US1] Add unit tests for polling interval in BellIcon component test

**Checkpoint**: User Story 1 complete — badge shows/hides correctly based on unread releases and persists across refreshes

---

## Phase 4: User Story 2 - Open Release Dropdown (Priority: P1)

**Goal**: Clicking bell icon opens dropdown panel with recent releases (unread first, up to ~10 total, newest first within each group)

**Independent Test**: 
- Dropdown opens on bell icon click
- Dropdown closes on second click or click outside
- Recent releases displayed in correct order (unread first, then by date desc)
- Empty state message appears when no releases exist
- Dropdown responsive on mobile with touch dismissal

### Tests for User Story 2

- [ ] T022 [P] [US2] Component test for ReleasesDropdown opening/closing in `apps/web/tests/unit/components/test_releases_dropdown.svelte` (test click handlers, escape key dismiss, outside click handling)
- [ ] T023 [P] [US2] Component test for release list rendering in dropdown `apps/web/tests/unit/components/test_releases_dropdown.svelte` (test sorting unread→read, date ordering, empty state)

### Implementation for User Story 2

- [ ] T024 [US2] Create ReleasesDropdown component in `apps/web/src/lib/components/releases/ReleasesDropdown.svelte` with Svelte 5 runes: `open` state, `releases` list prop, `onClose` handler, display unread first (2-3 tasks worth of complexity)
- [ ] T025 [P] [US2] Implement dropdown close on outside click using click-outside directive pattern (follow existing patterns from analytics/MultiSelectDropdown.svelte)
- [ ] T026 [P] [US2] Implement release list rendering in dropdown with correct sort order: map releases with read_at status, sort unread first + by date desc
- [ ] T027 [US2] Implement "View All Releases" link in dropdown pointing to `/releases/` route
- [ ] T028 [US2] Connect ReleasesDropdown to BellIcon component trigger in Navbar (pass releases from store, handle open/close state)
- [ ] T029 [US2] Add mobile responsiveness testing for dropdown (ensure touch-dismiss works, dropdown positioned correctly on small screens)
- [ ] T030 [US2] Add accessibility: manage focus when dropdown opens (trap focus, aria-expanded, role="dialog" or "region")

**Checkpoint**: User Story 2 complete — dropdown opens/closes, displays releases in correct order, empty state works

---

## Phase 5: User Story 3 - Mark Releases as Read (Priority: P2)

**Goal**: Users can mark individual releases as read in dropdown; badge clears when all marked read

**Independent Test**: 
- Marking release as read removes visual indicator (bold/highlight)
- Badge disappears when all releases marked read
- Read status persists across page refreshes
- Already-read releases remain visible but unmarked

### Tests for User Story 3

- [ ] T031 [P] [US3] Unit test for `ReleaseNotificationStatusRepository.mark_as_read()` in `apps/api/tests/unit/adapters/test_notification_repository.py` (verify updates read_at timestamp to current UTC, returns updated entity)
- [ ] T032 [P] [US3] API test for `PATCH /api/v1/releases/{id}/status` endpoint in `apps/api/tests/api/test_releases_routes.py` (auth required, 404 on missing release, 200 returns updated notification status)
- [ ] T033 [P] [US3] Component test for mark-as-read interaction in `apps/web/tests/unit/components/test_release_item.svelte` (click handler calls service, optimistic UI update)

### Implementation for User Story 3

- [ ] T034 [US3] Implement auto-mark-as-read on detail panel open (will implement in US4, but database schema/API ready here)
- [ ] T035 [US3] Create API endpoint `PATCH /api/v1/releases/{release_id}/status` in `apps/api/src/api/routes/releases.py` that calls service.mark_as_read(), returns ReleaseNotificationStatusResponse
- [ ] T036 [US3] Update ReleasesDropdown to show read/unread visual indicator (e.g., bold for unread, gray for read) in release list items
- [ ] T037 [US3] Add "Mark as Read" button to each release item in dropdown (call `markAsRead()` from releases service, update store on success)
- [ ] T038 [US3] Update releases store to handle read status updates (toggle read_at field for specific release_id)
- [ ] T039 [US3] Implement badge auto-clear when all releases marked read (derive from unread count = 0)

**Checkpoint**: User Story 3 complete — marking releases as read updates UI and persists to database

---

## Phase 6: User Story 4 - View Full Release Details (Priority: P2)

**Goal**: Users can click release to view full changelog in side panel; auto-mark as read when panel opens

**Independent Test**: 
- Clicking release opens side panel from right
- Detail panel closes when user clicks X or outside
- Release auto-marked as read when panel opens
- Breaking changes highlighted
- Documentation link present and functional
- Panel responsive on mobile, scrollable content

### Tests for User Story 4

- [ ] T040 [P] [US4] Component test for ReleaseDetailPanel opening/closing in `apps/web/tests/unit/components/test_release_detail_panel.svelte` (test close on X, close on outside, auto-mark-as-read on mount)
- [ ] T041 [P] [US4] Component test for changelog rendering in panel `apps/web/tests/unit/components/test_release_detail_panel.svelte` (test breaking changes styling, doc link rendering)

### Implementation for User Story 4

- [ ] T042 [US4] Create ReleaseDetailPanel component in `apps/web/src/lib/components/releases/ReleaseDetailPanel.svelte` with Svelte 5 runes: `release` prop, `open` bindable prop, `onClose` handler, side-panel slide animation from right
- [ ] T043 [US4] Implement release detail rendering in panel: title, version, date, full changelog_html (sanitize with DOMPurify if needed for security), breaking_changes_flag styling
- [ ] T044 [US4] Implement auto-mark-as-read on detail panel mount using $effect() — call markAsRead() service when panel opens for first time
- [ ] T045 [US4] Add documentation link rendering in panel (if release.documentation_url exists, render <a> with target="_blank")
- [ ] T046 [US4] Implement close on outside-click for side panel (click on overlay dismisses panel)
- [ ] T047 [US4] Implement close button (X icon) in panel header
- [ ] T048 [US4] Add breaking changes visual styling (e.g., red badge, bold section header) in changelog rendering
- [ ] T049 [US4] Add mobile responsiveness for side panel (full-width on small screens, scrollable, readable on mobile)
- [ ] T050 [US4] Integrate ReleaseDetailPanel into ReleasesDropdown (pass selected release, manage open state, update store on mark-as-read)

**Checkpoint**: User Story 4 complete — full changelog viewable in side panel, auto-marks as read, closing works correctly

---

## Phase 7: GitHub Release Integration & Public Archive

**Purpose**: Sync releases from GitHub, provide public releases archive page

- [ ] T051 Create ReleaseNotificationManager wrapper component in `apps/web/src/lib/components/releases/ReleaseNotificationManager.svelte` that orchestrates: polling service, store updates, sub-component composition (BellIcon + Dropdown + DetailPanel)
- [ ] T052 [P] Implement `fetch_latest_releases()` in GitHub API adapter that: calls GitHub REST API `/repos/renatobardi/the-loop/releases`, parses JSON to Release domain models, handles rate limiting (60 req/hr unauth, 5k auth)
- [ ] T053 [P] Add GitHub API token configuration: read from GCP Secret Manager in backend startup, validate token has repo read access
- [ ] T054 Create or update `POST /api/v1/releases/sync` endpoint (admin-only or internal-only) to manually trigger GitHub sync (useful for testing, can be called on startup)
- [ ] T055 Create public releases archive page in `apps/web/src/routes/releases/+page.svelte` displaying all releases (no read status, pagination, searchable)
- [ ] T056 Create `[version]` detail route in `apps/web/src/routes/releases/[version]/+page.svelte` for individual release detail (public, no auth required, full changelog)
- [ ] T057 Add layout for releases routes in `apps/web/src/routes/releases/+layout.svelte` with Container, breadcrumb nav

---

## Phase 8: Testing & Cross-Story Integration

**Purpose**: Verify all user stories work together, end-to-end validation

- [ ] T058 [P] Integration test: "Full user workflow — badge → dropdown → detail → auto-read → badge clears" in `apps/api/tests/integration/test_release_notification_flow.py` (test against real PostgreSQL, new releases from GitHub API)
- [ ] T059 [P] Component integration test in `apps/web/tests/unit/components/test_release_notification_manager.svelte` (all sub-components together, state flow, closing/opening sequence)
- [ ] T060 E2E test via Playwright (optional, if time permits): User logs in → sees badge → opens dropdown → clicks release → views details → re-opens dropdown → no badge

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories, deployment readiness

- [ ] T061 [P] Documentation: Add quickstart.md with: GitHub API token setup, running migrations, polling interval explanation, architecture overview
- [ ] T062 [P] Documentation: Update CLAUDE.md with release notification feature summary (brief description of components, polling interval, data flow)
- [ ] T063 [P] Add logging for release sync operations in backend (log GitHub API calls, sync success/failure, polling errors)
- [ ] T064 [P] Add error state handling in frontend: display error message if releases fetch fails, provide retry button, graceful degradation (show "Unable to load releases" instead of breaking UI)
- [ ] T065 Code quality: Run ruff format/lint on all new Python files (apps/api/src/adapters/github/*, apps/api/src/api/routes/releases.py, repositories, services)
- [ ] T066 Code quality: Run ESLint + Prettier on all new TypeScript/Svelte files (apps/web/src/lib/components/releases/*, apps/web/src/lib/services/releases.ts, stores/releases.ts)
- [ ] T067 Type safety: Run mypy strict on all new backend files
- [ ] T068 Type safety: Run TypeScript strict mode check on all new frontend files
- [ ] T069 Run all unit tests locally: `pytest apps/api/tests/unit/` (confirm all pass with coverage ≥80%)
- [ ] T070 Run all frontend unit tests locally: `npm run test -- --run apps/web/tests/unit/` (confirm all pass)
- [ ] T071 Database migration validation: `alembic upgrade head` on fresh DB, verify Release and ReleaseNotificationStatus tables created correctly
- [ ] T072 Performance spot-check: Verify dropdown opens <1s, detail panel opens <1s, polling doesn't cause UI lag
- [ ] T073 Accessibility audit: Test keyboard navigation (Tab/Shift+Tab through dropdown, Escape closes), test with screen reader (aria labels on badge, links)
- [ ] T074 Mobile testing: Test on device or simulator at 375px width, verify dropdown responsive, touch-dismiss works, side panel readable
- [ ] T075 Run full CI suite locally before PR: lint, type-check, tests, build (both backend + frontend)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion — **BLOCKS all user stories**
- **Phase 3 & 4 (User Stories 1 & 2, P1)**: Depend on Phase 2 — can run in parallel
- **Phase 5 & 6 (User Stories 3 & 4, P2)**: Depend on Phase 2 (and optionally US1/US2 for UI flow, but can work in parallel)
- **Phase 7 (GitHub Integration)**: Depends on Phase 2 (can start once services ready, independent of UI stories)
- **Phase 8 (Integration Testing)**: Depends on all story phases completion
- **Phase 9 (Polish)**: Final phase after all features complete

### Within Each User Story

- Models/entities before services
- Services before endpoints/components
- Core implementation before integration
- Story complete before moving to next

### Parallel Opportunities

- All **Phase 1 tasks marked [P]** can run in parallel (different files, no dependencies)
- All **Phase 2 tasks marked [P]** can run in parallel within Phase 2 (once Phase 1 done)
- **US1 & US2 (Phase 3 & 4)** can run in parallel (independent frontend/backend work)
- **US3 & US4 (Phase 5 & 6)** can run in parallel (different components, integrated at end)
- **US3, US4, & GitHub sync (Phase 7)** can run in parallel after Phase 2
- **All [P] test tasks** within a story can run in parallel

**Example parallel run for 3 developers**:
```
Developer A:        Developer B:        Developer C:
Phase 1 (setup)     (blocked)           (blocked)
        ↓
Phase 2 (foundation)  Phase 2           Phase 2
        ↓
US1 (P1)            US2 (P1)            US3 (P2)
        ↓
Integration tests   Polish & docs
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (database, models)
2. Complete Phase 2: Foundational (services, repositories, API endpoints, stores, BellIcon component)
3. Complete Phase 3: User Story 1 (badge indicator)
4. **STOP and VALIDATE**: Test User Story 1 independently — badge appears/disappears correctly
5. Deploy to staging/production if ready

### Incremental Delivery

1. Complete Phases 1–2 → Foundation ready
2. Add US1 → Test independently → Deploy (MVP badge feature!)
3. Add US2 → Test independently → Deploy (add dropdown)
4. Add US3 → Test independently → Deploy (add mark-as-read)
5. Add US4 → Test independently → Deploy (add detail panel)
6. Add GitHub sync + archive → Test independently → Deploy (complete feature)

### Parallel Team Strategy (3+ developers)

1. All 3 developers complete Phases 1–2 together (~1–2 days)
2. Once Foundational done, split work:
   - **Dev A**: US1 + US2 (badge + dropdown)
   - **Dev B**: US3 + US4 (mark-as-read + detail panel)
   - **Dev C**: GitHub sync + public archive + testing
3. Stories complete in parallel, integrate at end with Phase 8 integration tests
4. All test locally, confirm cross-story flow works, then open single PR

---

## Notes

- [P] tasks = different files, can run in parallel within same phase
- [Story] label traces tasks to specific user story for code review/accountability
- Each user story designed to be independently completable and testable
- Write tests FIRST, ensure they fail before implementing (TDD)
- Commit after each task or logical group (keep commits small)
- Stop at each checkpoint to validate user story independently before moving forward
- Follow existing The Loop patterns: hexagonal backend, Svelte 5 runes, Tailwind 4 tokens
- No task should modify multiple unrelated files or cross-story concerns (keep stories isolated)

---

## Summary

- **Total Tasks**: 75
- **Backend Tasks**: ~25 (domain, repositories, services, API routes, tests)
- **Frontend Tasks**: ~30 (components, services, stores, tests)
- **Database Tasks**: 4 (migrations)
- **Infrastructure Tasks**: 4 (GitHub sync, public pages)
- **Testing & Polish Tasks**: 12 (integration, accessibility, performance, CI validation)
- **User Story Task Breakdown**:
  - US1 (P1 badge): 7 tasks
  - US2 (P1 dropdown): 9 tasks
  - US3 (P2 mark-as-read): 6 tasks
  - US4 (P2 detail panel): 9 tasks
  - Cross-cutting/foundational: 39 tasks
- **Parallel Opportunities**: ~60% of tasks can run in parallel across phases
- **Estimated Timeline**: 
  - Solo dev: 7–10 days (sequential)
  - 2 devs: 4–6 days (parallel after Phase 2)
  - 3 devs: 3–5 days (Phase 2 together, then parallel)
- **Suggested MVP Scope**: Complete US1 only for initial release (badge feature in ~2–3 days)
