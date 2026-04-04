# Tasks: Incident Analytics Dashboard (Spec-014)

## Phase Overview

**Total**: 87 tasks | **Duration**: 12 days | **Coverage**: Backend (25) + Frontend (35) + Testing (27)

---

## Phase 1: Database & API Foundation (15 tasks, 3 days)

### Database Preparation
- [ ] T001 Create alembic migration 009_add_analytics_indexes.py with 4 indexes
- [ ] T002 Add index: postmortems(created_at DESC, root_cause_category)
- [ ] T003 Add index: postmortems(team_responsible, created_at DESC)
- [ ] T004 Add index: incidents(resolved_at, created_at DESC)
- [ ] T005 Add index: timeline_events(data->>'rule_id', created_at DESC)
- [ ] T006 [P] Test migration up/down with integration test

### Data Models (Domain)
- [ ] T007 Create domain/models.py additions: RootCauseCategory (reuse if exists)
- [ ] T008 Create CategoryStats frozen dataclass in domain/models.py
- [ ] T009 Create TeamStats frozen dataclass in domain/models.py
- [ ] T010 Create TimelinePoint frozen dataclass in domain/models.py
- [ ] T011 Create RuleEffect frozen dataclass in domain/models.py
- [ ] T012 Create AnalyticsFilter frozen dataclass in domain/models.py
- [ ] T013 Create Period union type (week|month|quarter|custom)
- [ ] T014 Create AnalyticsSummary frozen dataclass in domain/models.py

### Ports (Interfaces)
- [ ] T015 Create ports/analytics.py with AnalyticsRepoPort protocol

---

## Phase 2: Service & Repository Layer (18 tasks, 2 days)

### Raw SQL Queries
- [ ] T016 Create adapters/postgres/analytics_queries.py module
- [ ] T017 Implement Q1: SELECT by category with aggregates
- [ ] T018 Implement Q2: Timeline with weekly bucketing and jsonb_object_agg
- [ ] T019 Implement Q3: Rule effectiveness with temporal filters
- [ ] T020 Add query sanitization + parameter binding (prevent SQL injection)

### Analytics Service
- [ ] T021 Create domain/services.py: AnalyticsService class
- [ ] T022 Implement get_summary() method with period parsing
- [ ] T023 Implement get_by_category() method with sorting
- [ ] T024 Implement get_by_team() method with top_categories extraction
- [ ] T025 Implement get_timeline() method with 12-week minimum
- [ ] T026 Implement get_rule_effectiveness() method
- [ ] T027 Implement _parse_period() helper (week/month/quarter → dates)
- [ ] T028 Implement _normalize_stats() (ensure percentages sum to 100)

### Repository Implementation
- [ ] T029 Create adapters/postgres/analytics_repository.py
- [ ] T030 Implement PostgresAnalyticsRepository (all methods from port)
- [ ] T031 Map raw SQL results to domain models (error handling for NULLs)
- [ ] T032 Add structured logging (query execution time)
- [ ] T033 [P] Write 20 integration tests (test_analytics_repository.py)

---

## Phase 3: API Routes (15 tasks, 2 days)

### Models
- [ ] T034 Create api/models/analytics.py with request/response dataclasses
- [ ] T035 Add AnalyticsFilterRequest (period, team, category, status)
- [ ] T036 Add CategoryStatsResponse
- [ ] T037 Add TeamStatsResponse
- [ ] T038 Add TimelinePointResponse
- [ ] T039 Add RuleEffectResponse
- [ ] T040 Add SummaryResponse with validation (counts > 0)

### Endpoints
- [ ] T041 Create api/routes/analytics.py
- [ ] T042 Implement GET /api/v1/incidents/analytics/summary
- [ ] T043 Implement GET /api/v1/incidents/analytics/by-category
- [ ] T044 Implement GET /api/v1/incidents/analytics/by-team
- [ ] T045 Implement GET /api/v1/incidents/analytics/timeline
- [ ] T046 Implement GET /api/v1/rules/effectiveness

### Dependency Injection
- [ ] T047 Add get_analytics_service() to api/deps.py
- [ ] T048 Wire AnalyticsService into all 5 endpoints

### Error Handling
- [ ] T049 Handle invalid period parameter → 400 Bad Request
- [ ] T050 Handle empty result set → 200 with empty arrays

---

## Phase 4: Frontend - Component Structure (25 tasks, 3 days)

### Type Definitions
- [ ] T051 Create lib/types/analytics.ts with all interfaces
- [ ] T052 Add CategoryStats, TeamStats, TimelinePoint, RuleEffect
- [ ] T053 Add AnalyticsSummary, AnalyticsFilter interfaces
- [ ] T054 Add Period type (week|month|quarter|custom)
- [ ] T055 Add API response interfaces (mirror backend models)

### API Client
- [ ] T056 Add to lib/services/incidents.ts:
- [ ] T057 Implement getAnalyticsSummary(filters) → GET /summary
- [ ] T058 Implement getAnalyticsByCategory(filters) → GET /by-category
- [ ] T059 Implement getAnalyticsByTeam(filters) → GET /by-team
- [ ] T060 Implement getAnalyticsTimeline(filters) → GET /timeline
- [ ] T061 Implement getRuleEffectiveness(since) → GET /rules/effectiveness

### Page Component
- [ ] T062 Create routes/incidents/analytics/+page.svelte
- [ ] T063 Create routes/incidents/analytics/+page.ts (load function)
- [ ] T064 Fetch all 5 data endpoints in load (server-side)
- [ ] T065 Handle errors in load (fallback to empty state)
- [ ] T066 Implement period parameter from URL (?period=month)

### Filter Component
- [ ] T067 Create lib/components/analytics/AnalyticsFilters.svelte
- [ ] T068 Implement period selector (Week, Month, Quarter, Custom)
- [ ] T069 Implement custom date picker (if period=custom)
- [ ] T070 Implement team multi-select dropdown
- [ ] T071 Implement category multi-select checkbox group
- [ ] T072 Implement status selector (Resolved, Unresolved, All)
- [ ] T073 Add Apply / Reset buttons with URL param updates

### Dashboard Grid
- [ ] T074 Create lib/components/analytics/DashboardGrid.svelte
- [ ] T075 Responsive grid layout (1 col mobile, 2 cols tablet, 3+ desktop)
- [ ] T076 Position AnalyticsFilters as sticky header
- [ ] T077 Layout 5 card components

### Card Components
- [ ] T078 Create lib/components/analytics/CategoryHeatmap.svelte
- [ ] T079 Render horizontal bar chart (6 categories max)
- [ ] T080 Show count, percentage, avg_severity in tooltip
- [ ] T081 Color bars by severity (red=error 100%, yellow=warning 50%)
- [ ] T082 Create lib/components/analytics/TeamHeatmap.svelte
- [ ] T083 Render table: Team | Count | Top 3 Categories
- [ ] T084 Make table sortable by count (click header)
- [ ] T085 Create lib/components/analytics/PatternTimeline.svelte
- [ ] T086 Render line chart (6 colors, one per category)
- [ ] T087 Implement hover tooltip with week date + count
- [ ] T088 Create lib/components/analytics/RuleEffectiveness.svelte
- [ ] T089 Render table: Rule | Blocks/Week | Blocks/Month | Override % | Status
- [ ] T090 Style deprecated rules gray, active rules normal
- [ ] T091 Make table sortable by any column
- [ ] T092 Create lib/components/analytics/SummaryCard.svelte
- [ ] T093 Display: Total | Resolved | Unresolved | Avg Resolution Days

---

## Phase 5: Styling, Accessibility & Testing (25 tasks, 3 days)

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
- [ ] T105 Implement empty state: "No incidents in this period" message
- [ ] T106 Add loading skeleton cards while data fetches
- [ ] T107 Style error state: "Failed to load analytics" with retry button

### Unit Tests (Frontend)
- [ ] T108 Test CategoryHeatmap renders correct data
- [ ] T109 Test TeamHeatmap sorts by count
- [ ] T110 Test PatternTimeline plots 6 lines correctly
- [ ] T111 Test RuleEffectiveness table interactive sorting
- [ ] T112 Test AnalyticsFilters URL param updates
- [ ] T113 Test empty state display (0 incidents)
- [ ] T114 [P] Write 15 Vitest tests (tests/unit/analytics/*.test.ts)

### API Tests
- [ ] T115 Test GET /analytics/summary → 200 + valid JSON
- [ ] T116 Test GET /by-category with team filter
- [ ] T117 Test GET /by-team with category filter
- [ ] T118 Test GET /timeline returns 12+ weeks
- [ ] T119 Test GET /rules/effectiveness excludes deprecated rules
- [ ] T120 Test invalid period parameter → 400
- [ ] T121 Test missing auth → 401
- [ ] T122 [P] Write 12 API tests (tests/api/test_analytics.py)

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
3. → Phase 3: API (5 endpoints)
4. → Phase 4: Frontend (components, page)
5. → Phase 5: Testing, accessibility, deployment

**Parallelization**: Phases 2 & 4 can overlap (team A on backend, team B on frontend) after Phase 1 indexes are applied.

---

## Acceptance Criteria

- [ ] All 87 tasks marked `[x]`
- [ ] 80%+ test coverage (unit + integration + API)
- [ ] CI gates pass (ruff, mypy, pytest)
- [ ] Mobile tested on real iPhone (375px)
- [ ] All 5 cards render with real data
- [ ] Filters apply without reload
- [ ] Empty state displays when needed
- [ ] Performance <2s dashboard load
- [ ] Accessibility WCAG 2.1 AA
- [ ] PR review + approved by @renatobardi

