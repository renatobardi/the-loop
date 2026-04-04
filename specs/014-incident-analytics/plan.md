# Plan: Incident Analytics Dashboard (Spec-014)

**Tech Stack**: SvelteKit 2 (Svelte 5 runes) | FastAPI 0.104+ | PostgreSQL 16 + pgvector

---

## Phase Overview

| Phase | Title | Duration | Tasks | Deliverable |
|-------|-------|----------|-------|-------------|
| 1 | Database & API Foundation | 3 days | 15-20 | 4 endpoints, 5 aggregation queries |
| 2 | Service & Repo Layer | 2 days | 10-15 | AnalyticsService, RawSQL adapters, 20 tests |
| 3 | Frontend Components | 3 days | 20-25 | 5 cards, filters, responsive grid |
| 4 | Integration & Styling | 2 days | 15-20 | E2E flows, Tailwind tokens, accessibility |
| 5 | Performance & Polish | 2 days | 10-15 | Caching, metrics, docs, final tests |

**Total**: 12 days | ~75-95 tasks

---

## Architecture

### Backend API Layer

#### Endpoints (4 total)

**GET /api/v1/incidents/analytics/summary**
- Response: `{total: int, resolved: int, unresolved: int, avg_resolution_days: float}`
- Params: `?period=week&team=backend&category=injection&status=resolved`
- No caching initially (Spec-C.X for Redis)

**GET /api/v1/incidents/analytics/by-category**
- Response: `[{category, count, percentage, avg_severity, avg_resolution_days}]`
- Sorted: descending count
- Params: same filters

**GET /api/v1/incidents/analytics/by-team**
- Response: `[{team, count, top_categories: [str, ...], avg_resolution_days}]`
- Sorted: descending count
- Top 5 categories per team

**GET /api/v1/rules/effectiveness**
- Response: `[{rule_id, rule_version, blocks_week, blocks_month, override_rate, status}]`
- Status: "active" | "deprecated"
- Filters: ?since=2026-03-01 (start date for counting blocks)

#### Raw SQL Queries (Optimized)

```sql
-- Q1: Incident count by category (with period filter)
SELECT 
  root_cause_category,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM postmortems WHERE created_at >= $start), 2) as percentage,
  ROUND(AVG(CASE WHEN severity_for_rule = 'error' THEN 1 ELSE 0 END) * 100, 2) as error_percentage,
  ROUND(AVG(EXTRACT(DAY FROM i.resolved_at - p.created_at)), 1) as avg_resolution_days
FROM postmortems p
LEFT JOIN incidents i ON p.incident_id = i.id
WHERE p.created_at >= $start AND p.created_at < $end
  AND (p.team_responsible = $team OR $team IS NULL)
  AND (p.root_cause_category = $category OR $category IS NULL)
GROUP BY root_cause_category
ORDER BY count DESC;

-- Q2: Timeline of incidents (weekly buckets)
SELECT
  DATE_TRUNC('week', p.created_at) as week,
  COUNT(*) as count,
  jsonb_object_agg(p.root_cause_category, COALESCE(cnt, 0)) as by_category
FROM postmortems p
LEFT JOIN (
  SELECT DATE_TRUNC('week', created_at) as week, root_cause_category, COUNT(*) as cnt
  FROM postmortems
  WHERE created_at >= $start AND created_at < $end
  GROUP BY week, root_cause_category
) breakdown ON DATE_TRUNC('week', p.created_at) = breakdown.week AND p.root_cause_category = breakdown.root_cause_category
WHERE p.created_at >= $start AND p.created_at < $end
GROUP BY week
ORDER BY week DESC;

-- Q3: Rules effectiveness (count blocks per rule version)
SELECT
  r.id,
  r.version,
  COALESCE(SUM(CASE WHEN t.event_type = 'rule_block' AND t.created_at >= NOW() - '7 days'::interval THEN 1 ELSE 0 END), 0) as blocks_week,
  COALESCE(SUM(CASE WHEN t.event_type = 'rule_block' AND t.created_at >= NOW() - '30 days'::interval THEN 1 ELSE 0 END), 0) as blocks_month,
  rv.status
FROM rule_versions r
LEFT JOIN timeline_events t ON t.data->>'rule_id' = r.id AND t.created_at >= $start
LEFT JOIN rule_versions rv ON rv.id = r.id
WHERE r.published_at < NOW()
ORDER BY blocks_week DESC;
```

#### Database Indexes

Add after migration 009:
```python
# alembic/versions/009_add_analytics_indexes.py
CREATE INDEX idx_postmortems_created_category ON postmortems(created_at DESC, root_cause_category);
CREATE INDEX idx_postmortems_team_created ON postmortems(team_responsible, created_at DESC);
CREATE INDEX idx_incidents_resolved_created ON incidents(resolved_at, created_at DESC);
CREATE INDEX idx_timeline_events_rule ON timeline_events(data->>'rule_id', created_at DESC);
```

### Backend Service Layer

**AnalyticsService** (domain/services.py)

```python
class AnalyticsService:
    def __init__(self, repo: AnalyticsRepoPort):
        self._repo = repo
    
    async def get_summary(self, period: Period, filters: AnalyticsFilter) -> AnalyticsSummary:
        start, end = self._parse_period(period)
        return await self._repo.get_summary(start, end, filters)
    
    async def get_by_category(self, period: Period, filters: AnalyticsFilter) -> list[CategoryStats]:
        start, end = self._parse_period(period)
        stats = await self._repo.get_by_category(start, end, filters)
        # Business logic: ensure categories are sorted, percentages sum to 100
        return self._normalize_stats(stats)
    
    async def get_by_team(self, period: Period, filters: AnalyticsFilter) -> list[TeamStats]:
        ...
    
    async def get_timeline(self, period: Period, filters: AnalyticsFilter) -> list[TimelinePoint]:
        ...
    
    async def get_rule_effectiveness(self, since: datetime) -> list[RuleEffect]:
        ...
    
    def _parse_period(self, period: Period) -> tuple[datetime, datetime]:
        # "week" → last 7 days, "month" → last 30 days, etc.
        ...
```

**AnalyticsRepoPort** (ports/analytics.py)

```python
class AnalyticsRepoPort(Protocol):
    async def get_summary(self, start: datetime, end: datetime, filters: AnalyticsFilter) -> AnalyticsSummary: ...
    async def get_by_category(self, start: datetime, end: datetime, filters: AnalyticsFilter) -> list[CategoryStats]: ...
    async def get_by_team(self, start: datetime, end: datetime, filters: AnalyticsFilter) -> list[TeamStats]: ...
    async def get_timeline(self, start: datetime, end: datetime, filters: AnalyticsFilter) -> list[TimelinePoint]: ...
    async def get_rule_effectiveness(self, since: datetime) -> list[RuleEffect]: ...
```

**PostgresAnalyticsRepository** (adapters/postgres/analytics_queries.py)

- Executes raw SQL queries
- Maps results to domain models
- Handles NULL values, empty result sets
- Logs query execution time (structlog)

### Frontend Architecture

#### Page Structure

```
src/routes/incidents/analytics/
  +page.svelte          # Master (load + component orchestration)
  +page.ts             # SvelteKit load function (fetch data server-side)
```

#### Components

**DashboardGrid.svelte** (master layout)
- Grid container (responsive: 1 col mobile, 2 cols tablet, varies desktop)
- Loads AnalyticsFilters (sticky header)
- Grid children: 5 cards

**AnalyticsFilters.svelte** (RF-006)
- Period selector: Week | Month | Quarter | Custom (date range)
- Team multi-select (fetchable from API or hardcoded list)
- Category multi-select (6 values)
- Status selector: Resolved | Unresolved | All
- Apply / Reset buttons
- State: formData (SvelteKit form actions or fetch)

**CategoryHeatmap.svelte** (RF-002)
- Receives: `{categories: [{name, count, percentage, avgSeverity}]}`
- Renders: Horizontal bar chart (Sveltekit + native SVG or Chart.js)
- Hover: Shows absolute count + percentage
- Color: By severity (red=error, yellow=warning)

**TeamHeatmap.svelte** (RF-003)
- Receives: `{teams: [{name, count, topCategories}]}`
- Renders: Table or grid cards
- Each row: Team | Count | Top 3 categories (badges)
- Sortable by count

**PatternTimeline.svelte** (RF-004)
- Receives: `{timeline: [{week: Date, count, byCategory}]}`
- Renders: Line chart (6 lines, one per category)
- Tooltip on hover
- X-axis: Week labels
- Y-axis: Count

**RuleEffectiveness.svelte** (RF-005)
- Receives: `{rules: [{id, blocks_week, blocks_month, override_rate, status}]}`
- Renders: Table
- Columns: Rule ID | Blocks (Week) | Blocks (Month) | Override % | Status
- Status styling: Active (green), Deprecated (gray)
- Sortable by any column

#### State Management

**SvelteKit +page.ts**:
```typescript
export const load: PageLoad = async ({ fetch, url }) => {
  // Extract filters from URL params or use defaults
  const period = url.searchParams.get('period') ?? 'month';
  const team = url.searchParams.get('team') ?? null;
  const category = url.searchParams.get('category') ?? null;
  
  // Fetch all data server-side (SSR advantage)
  const [summary, byCategory, byTeam, timeline, rules] = await Promise.all([
    fetch('/api/v1/incidents/analytics/summary?...')
      .then(r => r.json()),
    // ... other fetches
  ]);
  
  return { summary, byCategory, byTeam, timeline, rules };
};
```

**Client State** (Svelte 5 runes):
```svelte
<script lang="ts">
  let { data } = $props();
  
  let period = $state<Period>(data.params.period);
  let selectedTeam = $state<string | null>(data.params.team);
  let selectedCategory = $state<string | null>(data.params.category);
  
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
@dataclass(frozen=True)
class CategoryStats:
    category: RootCauseCategory
    count: int
    percentage: float  # 0-100
    avg_severity: float  # 0-1 (error=1, warning=0.5)
    avg_resolution_days: float

@dataclass(frozen=True)
class TeamStats:
    team: str
    count: int
    top_categories: list[RootCauseCategory]
    avg_resolution_days: float

@dataclass(frozen=True)
class TimelinePoint:
    week: datetime
    count: int
    by_category: dict[RootCauseCategory, int]

@dataclass(frozen=True)
class RuleEffect:
    rule_id: str
    rule_version: str
    blocks_week: int
    blocks_month: int
    override_rate: float  # 0-1
    status: Literal["active", "deprecated"]

@dataclass(frozen=True)
class AnalyticsFilter:
    team: str | None = None
    category: RootCauseCategory | None = None
    status: Literal["resolved", "unresolved", "all"] = "all"

@dataclass(frozen=True)
class Period:
    value: Literal["week", "month", "quarter"] | "custom"
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

class CategoryStatsResponse(BaseModel):
    category: str
    count: int
    percentage: float
    avg_severity: float
    avg_resolution_days: float

class SummaryResponse(BaseModel):
    total: int
    resolved: int
    unresolved: int
    avg_resolution_days: float
```

---

## Testing Strategy

### Unit Tests (src → test coverage >80%)
- AnalyticsService._parse_period()
- Filter normalization
- Date arithmetic

### Integration Tests (SQL queries)
- get_by_category() with various periods + filters
- get_timeline() returns 12+ weeks of data
- Empty result handling (0 incidents)
- Deprecated rules excluded from effectiveness

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
- Client-side filtering (avoid re-fetch if possible)
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
| Deprecated rule confusion | Low | Mark visually (gray color) in UI |
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

