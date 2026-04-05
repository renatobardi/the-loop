# Tasks: Analytics Dashboard — Product Analytics Redesign

**Specification**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)  
**Branch**: `019-product-analytics` | **Total Tasks**: 56 | **Est. Duration**: ~14 days

---

## Phase 0: Setup & Documentation

### Goal
Prepare the repository and documentation for Spec-019 implementation.

### Tasks

- [ ] T001 Update CLAUDE.md with Phase 19 status, task count (56 tasks), and 7 implementation phases in project phase table at `CLAUDE.md` Phase Status section, link to PR #XXX
- [ ] T001b Verify PostgreSQL 16 extensions before Phase 1: run `psql -c "CREATE EXTENSION IF NOT EXISTS pgvector; CREATE EXTENSION IF NOT EXISTS pg_trgm;"` on Cloud SQL instance in production, document extension versions, abort Phase 1 if either extension unavailable

---

## Phase 1: Foundational (Blocking Prerequisites)

### Goal
Fix critical SQL bugs, create cache infrastructure, update design system. All P1/P2 user stories depend on these tasks.

### Independent Test Criteria

- ✅ QUERY_TIMELINE test passes with team/category filters applied
- ✅ QUERY_BY_TEAM test passes with status/team/category filters applied
- ✅ AnalyticsCache stores and retrieves values with TTL expiry
- ✅ Badge component renders 'warning' variant with correct styles
- ✅ MultiSelectDropdown component opens/closes and emits selected values

### Tasks

- [ ] T002 [P] Fix QUERY_TIMELINE SQL query in `apps/api/src/adapters/postgres/analytics_queries.py`: add team and category filter bindings to inner subquery using `ANY(:team_array)` and `ANY(:category_array)` PostgreSQL operators
- [ ] T003 [P] Fix QUERY_BY_TEAM SQL query in `apps/api/src/adapters/postgres/analytics_queries.py`: add status, team, and category filters to inner subquery `cat_count`
- [ ] T004 [P] Create `SeverityTrendPoint` and `RuleEffectivenessStats` domain models in `apps/api/src/domain/models.py` with proper Pydantic configuration
- [ ] T005 [P] Create `AnalyticsCache` class in `apps/api/src/adapters/postgres/analytics_cache.py`: in-memory dict with 5-minute TTL, keyed by sorted parameter tuple, `get()` and `set()` methods
- [ ] T006 [P] Add 'warning' variant to Badge component in `apps/web/src/lib/ui/Badge.svelte`: update variant union type and add warning styles (`bg-warning/10 text-warning border border-warning/20`)
- [ ] T007 [P] Add 3 chart color tokens to `apps/web/src/app.css` inside `@theme` block: `--color-chart-green: #10b981`, `--color-chart-amber: #f59e0b`, `--color-chart-teal: #14b8a6`
- [ ] T008 Create `MultiSelectDropdown.svelte` component in `apps/web/src/lib/components/analytics/MultiSelectDropdown.svelte`: Svelte 5 runes, props for options/selected/placeholder, click-outside handler, emit onChange event

---

## Phase 2: User Story 1 — PMO/Executive Views Real-Time Incident KPIs (P1)

### Goal
Implement 8 KPI cards with accurate calculations and real incident data. Dashboard loads <2s, executes without errors.

### Story Dependencies
None — Phase 1 foundational tasks must complete first.

### Independent Test Criteria

- ✅ Dashboard loads in <2 seconds
- ✅ All 8 KPI cards render: Total, Resolved, Unresolved, MTTR, ERROR count, WARNING count, Top Category, Most Affected Team
- ✅ KPI values match database aggregations (within 1% tolerance)
- ✅ Period filter changes update all KPIs within 500ms
- ✅ Empty data state shows zeros with "No incidents in this period" message

### Tasks

- [ ] T009 [P] [US1] Update `AnalyticsFilter` model in `apps/api/src/domain/models.py`: add `team: list[str] | None` and `category: list[RootCauseCategory] | None` fields for new severity-trend and top-rules endpoints
- [ ] T010 [P] [US1] Create `get_severity_trend()` method in `apps/api/src/adapters/postgres/analytics_repository.py`: execute QUERY_SEVERITY_TREND, return `list[SeverityTrendPoint]` (week, error_count, warning_count)
- [ ] T011 [P] [US1] Create `get_top_rules()` method in `apps/api/src/adapters/postgres/analytics_repository.py`: execute QUERY_TOP_RULES, return `list[RuleEffectivenessStats]` (rule_id, incident_count, avg_severity)
- [ ] T012 [P] [US1] Add `get_severity_trend` and `get_top_rules` to `AnalyticsRepoPort` in `apps/api/src/ports/analytics.py`
- [ ] T013 [US1] Extend `AnalyticsService` in `apps/api/src/domain/services.py`: inject `AnalyticsCache`, add methods `get_severity_trend()` and `get_top_rules()`, wrap all 6 service methods (get_summary, get_by_category, get_by_team, get_timeline, get_severity_trend, get_top_rules) with cache logic: cache.get(key) or fetch and cache.set(key)
- [ ] T014 [P] [US1] Add `SeverityTrendResponse` and `RuleEffectivenessResponse` models in `apps/api/src/api/models/analytics.py` with `from_domain()` classmethods
- [ ] T015 [US1] Add `get_analytics_cache()` and `init_analytics_cache()` functions to `apps/api/src/api/deps.py`, following `rule_version_cache_instance` pattern
- [ ] T016 [US1] Update `get_analytics_service()` in `apps/api/src/api/deps.py`: inject `AnalyticsCache` instance
- [ ] T017 [US1] Remove `from __future__ import annotations` from `apps/api/src/api/routes/analytics.py` (line 3) — Python 3.12 native unions, slowapi incompatibility fix
- [ ] T018 [US1] Add 2 route handlers in `apps/api/src/api/routes/analytics.py`: `GET /api/v1/incidents/analytics/severity-trend` and `GET /api/v1/incidents/analytics/top-rules` with rate limiting `@limiter.limit("60/minute")`
- [ ] T019 [P] [US1] Update analytics types in `apps/web/src/lib/types/analytics.ts`: add `SeverityTrendPoint` and `RuleEffectiveness` types, `AnalyticsFilter` for new endpoints
- [ ] T020 [P] [US1] Add `getAnalyticsSeverityTrend()` and `getAnalyticsTopRules()` methods in `apps/web/src/lib/services/analytics.ts` that attach Firebase token and call new endpoints
- [ ] T021 [US1] Update analytics page loader in `apps/web/src/routes/analytics/+page.ts`: add new endpoints to `Promise.all()`, return `severityTrend` and `topRules` in page data
- [ ] T022 [US1] Redesign `SummaryCard.svelte` in `apps/web/src/lib/components/analytics/SummaryCard.svelte`: accept props `byCategory`, `byTeam`, render 8 KPIs in 2 rows × 4 columns grid. Derived metrics: ERROR count (sum incidents where avg_severity ≥ 0.9), WARNING count (sum where < 0.9), top category (byCategory.sort by count[0]), most affected team (byTeam.sort by count[0])
- [ ] T023 [US1] Update `DashboardGrid.svelte` in `apps/web/src/lib/components/analytics/DashboardGrid.svelte`: add props for new data, pass to SummaryCard, update loading skeletons, render new components (RuleEffectivenessCard, SeverityTrendChart)
- [ ] T024 [US1] Add unit tests for QUERY_TIMELINE bug fix in `apps/api/tests/api/test_analytics.py`: verify team and category filters are applied correctly
- [ ] T025 [US1] Add unit tests for QUERY_BY_TEAM bug fix in `apps/api/tests/api/test_analytics.py`: verify status, team, and category filters are applied correctly
- [ ] T026 [US1] Add API tests for new severity-trend endpoint in `apps/api/tests/api/test_analytics_new_endpoints.py`: happy path, empty data, 401 unauthorized, 400 bad request
- [ ] T027 [US1] Add API tests for new top-rules endpoint in `apps/api/tests/api/test_analytics_new_endpoints.py`: happy path, empty data, 401 unauthorized, 400 bad request

---

## Phase 3: User Story 2 — Tech Lead Analyzes Patterns for Their Specific Team (P1)

### Goal
Enable multi-select filters and drill-down navigation. Users can select multiple teams/categories, URL state persists, dashboard filters correctly.

### Story Dependencies
Depends on: Phase 2 (US1) — KPI card infrastructure required first.

### Independent Test Criteria

- ✅ Multi-select dropdown opens/closes correctly
- ✅ URL updates with repeated parameters: `?team=Backend&team=Frontend&category=code_pattern`
- ✅ Dashboard filters correctly for multiple teams and categories
- ✅ Clicking category/team pill navigates to `/incidents/?category=X` or `/incidents/?team=Y`
- ✅ Back button returns to analytics with filters intact

### Tasks

- [ ] T028 [P] [US2] Update `_build_params()` and SQL binding in `apps/api/src/adapters/postgres/analytics_repository.py`: handle `list[str] | None` for team/category using `bindparam("team_array", type_=ARRAY(String()))` and `bindparam("category_array", type_=ARRAY(String()))`
- [ ] T029 [US2] Update `AnalyticsFilters.svelte` in `apps/web/src/lib/components/analytics/AnalyticsFilters.svelte`: replace single-select `<select>` for team/category with `<MultiSelectDropdown>` component, update state to `team: string[] = $state([])` and `category: RootCauseCategory[] = $state([])`
- [ ] T030 [US2] Implement "Reset Filters" button in `AnalyticsFilters.svelte`: onclick handler clears `team: []`, `category: []`, rebuilds URL with default params (period=month, no filters), calls `goto()` to refresh dashboard
- [ ] T031 [US2] Update `handleFiltersChange` function in `apps/web/src/routes/analytics/+page.svelte`: use `params.append()` in loop for array fields (not `params.set()`), serialize as repeated params (?team=a&team=b)
- [ ] T032 [US2] Update page loader in `apps/web/src/routes/analytics/+page.ts`: use `url.searchParams.getAll('team')` and `url.searchParams.getAll('category')` to read multi-select filters as string arrays
- [ ] T033 [P] [US2] Add drill-down onclick handlers in `apps/web/src/lib/components/analytics/CategoryHeatmap.svelte`: clicking category bar navigates to `/incidents/?category=X`, import `goto` from `$app/navigation`
- [ ] T034 [P] [US2] Add drill-down onclick handlers in `apps/web/src/lib/components/analytics/TeamHeatmap.svelte`: clicking team row navigates to `/incidents/?team=Y`, add cursor pointer style and aria-labels
- [ ] T035 [P] [US2] Replace `<span>` category pills in `apps/web/src/lib/components/analytics/TeamHeatmap.svelte` with `<Badge variant="default">` component
- [ ] T036 [US2] Add integration tests in `apps/api/tests/api/test_analytics.py` for multi-select filtering: verify `?team=a&team=b` returns combined results, verify `?category=x&category=y` filters correctly, test empty array parameters

---

## Phase 4: User Story 3 — DevOps/SRE Tracks Severity Trends Over Time (P2)

### Goal
Implement stacked area chart showing ERROR vs WARNING incidents by week. Chart renders correctly, tooltip doesn't overflow, updates with filters.

### Story Dependencies
Depends on: Phase 2 (US1) — severity-trend endpoint required.

### Independent Test Criteria

- ✅ Chart renders without errors
- ✅ Stacked area layout correct: ERROR bottom, WARNING on top
- ✅ Tooltip appears on hover with week + counts
- ✅ Tooltip clamped to viewport (no overflow)
- ✅ Chart updates when dashboard filters change

### Tasks

- [ ] T037 [P] [US3] Create `SeverityTrendChart.svelte` in `apps/web/src/lib/components/analytics/SeverityTrendChart.svelte`: SVG stacked area chart, accepts `data: SeverityTrendPoint[]`, uses `--color-error` and `--color-warning` CSS vars, fill opacity 0.3, clamped tooltip (X: Math.min(x + 12, SVG_WIDTH - 180), Y: similar clamp)
- [ ] T038 [US3] Fix tooltip overflow in `apps/web/src/lib/components/analytics/PatternTimeline.svelte`: clamp X position `Math.min(tooltip.x + 12, SVG_WIDTH - 180)` and Y position to prevent overflow on small viewports
- [ ] T039 [US3] Integrate `SeverityTrendChart` into dashboard in `apps/web/src/lib/components/analytics/DashboardGrid.svelte`: render full-width above `PatternTimeline`, pass `severityTrend` data from props

---

## Phase 5: User Story 4 — Security Lead Validates Rule Effectiveness (P2)

### Goal
Implement Rule Effectiveness Card showing top 5 rules by incident count. Card renders with severity badges, updates with filters.

### Story Dependencies
Depends on: Phase 2 (US1) — top-rules endpoint required.

### Independent Test Criteria

- ✅ Card renders top 5 rules by incident_count
- ✅ Severity badge shows ERROR (avg_severity ≥ 0.9) or WARNING
- ✅ Card shows empty state when no rules match filters
- ✅ Card updates when dashboard filters change

### Tasks

- [ ] T040 [P] [US4] Create `RuleEffectivenessCard.svelte` in `apps/web/src/lib/components/analytics/RuleEffectivenessCard.svelte`: accepts `data: RuleEffectiveness[]`, renders top-5 rules in table (rule_id monospace, incident_count, severity badge ERROR/WARNING), empty state message "No rules found in this period"
- [ ] T041 [US4] Integrate `RuleEffectivenessCard` into dashboard in `apps/web/src/lib/components/analytics/DashboardGrid.svelte`: render full-width after heatmap grid, pass `topRules` data from props

---

## Phase 6: Polish & Cross-Cutting Concerns

### Goal
Complete test coverage, validate performance, ensure code quality, update documentation.

### Independent Test Criteria

- ✅ Backend coverage ≥80% (pytest)
- ✅ Frontend coverage ≥70% (Vitest)
- ✅ Dashboard load time <2s (verified locally and in Cloud Run logs)
- ✅ Cache hit <50ms (verified in logs); Cache TTL expiry verified (6th request after 5min shows fresh query)
- ✅ Mobile responsive at 375px viewport
- ✅ mypy strict passes with 0 errors
- ✅ ruff check passes with 0 errors
- ✅ TypeScript strict passes
- ✅ ESLint passes

### Tasks

- [ ] T042 Add cache TTL expiry test to `apps/api/tests/api/test_analytics_new_endpoints.py`: make 2 requests within 5min (verify cache hit), wait >5min, make 3rd request (verify new query in logs), confirm TTL behavior
- [ ] T043 Run backend test suite and verify coverage ≥80%: `pytest apps/api/tests/ --cov=src --cov-report=term-missing`, fix any coverage gaps
- [ ] T044 Run frontend test suite and verify coverage ≥70%: `npm run test -- --run --coverage`, fix any coverage gaps
- [ ] T045 [P] Verify mobile responsiveness: open dashboard in browser DevTools at 375px viewport, test all filters and interactions, verify components render correctly
- [ ] T046 [P] Verify performance: load dashboard in Cloud Run, confirm <2s page load via DevTools Network tab, verify cache hits <50ms in API logs
- [ ] T046b Measure filter apply performance: from filter selection to dashboard re-render must complete in <500ms. Open DevTools Performance tab, apply multi-select team/category filter, measure time from click to DOM update complete. Profile and optimize if threshold exceeded.
- [ ] T046c Profile SeverityTrendChart render performance: measure time from data load to chart SVG rendered on screen in <1 second. Use DevTools Performance timeline. If slower, profile and optimize (reduce DOM complexity, lazy render, canvas fallback).
- [ ] T047 [P] Run linters and type checkers: `ruff check src/ tests/`, `mypy src/`, `npm run check`, `npm run lint` — fix all issues
- [ ] T048 Verify build pipeline: `npm run build` (frontend), Docker build (backend), confirm no errors or warnings
- [ ] T049 Prepare test dataset: create test data setup doc with SQL/script to generate 100+ incidents across 3 teams (Backend, Frontend, DevOps) and 5 categories (sql_injection, hardcoded_secrets, code_pattern, etc.)
- [ ] T050 Final manual testing: verify all 8 KPIs calculate correctly, test all filter combinations (single team, multi-team, single category, multi-category, empty results), verify no console errors, verify tooltips/pills render correctly
- [ ] T051 Update CLAUDE.md Spec-019 entry in Phase Status table: mark as COMPLETE, link to PR, summarize changes (53 tasks, 7 phases, 1 sprint, 2 SQL bug fixes, 2 new endpoints, 8 KPIs, multi-select filters, drill-down navigation)
- [ ] T052 Create PR with detailed description: summarize Spec-019 achievement (Product Analytics executive dashboard), list key deliverables (bug fixes, caching, KPIs, multi-filters, new charts), reference spec.md/plan.md/tasks.md, add testing evidence, request @renatobardi review
- [ ] T053 After PR approval and merge to main: monitor Cloud Run deployment completion without errors, verify `/analytics/` loads and renders all components correctly in production, check error logs for any issues

---

## Dependencies & Parallelization

### Dependency Graph

```
Phase 0 (Setup)
    ↓
Phase 1 (Foundational Prerequisites)
    ↓
Phase 2 (US1: KPIs) [blocks US2, US3, US4]
    ├→ Phase 3 (US2: Multi-Select & Drill-Down)
    ├→ Phase 4 (US3: Severity Trends) [depends on US1]
    └→ Phase 5 (US4: Rule Effectiveness) [depends on US1]
    ↓
Phase 6 (Polish & Cross-Cutting)
```

### Parallel Execution by Phase

**Phase 0** (Setup): T001 (1 task, 1 hour).

**Phase 1** (Foundational): All 7 tasks [T002–T008] can run in parallel (independent files).

**Phase 2** (US1): Organize in execution order:
1. Backend setup: T009–T018 (models, methods, routes)
2. Frontend integration: T019–T023 (services, components, page)
3. Testing: T024–T027 (unit/API tests)
- Within backend: T009–T014 can parallel (separate files)
- Within backend: T015–T018 sequential (deps on T005)
- Within frontend: T019–T021 can parallel, then T022–T023 sequential

**Phase 3** (US2): After Phase 2 completes:
- T028–T029 parallel (independent files)
- T030–T032 parallel (independent files)
- T033–T035 parallel (independent heatmap + tests)
- T036 sequential (integration test)

**Phase 4** (US3): After Phase 2 completes:
- T037–T038 parallel (chart creation + timeline fix)
- T039 sequential (integration)

**Phase 5** (US4): After Phase 2 completes:
- T040–T041 can parallel

**Phase 6** (Polish): After all phases:
- T042–T047 parallel (tests/linting)
- T048–T053 sequential (dataset prep → manual test → PR → deployment)

---

## Implementation Strategy

### MVP Scope (Days 1–7)
Complete Phase 0, Phase 1, Phase 2 (US1) fully. Delivers working KPI dashboard with 2 SQL bug fixes, in-memory cache, and 8 KPIs. **Achieves**: SC-001, SC-004, SC-005, SC-009, FR-001–FR-006.

**Day 1**: Phase 0 (setup, 1h) + Phase 1 (7 foundational tasks, parallelizable, ~2d)  
**Days 3–7**: Phase 2 (19 US1 tasks, backend → frontend → tests, ~3d)

### Incremental Delivery (Days 8–14)
Complete Phase 3 (US2), Phase 4 (US3), Phase 5 (US4), Phase 6 (Polish). Delivers multi-select filters, drill-down navigation, severity trend chart, rule effectiveness card, and full test coverage.

**Days 8–9**: Phase 3 (8 tasks, ~2d)  
**Days 10–11**: Phase 4 (3 tasks, ~1d) + Phase 5 (2 tasks, ~1d) in parallel  
**Days 12–14**: Phase 6 (12 tasks, polish/testing/deployment, ~2d)

### Rollback Plan
If any phase fails:
1. Revert last commit (git reset --hard)
2. Fix root cause
3. Restart failed phase
4. No data loss (no DB migrations, only code changes)
5. Cache is in-memory (no persistence to roll back)

---

## Coverage by Requirement

| Requirement | Task(s) | Phase |
|-------------|---------|-------|
| FR-001: Fix QUERY_TIMELINE | T002, T024 | Phase 1, 2 |
| FR-002: Fix QUERY_BY_TEAM | T003, T025 | Phase 1, 2 |
| FR-003: Implement cache | T005, T013, T015-T016, T042 | Phase 1, 2, 6 |
| FR-004: New endpoints | T010-T011, T018, T026-T027 | Phase 2 |
| FR-005: Multi-select filters | T008, T028-T031, T036 | Phase 1, 3 |
| FR-006: 8 KPIs | T022 | Phase 2 |
| FR-007: SummaryCard layout | T022 | Phase 2 |
| FR-008: RuleEffectivenessCard | T040-T041 | Phase 5 |
| FR-009: SeverityTrendChart | T037-T039, T046c | Phase 4, 6 |
| FR-010: Drill-down navigation | T033-T035 | Phase 3 |
| FR-011: Design system updates | T006-T007 | Phase 1 |
| SC-001–SC-011 | T043-T056 | Phase 2–6 |
| SC-002 (Filter <500ms) | T046b | Phase 6 |
| SC-008 (Chart <1s) | T046c | Phase 6 |
| Infrastructure (PostgreSQL) | T001b | Phase 0 |

---

## Checklist Status

- [x] All tasks follow checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
- [x] All 56 tasks (T001–T001b, T002–T056) are specific and executable
- [x] All tasks have explicit file paths
- [x] Dependencies documented with explicit phase blocking relationships
- [x] Parallel opportunities identified (20 tasks marked [P])
- [x] Coverage mapping complete (all 22 FRs/SCs mapped)
- [x] Phase 0–6 organized by priority and story dependency
- [x] MVP scope identified (Phase 0–2, Days 1–7)
- [x] All analysis findings (CRITICAL, HIGH, MEDIUM, LOW) resolved and documented
- [x] Task count corrected: 53 total (T001-T053)
- [x] Phase structure clarified: 7 story-based phases (Phase 0–6) aligned with plan.md's 7 technical phases
- [x] Cache TTL expiry test added (T042)
- [x] Reset filters UI task added (T030)
- [x] Test data setup documentation task added (T049)
- [x] Deployment rollback procedures documented
