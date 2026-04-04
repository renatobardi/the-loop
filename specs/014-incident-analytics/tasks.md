# Tasks: Incident Analytics Dashboard (Spec-014)

## Phase Overview

**Total**: 139 tasks (126 active, 13 deferred to Spec-015) | **Duration**: 13 days | **Coverage**: Backend (50) + Frontend (43) + Testing (46)

---

## Phase 1: Database & API Foundation (15 tasks, 3 days)

### Database Preparation
- [x] T001 Create alembic migration 009_add_analytics_indexes.py with 3 indexes (T005 deferred)
- [x] T002 Add index: postmortems(created_at DESC, root_cause_category)
- [x] T003 Add index: postmortems(team_responsible, created_at DESC)
- [x] T004 Add index: incidents(resolved_at, created_at DESC)
- [ ] T005 ~~Add index: timeline_events(data->>'rule_id', created_at DESC)~~ _deferred — Spec-015_
- [ ] T006 [P] Test migration up/down with integration test

### Data Models (Domain)
- [x] T007 Create domain/models.py additions: RootCauseCategory (reuse if exists)
- [x] T008 Create CategoryStats Pydantic model (frozen) in domain/models.py
- [x] T009 Create TeamStats Pydantic model (frozen) in domain/models.py
- [x] T010 Create TimelinePoint Pydantic model (frozen) in domain/models.py
- [ ] T011 ~~Create RuleEffect Pydantic model (frozen) in domain/models.py~~ _deferred — Spec-015_
- [x] T012 Create AnalyticsFilter Pydantic model (frozen) in domain/models.py
- [x] T013 Create AnalyticsPeriod Pydantic model with value: Literal["week","month","quarter","custom"] + optional date range
- [x] T014 Create AnalyticsSummary Pydantic model (frozen) in domain/models.py

### Ports (Interfaces)
- [x] T015 Create ports/analytics.py with AnalyticsRepoPort protocol

---

## Phase 2: Service & Repository Layer (18 tasks, 2 days)

### Raw SQL Queries
- [x] T016 Create adapters/postgres/analytics_queries.py module
- [x] T017 Implement Q1: SELECT by category with aggregates (include status filter: $status='all' skips filter; 'resolved' → i.resolved_at IS NOT NULL; 'unresolved' → i.resolved_at IS NULL)
- [x] T018 Implement Q2: Timeline with weekly bucketing and jsonb_object_agg (LEFT JOIN incidents for status filter; by_category dict always has all 5 RootCauseCategory keys with 0 for absent)
- [ ] T019 ~~Implement Q3: Rule effectiveness with temporal filters~~ _deferred — Spec-015_
- [x] T020 Add query sanitization + parameter binding (prevent SQL injection)

### Analytics Service
- [x] T021 Create domain/services.py: AnalyticsService class
- [x] T022 Implement get_summary() method with period parsing
- [x] T023 Implement get_by_category() method with sorting
- [x] T024 Implement get_by_team() method with top_categories extraction (top 3 per RF-003)
- [x] T025 Implement get_timeline() method with 52-week minimum (12 months)
- [ ] T026 ~~Implement get_rule_effectiveness() method~~ _deferred — Spec-015_
- [x] T027 Implement _parse_period() helper: week → last 7 days; month → last 30 days; quarter → start of current calendar quarter to today (quarter-to-date, end = min(today, end_of_quarter)); custom → AnalyticsPeriod.start_date/end_date
- [x] T028 Implement _normalize_stats() (ensure percentages sum to 100)

### Repository Implementation
- [x] T029 Create adapters/postgres/analytics_repository.py
- [x] T030 Implement PostgresAnalyticsRepository (all methods from port)
- [x] T031 Map raw SQL results to domain models (error handling for NULLs); Q1 avg_severity: SQL returns float 0.5–1.0 directly — no conversion needed; avg_resolution_days: SQL may return NULL (status=unresolved) → map to None (field is float | None)
- [x] T032 Add structured logging (query execution time)
- [ ] T033 [P] Write 20 integration tests (test_analytics_repository.py)

---

## Phase 3: API Routes (17 tasks, 2 days)

### Models
- [x] T034 Create api/models/analytics.py with request/response Pydantic models
- [x] T035 Add AnalyticsFilterRequest (period, team, category, status, start_date, end_date)
- [x] T036 Add CategoryStatsResponse
- [x] T037 Add TeamStatsResponse
- [x] T038 Add TimelinePointResponse
- [ ] T039 ~~Add RuleEffectResponse~~ _deferred — Spec-015_
- [x] T040 Add SummaryResponse with validation (non-negative counts)

### Endpoints
- [x] T041 Create api/routes/analytics.py
- [x] T042 Implement GET /api/v1/incidents/analytics/summary
- [x] T043 Implement GET /api/v1/incidents/analytics/by-category
- [x] T044 Implement GET /api/v1/incidents/analytics/by-team
- [x] T045 Implement GET /api/v1/incidents/analytics/timeline
- [ ] T046 ~~Implement GET /api/v1/rules/effectiveness~~ _deferred — Spec-015_

### Dependency Injection
- [x] T047 Add get_analytics_service() to api/deps.py
- [x] T048 Wire AnalyticsService + get_current_user (auth) into all 4 endpoints (→ 401 if unauthenticated)

### Error Handling
- [x] T049 Handle invalid period parameter → 400 Bad Request; also validate period=custom requires both start_date AND end_date → 400 if either missing
- [x] T050 Handle empty result set → 200 with empty arrays

---

## Phase 4: Frontend - Component Structure (43 tasks, 3 days)

### Type Definitions
- [x] T051 Create lib/types/analytics.ts with all interfaces
- [x] T052 Add CategoryStats, TeamStats, TimelinePoint interfaces (RuleEffect deferred — Spec-015)
- [x] T053 Add AnalyticsSummary, AnalyticsFilter interfaces
- [x] T054 Add Period type (week|month|quarter|custom)
- [x] T055 Add API response interfaces (mirror backend models)

### API Client
- [x] T056 Create lib/services/analytics.ts (separate file — do NOT add to incidents.ts); follows incidents.ts pattern: attaches Firebase auth token via getIdToken() to every request
- [x] T057 Implement getAnalyticsSummary(filters) → GET /summary
- [x] T058 Implement getAnalyticsByCategory(filters) → GET /by-category
- [x] T059 Implement getAnalyticsByTeam(filters) → GET /by-team
- [x] T060 Implement getAnalyticsTimeline(filters) → GET /timeline
- [ ] T061 ~~Implement getRuleEffectiveness(since) → GET /rules/effectiveness~~ _deferred — Spec-015_

### Page Component
- [x] T062 Create routes/incidents/analytics/+page.svelte
- [x] T063 Create routes/incidents/analytics/+page.ts (load function)
- [x] T064 Fetch 5 endpoints in load() via Promise.all using analytics.ts service functions (not raw fetch — service handles auth token): summary, by-category, by-team (filtered), by-team (unfiltered for dropdown — byTeamAll with team:null), timeline (+page.ts universal load — SSR on first request, CSR on filter updates)
- [x] T065 Handle errors in load (fallback to empty state)
- [x] T066 Implement period parameter from URL (?period=month); for custom: extract ?period=custom&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD

### Filter Component
- [x] T067 Create lib/components/analytics/AnalyticsFilters.svelte
- [x] T068 Implement period selector (Week, Month, Quarter, Custom)
- [x] T069 Implement custom date picker (if period=custom)
- [x] T070 Implement team single-select dropdown (team list sourced from byTeamAll — by-team called with all active filters EXCEPT team; shows only teams active in current period/category/status context)
- [x] T071 Implement category single-select dropdown (5 values matching RootCauseCategory enum)
- [x] T072 Implement status selector (Resolved, Unresolved, All)
- [x] T073 Add Apply / Reset buttons with URL param updates

### Dashboard Grid
- [x] T074 Create lib/components/analytics/DashboardGrid.svelte
- [x] T075 Responsive grid layout (1 col mobile, 2 cols tablet, 3+ desktop)
- [x] T076 Position AnalyticsFilters as sticky header
- [x] T077 Layout 4 card components in grid order: SummaryCard first (full-width span on all breakpoints), then CategoryHeatmap, TeamHeatmap, PatternTimeline

### Card Components
- [x] T078 Create lib/components/analytics/CategoryHeatmap.svelte
- [x] T079 Render horizontal bar chart using native SVG (5 categories — matches RootCauseCategory enum values; no Chart.js)
- [x] T080 Show count, percentage, avg_severity in tooltip
- [x] T081 Color bars by severity (red=error 100%, yellow=warning 50%)
- [x] T082 Create lib/components/analytics/TeamHeatmap.svelte
- [x] T083 Render table: Team | Count | Top 3 Categories
- [x] T084 Make table sortable by count (click header)
- [x] T085 Create lib/components/analytics/PatternTimeline.svelte
- [x] T086 Render line chart using native SVG (5 colors, one per RootCauseCategory value; no Chart.js); X-axis: monthly labels (12 ticks) over weekly data points
- [x] T087 Implement hover tooltip with week date + count
- [ ] T088 ~~Create lib/components/analytics/RuleEffectiveness.svelte~~ _deferred — Spec-015_
- [ ] T089 ~~Render table: Rule | Blocks/Week | Blocks/Month | Override % | Status~~ _deferred_
- [ ] T090 ~~Style deprecated rules gray, active rules normal~~ _deferred_
- [ ] T091 ~~Make table sortable by any column~~ _deferred_
- [x] T092 Create lib/components/analytics/SummaryCard.svelte
- [x] T093 Display: Total | Resolved | Unresolved | Avg Resolution Days (show "N/A" when avg_resolution_days is null)

---

## Phase 5: Styling, Accessibility & Testing (46 tasks, 3 days)

### Responsive Design
- [ ] T094 Test mobile (375px): DashboardGrid 1 col, fonts readable
- [ ] T095 Test tablet (768px): DashboardGrid 2 cols, cards wrap
- [ ] T096 Test desktop (1024px+): Full 3+ col layout
- [ ] T097 Test filters on mobile: Dropdowns accessible, date picker works

### Accessibility
- [ ] T098 Add alt text to all SVG charts
- [ ] T099 Ensure color contrast ratio > 4.5:1 (WCAG AA)
- [ ] T100 Add aria-label to interactive elements (filters, buttons)
- [ ] T101 Ensure keyboard navigation (Tab through filters, Enter to apply)
- [ ] T102 Test with screen reader (NVDA/JAWS equivalent)

### Styling & Design System
- [ ] T103 Use Tailwind design tokens (colors, spacing, shadows)
- [ ] T104 Style AnalyticsFilters consistent with Spec-013 components
- [ ] T105 Implement empty state: "No incidents in this period" message with suggestion to expand the selected period (per E-001)
- [ ] T106 Add loading skeleton cards while data fetches
- [ ] T107 Style error state: "Failed to load analytics" with retry button
- [ ] T136 Handle E-002: incidents with draft postmortem — include in count normally; "analysis pending" badge deferred (requires postmortem.status in queries)

### Unit Tests (Frontend)
- [ ] T108 Test CategoryHeatmap renders correct data
- [ ] T109 Test TeamHeatmap sorts by count
- [ ] T110 Test PatternTimeline plots 5 lines correctly (one per RootCauseCategory)
- [ ] T111 ~~Test RuleEffectiveness table interactive sorting~~ _deferred — Spec-015_
- [ ] T112 Test AnalyticsFilters URL param updates
- [ ] T113 Test empty state display (0 incidents)
- [ ] T114 [P] Write 15 Vitest tests (tests/unit/analytics/*.test.ts)

### API Tests
- [x] T115 Test GET /analytics/summary → 200 + valid JSON
- [x] T116 Test GET /by-category with team filter
- [x] T117 Test GET /by-team with category filter
- [x] T118 Test GET /timeline returns 12+ months of data (52+ weeks)
- [ ] T119 ~~Test GET /rules/effectiveness excludes deprecated rules~~ _deferred — Spec-015_
- [x] T120 Test invalid period parameter → 400
- [x] T121 Test missing auth → 401
- [x] T122 [P] Write 12 API tests (tests/api/test_analytics.py)

### Integration Tests
- [ ] T123 End-to-end: Load page, apply filters, data updates
- [ ] T124 E2E: Custom date range (period=custom + date picker)
- [ ] T125 E2E: Multi-filter (team + category + status)
- [ ] T126 E2E: Empty result set (0 incidents, show empty state)
- [ ] T127 E2E: Mobile breakpoint test (responsive design)
- [ ] T128 [P] Write 5 Cypress/Playwright E2E tests (optional for MVP)

### Documentation & QA
- [ ] T129 Update README.md: Add "Analytics Dashboard" section
- [ ] T130 Write ANALYTICS.md: User guide (how to filter, interpret charts)
- [ ] T131 Add JSDoc comments to all API endpoints
- [ ] T132 Verify all data in production looks sensible (sanity check)
- [ ] T133 Performance test: Load time <2s with 1000 incidents
- [ ] T134 Monitor query execution time in production (Grafana)
- [ ] T135 Final code review & merge prep
- [x] T137 Add structlog context fields: category, team, period on each analytics query (SC-O01)
- [x] T138 Export metric `analytics_dashboard_load_time_ms` via structlog timing in AnalyticsService (SC-O02)
- [x] T139 Export metric `analytics_query_result_count` per query type in repository (SC-O03)

---

## Dependencies & Blockers

- Blocked by: Spec-013 ✅ (postmortem data)
- Blocked by: Spec-012 ✅ (rule versioning)
- Unblocked: Spec-010 ✅ (base rules)

**No external dependencies** (no AWS, no Redis for MVP)

---

## Execution Order

1. ✅ Phase 1: Database (indexes, migrations)
2. → Phase 2: Service layer (SQL, AnalyticsService)
3. → Phase 3: API (4 endpoints)
4. → Phase 4: Frontend (components, page)
5. → Phase 5: Testing, accessibility, deployment

**Parallelization**: Phases 2 & 4 can overlap (team A on backend, team B on frontend) after Phase 1 indexes are applied.

---

## Acceptance Criteria

- [ ] All 126 active tasks marked `[x]` (13 deferred tasks excluded)
- [ ] 80%+ test coverage (unit + integration + API)
- [ ] CI gates pass (ruff, mypy, pytest)
- [ ] Mobile tested on real iPhone (375px)
- [ ] All 5 sections render with real data (RF-002, RF-003, RF-004, RF-006, RF-007)
- [ ] Filters apply without reload
- [ ] Empty state displays when needed
- [ ] Performance <2s dashboard load
- [ ] Accessibility WCAG 2.1 AA
- [ ] PR review + approved by @renatobardi

