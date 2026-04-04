# Plan: Incident Analytics Dashboard (Spec-014)

**Tech Stack**: SvelteKit 2 (Svelte 5 runes) | FastAPI 0.104+ | PostgreSQL 16 + pgvector

---

## Phase Overview

| Phase | Title | Duration | Tasks | Deliverable |
|-------|-------|----------|-------|-------------|
| 1 | Database & API Foundation | 3 days | 15 | 3 indexes, domain models, port |
| 2 | Service & Repo Layer | 2 days | 18 | AnalyticsService, RawSQL adapters, 20 tests |
| 3 | API Routes | 2 days | 17 | 4 endpoints, error handling, DI |
| 4 | Frontend Components | 3 days | 43 | 4 cards, filters, responsive grid |
| 5 | Styling, Accessibility & Testing | 3 days | 46 | E2E flows, Tailwind tokens, accessibility, metrics, docs |

**Total**: 13 days | 139 tasks (126 active, 13 deferred)

---

## Architecture

### Backend API Layer

#### Endpoints (4 total)

All 4 endpoints require authentication (`Depends(get_current_user)` → 401 if missing).

**GET /api/v1/incidents/analytics/summary**
- Response: `{total: int, resolved: int, unresolved: int, avg_resolution_days: float | null}`
- Params: `?period=week&team=backend&category=injection&status=resolved`
- Custom period: `?period=custom&start_date=2026-01-01&end_date=2026-03-31`
- No caching initially (Spec-C.X for Redis)

**GET /api/v1/incidents/analytics/by-category**
- Response: `[{category, count, percentage, avg_severity, avg_resolution_days: float | null}]`
- Sorted: descending count
- Params: same filters

**GET /api/v1/incidents/analytics/by-team**
- Response: `[{team, count, top_categories: [str, ...], avg_resolution_days: float | null}]`
- Sorted: descending count
- Top 3 categories per team

**GET /api/v1/incidents/analytics/timeline**
- Response: `[{week: str, count: int, by_category: dict}]` — `by_category` always contains all 5 RootCauseCategory keys (0 for absent)
- Returns 12+ months of data (52+ weeks)
- Params: same filters

> **GET /api/v1/rules/effectiveness** — deferred to Spec-015. Requires `rule_block` event tracking not yet implemented.

#### Raw SQL Queries (Optimized)

```sql
-- Q1: Incident count by category (with period filter)
SELECT 
  root_cause_category,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / (
    SELECT COUNT(*) FROM postmortems p2
    LEFT JOIN incidents i2 ON p2.incident_id = i2.id
    WHERE p2.created_at >= $start AND p2.created_at < $end
      AND ($status = 'all'
           OR ($status = 'resolved' AND i2.resolved_at IS NOT NULL)
           OR ($status = 'unresolved' AND i2.resolved_at IS NULL))
  ), 2) as percentage,
  ROUND(AVG(CASE WHEN severity_for_rule = 'error' THEN 1.0 ELSE 0.5 END), 2) as avg_severity,  -- maps to CategoryStats.avg_severity (error=1.0, warning=0.5)
  ROUND(AVG(EXTRACT(DAY FROM i.resolved_at - p.created_at)), 1) as avg_resolution_days
FROM postmortems p
LEFT JOIN incidents i ON p.incident_id = i.id
WHERE p.created_at >= $start AND p.created_at < $end
  AND (p.team_responsible = $team OR $team IS NULL)
  AND (p.root_cause_category = $category OR $category IS NULL)
  AND ($status = 'all'
       OR ($status = 'resolved' AND i.resolved_at IS NOT NULL)
       OR ($status = 'unresolved' AND i.resolved_at IS NULL))
GROUP BY root_cause_category
ORDER BY count DESC;

-- Q2: Timeline of incidents (weekly buckets)
-- by_category always contains all 5 RootCauseCategory keys (0 for absent categories)
SELECT
  DATE_TRUNC('week', p.created_at) as week,
  COUNT(*) as count,
  jsonb_object_agg(p.root_cause_category, COALESCE(cnt, 0)) as by_category
FROM postmortems p
LEFT JOIN incidents i ON p.incident_id = i.id
LEFT JOIN (
  SELECT DATE_TRUNC('week', created_at) as week, root_cause_category, COUNT(*) as cnt
  FROM postmortems
  WHERE created_at >= $start AND created_at < $end
  GROUP BY week, root_cause_category
) breakdown ON DATE_TRUNC('week', p.created_at) = breakdown.week AND p.root_cause_category = breakdown.root_cause_category
WHERE p.created_at >= $start AND p.created_at < $end
  AND ($status = 'all'
       OR ($status = 'resolved' AND i.resolved_at IS NOT NULL)
       OR ($status = 'unresolved' AND i.resolved_at IS NULL))
GROUP BY week
ORDER BY week ASC;

-- Q3 (deferred — Spec-015): Rule effectiveness query requires rule_block events
-- not yet tracked in timeline_events. Implement after Spec-015 webhook integration.
```

#### Database Indexes

Add after migration 009:
```python
# alembic/versions/009_add_analytics_indexes.py
CREATE INDEX idx_postmortems_created_category ON postmortems(created_at DESC, root_cause_category);
CREATE INDEX idx_postmortems_team_created ON postmortems(team_responsible, created_at DESC);
CREATE INDEX idx_incidents_resolved_created ON incidents(resolved_at, created_at DESC);
-- idx_timeline_events_rule deferred (Spec-015): not needed until rule_block events exist
```

### Backend Service Layer

**AnalyticsService** (domain/services.py)

```python
class AnalyticsService:
    def __init__(self, repo: AnalyticsRepoPort):
        self._repo = repo
    
    async def get_summary(self, period: AnalyticsPeriod, filters: AnalyticsFilter) -> AnalyticsSummary:
        start, end = self._parse_period(period)
        return await self._repo.get_summary(start, end, filters)
    
    async def get_by_category(self, period: AnalyticsPeriod, filters: AnalyticsFilter) -> list[CategoryStats]:
        start, end = self._parse_period(period)
        stats = await self._repo.get_by_category(start, end, filters)
        # Business logic: ensure categories are sorted, percentages sum to 100
        return self._normalize_stats(stats)
    
    async def get_by_team(self, period: AnalyticsPeriod, filters: AnalyticsFilter) -> list[TeamStats]:
        ...
    
    async def get_timeline(self, period: AnalyticsPeriod, filters: AnalyticsFilter) -> list[TimelinePoint]:
        ...
    
    def _parse_period(self, period: AnalyticsPeriod) -> tuple[datetime, datetime]:
        # "week" → last 7 days
        # "month" → last 30 days
        # "quarter" → start of current calendar quarter to today (quarter-to-date)
        #             Q1=Jan–Mar, Q2=Apr–Jun, Q3=Jul–Sep, Q4=Oct–Dec; end = min(today, end_of_quarter)
        # "custom" → period.start_date to period.end_date
        ...
```

**AnalyticsRepoPort** (ports/analytics.py)

```python
class AnalyticsRepoPort(Protocol):
    async def get_summary(self, start: datetime, end: datetime, filters: AnalyticsFilter) -> AnalyticsSummary: ...
    async def get_by_category(self, start: datetime, end: datetime, filters: AnalyticsFilter) -> list[CategoryStats]: ...
    async def get_by_team(self, start: datetime, end: datetime, filters: AnalyticsFilter) -> list[TeamStats]: ...
    async def get_timeline(self, start: datetime, end: datetime, filters: AnalyticsFilter) -> list[TimelinePoint]: ...
```

**PostgresAnalyticsRepository** (adapters/postgres/analytics_repository.py)
- Raw SQL strings live in `adapters/postgres/analytics_queries.py` (imported by repository)

- Executes raw SQL queries
- Maps results to domain models
- Handles NULL values, empty result sets
- Logs query execution time (structlog)

### Frontend Architecture

#### Page Structure

```
src/routes/incidents/analytics/
  +page.svelte          # Master (load + component orchestration)
  +page.ts             # SvelteKit universal load function (SSR + CSR)
```

#### Components

**DashboardGrid.svelte** (master layout)
- Grid container (responsive: 1 col mobile, 2 cols tablet, varies desktop)
- Loads AnalyticsFilters (sticky header)
- Grid children: SummaryCard (full-width, first), then CategoryHeatmap, TeamHeatmap, PatternTimeline

**AnalyticsFilters.svelte** (RF-006)
- Period selector: Week | Month | Quarter | Custom (date range)
- Team single-select dropdown (populated from `byTeamAll` — `GET /by-team` called with all active filters EXCEPT team; shows only teams with incidents in the current period/category/status context, never the full historical list)
- Category single-select dropdown (5 values — matches RootCauseCategory enum)
- Status selector: Resolved | Unresolved | All
- Apply / Reset buttons
- State: fetch via `applyFilters()` + URL param updates (pushState)

**CategoryHeatmap.svelte** (RF-002)
- Receives: `{categories: [{category, count, percentage, avg_severity}]}`
- Renders: Horizontal bar chart (native SVG — zero bundle overhead, full WCAG control)
- Hover: Shows absolute count + percentage + avg_severity
- Color: By severity (red=error, yellow=warning)

**TeamHeatmap.svelte** (RF-003)
- Receives: `{teams: [{team, count, top_categories}]}`
- Renders: Table or grid cards
- Each row: Team | Count | Top 3 categories (badges)
- Sortable by count

**PatternTimeline.svelte** (RF-004)
- Receives: `{timeline: [{week, count, by_category}]}`
- Renders: Line chart (native SVG — 5 lines, one per RootCauseCategory value)
- Tooltip on hover
- X-axis: Monthly labels (12 ticks), weekly data points — readable on mobile
- Y-axis: Count

**RuleEffectiveness.svelte** (RF-005) — _deferred to Spec-015_

#### State Management

**SvelteKit +page.ts**:
```typescript
export const load: PageLoad = async ({ fetch, url }) => {
  // Extract filters from URL params or use defaults
  const period = url.searchParams.get('period') ?? 'month';
  const team = url.searchParams.get('team') ?? null;
  const category = url.searchParams.get('category') ?? null;
  const startDate = url.searchParams.get('start_date') ?? null;  // only used when period=custom
  const endDate = url.searchParams.get('end_date') ?? null;      // only used when period=custom
  
  // +page.ts = universal load (SSR on first request, CSR on navigation/filter updates)
  // Do NOT use +page.server.ts — filters must re-fetch client-side without full reload
  //
  // Use lib/services/analytics.ts (not raw fetch) — service handles Firebase auth token attachment
  // byTeamFiltered: used by TeamHeatmap (respects all filters including team)
  // byTeamAll: respects period/category/status but NOT team filter — used to populate the team dropdown (D1 decision)
  const filters = { period, team, category, startDate, endDate };
  const [summary, byCategory, byTeamFiltered, byTeamAll, timeline] = await Promise.all([
    getAnalyticsSummary(filters),
    getAnalyticsByCategory(filters),
    getAnalyticsByTeam(filters),
    getAnalyticsByTeam({ ...filters, team: null }),  // byTeamAll: no team filter
    getAnalyticsTimeline(filters),
  ]);
  
  const teamList = byTeamAll.map((t: { team: string }) => t.team);
  
  // Return filter params alongside data so page component can initialize state
  return { summary, byCategory, byTeam: byTeamFiltered, teamList, timeline, period, team, category, startDate, endDate };
};
```

**Client State** (Svelte 5 runes):
```svelte
<script lang="ts">
  let { data } = $props();
  
  // data.period/team/category/startDate/endDate are extracted from URL params inside +page.ts load()
  let period = $state<string>(data.period);
  let selectedTeam = $state<string | null>(data.team);
  let selectedCategory = $state<string | null>(data.category);
  let startDate = $state<string | null>(data.startDate);  // only used when period=custom
  let endDate = $state<string | null>(data.endDate);      // only used when period=custom
  
  async function applyFilters() {
    // Update URL params (pushState)
    // Re-fetch data
  }
</script>
```

---

## Data Models

### Domain Models

```python
# Project convention: Pydantic BaseModel with frozen=True (NOT @dataclass)
# See existing domain/models.py for pattern reference

class CategoryStats(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: RootCauseCategory
    count: int
    percentage: float  # 0-100
    avg_severity: float  # 0-1 (error=1, warning=0.5)
    avg_resolution_days: float | None = None  # None when filtered to unresolved-only

class TeamStats(BaseModel):
    model_config = ConfigDict(frozen=True)

    team: str
    count: int
    top_categories: list[RootCauseCategory]
    avg_resolution_days: float | None = None  # None when filtered to unresolved-only

class TimelinePoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    week: datetime
    count: int
    by_category: dict[RootCauseCategory, int]

class AnalyticsSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    total: int
    resolved: int
    unresolved: int
    avg_resolution_days: float | None = None  # None when filtered to unresolved-only

class AnalyticsFilter(BaseModel):
    model_config = ConfigDict(frozen=True)

    team: str | None = None
    category: RootCauseCategory | None = None
    status: Literal["resolved", "unresolved", "all"] = "all"

class AnalyticsPeriod(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: Literal["week", "month", "quarter", "custom"]
    start_date: datetime | None = None  # if custom
    end_date: datetime | None = None    # if custom
```

### API Request/Response Models

```python
class AnalyticsFilterRequest(BaseModel):
    period: str = "month"
    team: str | None = None
    category: str | None = None
    status: str = "all"
    start_date: datetime | None = None  # required when period="custom"
    end_date: datetime | None = None    # required when period="custom"

class CategoryStatsResponse(BaseModel):
    category: str
    count: int
    percentage: float
    avg_severity: float
    avg_resolution_days: float | None = None

class TeamStatsResponse(BaseModel):
    team: str
    count: int
    top_categories: list[str]
    avg_resolution_days: float | None = None

class TimelinePointResponse(BaseModel):
    week: str  # ISO date string
    count: int
    by_category: dict[str, int]

class SummaryResponse(BaseModel):
    total: int
    resolved: int
    unresolved: int
    avg_resolution_days: float | None = None
```

---

## Testing Strategy

### Unit Tests (src → test coverage >80%)
- AnalyticsService._parse_period()
- Filter normalization
- Date arithmetic

### Integration Tests (SQL queries)
- get_by_category() with various periods + filters
- get_timeline() returns 12+ months of data (52+ weeks)
- Empty result handling (0 incidents)

### API Tests (endpoints)
- GET /analytics/summary → 200 + valid JSON
- Filters applied correctly (team=backend → only backend incidents)
- Invalid period → 400 Bad Request
- Auth required → 401 if not logged in

### Frontend Tests (Vitest)
- CategoryHeatmap renders categories
- Filters apply correctly (URL updates)
- Empty state shown when no data
- Responsive grid breakpoints (mobile 1col, tablet 2col)

---

## Performance Targets

- **Dashboard load**: <2s (with 1000 incidentes)
- **API response**: <500ms per endpoint
- **Render time**: <100ms (Svelte reactivity)
- **Memory**: <50MB JS bundle (frontend)

**Strategy**:
- Raw SQL aggregates (faster than ORM)
- Indexes on hot columns
- Every filter change updates URL params and triggers a full server re-fetch (no client-side filter cache in MVP)
- Pagination deferred to Spec-C.X (if 10k+ incidents)

---

## Deployment

**Phase Order**:
1. Database migration (indexes)
2. Backend API (no breaking changes)
3. Frontend page (can be dark initially, gradually light up)
4. Monitoring (Grafana dashboard)

**Cloud Run**:
```
gcloud run deploy theloop-api \
  --update-env-vars "DATABASE_URL=..." \
  --set-cloudsql-instances theloop-db
```

**Rollback**:
- API: Revert Docker image
- Frontend: Revert SvelteKit build
- DB: Alembic downgrade (migration reversible)

---

## Risk & Mitigation

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Slow queries (1000+ incidentes) | Medium | Raw SQL + indexes; monitor query times |
| Filter combinations = no results | Low | Show empty state with suggestion to broaden |
| Deprecated rule confusion | Low | _(deferred — RF-005/Spec-015)_ |
| Mobile responsiveness broken | High | Test on 375px+ breakpoint early |

---

## Success Criteria

✅ All endpoints respond <500ms  
✅ Dashboard renders in <2s  
✅ Filters work without page reload  
✅ 80%+ test coverage  
✅ Mobile responsive (tested on iPhone SE)  
✅ Accessibility WCAG 2.1 AA  
✅ Production data looks sensible (sanity check values)

