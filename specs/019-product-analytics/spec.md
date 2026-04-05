# Feature Specification: Analytics Dashboard — Product Analytics Redesign

**Feature Branch**: `019-product-analytics`  
**Created**: 2026-04-05  
**Status**: Ready for Planning  
**Input**: Redesenhar completamente a página /analytics/ de um dashboard básico não-funcional em produção para um Product Analytics executivo com KPIs reais, cache de 5 minutos, filtros multi-select, drill-down interativo, novos endpoints severity-trend e top-rules, novo card de rule effectiveness com top-5 regras mais bloqueadas, novo chart de severity trend (stacked area), e correção de 2 bugs críticos de SQL.

---

## User Scenarios & Testing

### User Story 1 - PMO/Executive Views Real-Time Incident KPIs (Priority: P1)

A Product Manager or executive wants to access the analytics dashboard to see high-level metrics about incident patterns in the organization. They need to understand: total incidents in a period, how many are resolved vs. unresolved, average time to resolve, severity distribution, which teams have the most incidents, and which root cause categories are most common. This informs resource allocation decisions.

**Why this priority**: Core business need — executives need data-driven insights to prioritize engineering efforts. Without working KPIs, the dashboard is unusable.

**Independent Test**: Dashboard loads and displays all 8 KPIs (Total, Resolved, Unresolved, MTTR, ERROR count, WARNING count, Top Category, Most Affected Team) with real data within 2 seconds.

**Acceptance Scenarios**:

1. **Given** the user is authenticated and navigates to `/analytics/`, **When** the page loads with default period=month, **Then** all 8 KPI cards render with current month's data
2. **Given** 50+ incidents exist in the database, **When** the user views the dashboard, **Then** summary shows accurate total count and resolved/unresolved breakdown
3. **Given** incidents have varying severity_for_rule values, **When** the user views the dashboard, **Then** ERROR and WARNING counts are calculated correctly (ERROR = avg_severity ≥ 0.9, WARNING < 0.9)
4. **Given** the user changes the period filter from month to quarter, **When** filters are applied, **Then** all KPIs update to reflect the new period without page reload

---

### User Story 2 - Tech Lead Analyzes Patterns for Their Specific Team (Priority: P1)

A tech lead from a specific team (e.g., Backend) wants to drill into their team's incident patterns. They need to filter the dashboard to show only incidents attributed to their team, see which categories are most common in their team, and understand trends over time. This helps them identify systemic issues affecting their team specifically.

**Why this priority**: Core business need — teams must understand their own vulnerability patterns to improve. Multi-select and team filtering are prerequisites for this user story.

**Independent Test**: User can select multiple teams (or single team) from a multi-select dropdown, apply filters, and see dashboard update with data scoped to selected teams only. Drill-down on a category navigates to incidents list filtered by that category.

**Acceptance Scenarios**:

1. **Given** the team filter dropdown is open, **When** the user selects "Backend", **Then** the URL updates to `?team=Backend` and dashboard shows only incidents attributed to Backend team
2. **Given** multiple teams are available in the system, **When** the user selects "Backend" and "Frontend", **Then** the URL updates to `?team=Backend&team=Frontend` and dashboard shows combined incidents for both teams
3. **Given** the Category Heatmap is displayed, **When** the user clicks a category bar, **Then** the browser navigates to `/incidents/?category=code_pattern` with filtered incidents list
4. **Given** the Team Heatmap is displayed, **When** the user clicks a team row, **Then** the browser navigates to `/incidents/?team=Backend` with filtered incidents for that team

---

### User Story 3 - DevOps/SRE Tracks Severity Trends Over Time (Priority: P2)

A DevOps or SRE lead wants to see if the severity of incidents is improving or degrading over time. They need a trend chart showing weekly severity distribution (ERROR vs WARNING) over the past 12 months. This helps them assess whether recent changes/fixes are reducing critical-severity incidents.

**Why this priority**: Important for observability and trending — helps identify if improvement initiatives are working.

**Independent Test**: New Severity Trend Chart loads data from `/api/v1/incidents/analytics/severity-trend` endpoint and renders a stacked area chart showing ERROR and WARNING incident counts by week.

**Acceptance Scenarios**:

1. **Given** the user is on the analytics dashboard with default period=month, **When** the Severity Trend Chart loads, **Then** it displays weekly ERROR and WARNING counts as a stacked area chart
2. **Given** the user changes the period to quarter, **When** filters are applied, **Then** the Severity Trend Chart updates to show full quarter's data
3. **Given** the Severity Trend Chart is visible on a mobile device (375px width), **When** the user hovers over data points, **Then** the tooltip does not overflow the viewport

---

### User Story 4 - Security Lead Identifies Most-Blocked Rules (Priority: P2)

A Security lead wants to see which Semgrep rules have blocked the most incidents (rule effectiveness). They need to see the top-5 rules that prevented incidents from reaching production and understand which rules are the most effective.

**Why this priority**: Rule effectiveness is a key product differentiator.

**Independent Test**: New Rule Effectiveness Card loads data from `/api/v1/incidents/analytics/top-rules` endpoint and displays top-5 rules ranked by incident_count with severity badges.

**Acceptance Scenarios**:

1. **Given** postmortems have `related_rule_id` values populated, **When** the Rule Effectiveness Card loads, **Then** it displays top-5 rules by incident count with severity indicators
2. **Given** no postmortems have `related_rule_id` set, **When** the Rule Effectiveness Card loads, **Then** it shows empty state: "No rule-linked incidents yet. Link rules in postmortems."
3. **Given** the user filters by team=Backend, **When** the Rule Effectiveness Card updates, **Then** it shows top-5 rules for Backend incidents only

---

### Edge Cases

- What happens when zero incidents exist in the selected period? → Dashboard shows empty state: "No incidents in this period. Try expanding the selected period or removing active filters."
- What happens when a user applies filters that result in zero incidents? → All cards show 0 or N/A appropriately; no errors thrown.
- What happens when the analytics API is slow (>2s latency)? → Dashboard shows loading skeletons; user sees progress indication.
- What happens when a user applies multi-select filters and then resets? → All filter values cleared; dashboard reloads to default state.
- What happens when a user makes the same request twice within 5 minutes? → Second request returns cached data instantly; no database query.

---

## Requirements

### Functional Requirements

- **FR-001** (Bug Fix): System MUST fix QUERY_TIMELINE to apply `team` and `category` filters to the inner subquery (currently ignored)
- **FR-002** (Bug Fix): System MUST fix QUERY_BY_TEAM's inner `cat_count` subquery to apply `status`, `team`, and `category` filters
- **FR-003**: System MUST provide new `GET /api/v1/incidents/analytics/severity-trend` endpoint returning weekly ERROR vs WARNING incident counts
- **FR-004**: System MUST provide new `GET /api/v1/incidents/analytics/top-rules` endpoint returning top-10 rules by incident count with average severity
- **FR-005**: System MUST cache all analytics responses for 5 minutes; identical requests within 5-minute window must return cached data without database queries
- **FR-006**: System MUST support multi-select filters for `team` (checkbox dropdown) and `category` (checkbox dropdown); URL serialization as repeated params
- **FR-007**: System MUST implement drill-down navigation: clicking a category navigates to `/incidents/?category=X`; clicking a team navigates to `/incidents/?team=Y`
- **FR-008**: System MUST display 8 KPIs in summary card: Total Incidents, Resolved, Unresolved, Avg MTTR (days), ERROR count, WARNING count, Top Category, Most Affected Team
- **FR-009**: System MUST display new Severity Trend Chart (stacked area, SVG) showing weekly ERROR and WARNING distribution; responsive to all viewport widths
- **FR-010**: System MUST display new Rule Effectiveness Card with top-5 rules, rule ID in monospace, incident count, and severity badge (ERROR/WARNING); empty state when no rules linked
- **FR-011**: Filters MUST update URL without page reload; filter reset MUST clear all params and return to default state
- **FR-012**: Dashboard MUST load all data in parallel; user must see loading skeletons while data fetches

### Key Entities

- **Postmortem**: Has `root_cause_category`, `team_responsible`, `severity_for_rule`, `related_rule_id` (nullable), `created_at`; relates 1:1 to Incident
- **Incident**: Has `resolved_at` (null = unresolved), `deleted_at` (soft delete); relates 1:1 to Postmortem
- **Analytics Cache**: In-memory TTL dict; key = `endpoint_name:sorted_filter_params`; TTL = 5 minutes

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Dashboard page loads and renders all content within 2 seconds on standard broadband connection (>5 Mbps)
- **SC-002**: All 8 KPI tiles display accurate counts matching database state (verified via unit tests with fixtures)
- **SC-003**: Filter changes apply without page reload; URL updates and dashboard re-fetches data within 500ms
- **SC-004**: Multi-select filter combinations work correctly: selecting multiple teams shows union of data for all selected teams
- **SC-005**: Drill-down navigation from heatmaps works: clicking category navigates to `/incidents/?category=X`; clicking team navigates to `/incidents/?team=Y`
- **SC-006**: Cache reduces latency: second identical request within 5 minutes completes in <50ms (cache hit) vs. 500-2000ms (cache miss)
- **SC-007**: Severity Trend Chart renders correctly on all viewport sizes from 320px (mobile) to 1920px (desktop); tooltips never overflow
- **SC-008**: Rule Effectiveness Card displays correctly: with data shows top-5 rules; with no data shows empty state; with filters shows filtered results
- **SC-009**: All new endpoints require Firebase auth (return 401 if missing); rate limit 60 requests/minute
- **SC-010**: Specification has 0 [NEEDS CLARIFICATION] markers; ready for planning immediately

---

## Assumptions

- **Data integrity**: All incidents have at least one postmortem with `root_cause_category` and `team_responsible` populated (note: current data does not meet this; cleanup is out of scope)
- **Filtering semantics**: Multi-select uses AND logic within a field (category A OR B), AND across fields (category AND team AND period)
- **Caching strategy**: Cache is in-memory only (no Redis); invalidation is TTL-based (5 minutes); eventual consistency acceptable for analytics
- **MTTR definition**: MTTR = time from postmortem creation to incident resolution (not detection-to-resolution); known limitation not being changed
- **Rule linking**: `postmortem.related_rule_id` is nullable, populated manually by users; automated linking is out of scope
- **User access**: All authenticated Firebase users can access all analytics; no role-based filtering
- **Mobile support**: Dashboard is responsive (375px+) but full mobile optimization deferred to future phase

---

## Scope & Dependencies

### In Scope
- Fix 2 SQL query bugs (QUERY_TIMELINE, QUERY_BY_TEAM)
- Add 2 new API endpoints (severity-trend, top-rules)
- Implement in-memory cache (5-minute TTL)
- Redesign summary card with 8 KPIs
- Multi-select filters (team, category)
- Drill-down navigation
- Severity trend chart (stacked area, SVG)
- Rule effectiveness card
- Full test coverage
- Documentation updates

### Out of Scope
- Data cleanup (populating missing postmortem fields)
- Redis caching (in-memory only for v1)
- Real-time updates (WebSocket/polling deferred)
- Multi-organization isolation
- Advanced filtering (saved filters)
- Export/download analytics
- Automated rule linking
- Custom role-based access control

### Dependencies
- Existing schema (postmortems, incidents, rule_versions, scan_findings tables)
- Firebase JWT auth (Spec-007)
- Design system components (lib/ui)
- API infrastructure (hexagonal pattern + slowapi)
