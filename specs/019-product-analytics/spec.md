# Feature Specification: Analytics Dashboard — Product Analytics Redesign

**Feature Branch**: `019-product-analytics`  
**Created**: 2026-04-05  
**Status**: Ready for Implementation  
**Input**: Redesenhar completamente a página /analytics/ de um dashboard básico não-funcional em produção para um Product Analytics executivo com KPIs reais, cache de 5 minutos, filtros multi-select, drill-down interativo, novos endpoints severity-trend e top-rules, novo card de rule effectiveness com top-5 regras mais bloqueadas, novo chart de severity trend (stacked area), e correção de 2 bugs críticos de SQL.

---

## Context

The Loop's analytics dashboard at `/analytics/` was implemented in Phase C.2 (Spec-014) with 5 basic components and 4 endpoints but is **non-functional in production** because:

1. **No root_cause_category data**: Most incidents lack postmortem root cause categorization, so the dashboard displays "No incidents in this period" constantly
2. **SQL bugs**: QUERY_TIMELINE ignores team/category filters; QUERY_BY_TEAM inner subquery omits status/team/category filters
3. **No KPIs**: Missing high-level business metrics (total, resolved, unresolved, MTTR, severity counts)
4. **Single-select filters**: Users cannot drill into multiple teams or categories simultaneously
5. **No drill-down**: Clicking a category/team doesn't navigate to the filtered incidents list

This spec transforms the dashboard into a **Product Analytics executive tool** with real, actionable KPIs, a 5-minute cache, multi-select filters, drill-down navigation, 2 new endpoints (severity-trend, top-rules), 2 new cards (rule effectiveness heatmap, severity trend chart), and fixes for both SQL bugs. Target: 1 sprint (~14 days).

**Target Users**:
- Product Managers/Executives: Need KPI dashboards to prioritize engineering efforts
- Tech Leads: Need team-specific incident analysis and pattern identification
- DevOps/SRE: Need severity trends over time to assess improvement initiatives
- Security Teams: Need rule effectiveness metrics to validate/tune security rules

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

**Independent Test**: Dashboard displays a stacked area chart with ERROR and WARNING incident counts by week. Chart renders within 1 second; tooltip shows exact counts on hover without overflowing viewport.

**Acceptance Scenarios**:

1. **Given** the dashboard is loaded with default period, **When** the user scrolls to the Severity Trend Chart, **Then** a stacked area chart displays weekly ERROR/WARNING counts
2. **Given** incidents span multiple months, **When** the user views the chart, **Then** the chart correctly stacks ERROR (bottom) and WARNING (top) areas
3. **Given** the user hovers over a data point, **When** the tooltip appears, **Then** it shows the exact week and error/warning counts without overflowing the viewport boundaries

---

### User Story 4 - Security Lead Validates Rule Effectiveness (Priority: P2)

A Security Lead wants to understand which rules are most effective at catching incidents. They need a card showing the top 5 rules by incident count, with severity badges and a CTA to refine rule tuning. This validates that deployed rules are catching real-world patterns.

**Why this priority**: Useful for rule optimization but not critical to core analytics workflow. Depends on P1 stories completing first.

**Independent Test**: Rule Effectiveness Card displays top 5 rules by incident count, with incident count and average severity badge (ERROR/WARNING). Card updates when dashboard filters change.

**Acceptance Scenarios**:

1. **Given** the Rule Effectiveness Card is rendered, **When** the page loads, **Then** the card displays the 5 most common rules (by incident_count) with counts and severity badges
2. **Given** the user applies team/category filters, **When** filters are applied, **Then** the Rule Effectiveness Card updates to show rules filtered by the applied scope

---

## Functional Requirements

- **FR-001**: System MUST fix QUERY_TIMELINE to apply team and category filters via `ANY(:team_array)` and `ANY(:category_array)` PostgreSQL operators
- **FR-002**: System MUST fix QUERY_BY_TEAM inner subquery to apply status, team, and category filters
- **FR-003**: System MUST implement in-memory cache with 5-minute TTL for all 6 analytics endpoints (summary, category, team, timeline, severity-trend, top-rules)
- **FR-004**: System MUST add 2 new endpoints: `GET /api/v1/incidents/analytics/severity-trend` and `GET /api/v1/incidents/analytics/top-rules`
- **FR-005**: System MUST support multi-select filters via repeated URL parameters (e.g., `?team=Backend&team=Frontend&category=code_pattern`)
- **FR-006**: System MUST calculate and display 8 KPIs: Total, Resolved, Unresolved, Avg MTTR, ERROR count, WARNING count, Top Category, Most Affected Team
- **FR-007**: System MUST render SummaryCard with 2 rows × 4 columns KPI layout
- **FR-008**: System MUST render RuleEffectivenessCard showing top 5 rules by incident count with severity badges
- **FR-009**: System MUST render SeverityTrendChart as stacked area SVG (ERROR + WARNING) with clamped tooltip
- **FR-010**: System MUST support drill-down navigation: clicking category/team navigates to `/incidents/?category=X` or `/incidents/?team=Y`
- **FR-011**: System MUST update design system: add Badge variant `'warning'` and 3 chart color tokens (`--color-chart-green`, `--color-chart-amber`, `--color-chart-teal`)

---

## Success Criteria

- **SC-001**: All 8 KPIs display correctly with real incident data within 2 seconds of page load
- **SC-002**: Multi-select filters work: user selects multiple teams/categories, URL updates, dashboard re-renders with filtered data within 500ms
- **SC-003**: Drill-down works: user clicks category/team pill, navigates to `/incidents/?category=X` with correct filtered list
- **SC-004**: SQL bug fixes pass: `pytest tests/api/test_analytics.py -v` shows both QUERY_TIMELINE and QUERY_BY_TEAM tests passing
- **SC-005**: Cache works: second request to same endpoint within 5 minutes returns <50ms (no new database query in logs)
- **SC-006**: Cache expires: sixth request after >5 minutes shows new database query in logs
- **SC-007**: RuleEffectivenessCard renders top 5 rules with incident counts and severity badges
- **SC-008**: SeverityTrendChart renders stacked area without overlapping or overflowing tooltips
- **SC-009**: Backend: mypy strict + ruff check pass; Frontend: TypeScript strict + ESLint pass
- **SC-010**: Coverage: backend tests ≥80%, frontend tests ≥70%
- **SC-011**: Responsive: dashboard usable on 375px viewport (mobile-first)

---

## Key Entities

- **Postmortem**: Captured root cause category for an incident (nullable, populated during postmortem phase)
- **Incident**: Core entity with team_responsible, status, created_at, resolved_at
- **AnalyticsCache**: In-memory dict storing endpoint responses with TTL 5 minutes, keyed by (endpoint, sorted_params_tuple)
- **SeverityTrendPoint**: Weekly aggregation of ERROR/WARNING counts
- **RuleEffectiveness**: Rule ID + incident count + average severity

---

## Assumptions

- Incidents have postmortems with root_cause_category populated (may require data backfill for existing incidents)
- Teams are managed and consistent across incidents (no team name normalization needed)
- Dashboard is accessed by authenticated users only (no public analytics)
- Cache TTL of 5 minutes is acceptable for executive dashboard (not real-time)
- PostgreSQL `ANY(:array)` operator is available (standard in PG 9.1+)
- SVG rendering is acceptable for charts (no external charting library required)
- Rule whitelist filtering from Spec-016 does not apply to analytics endpoints (executives see all rules by default)

---

## Out of Scope

- ❌ Real-time analytics (WebSocket subscriptions)
- ❌ PDF/CSV export of dashboard
- ❌ Custom dashboard layouts or widget positioning
- ❌ Role-based access control (all authenticated users see same dashboard)
- ❌ Historical data backfill for incidents without root_cause_category
- ❌ Redis caching (MVP uses in-memory TTL dict)

---

## Edge Cases

- **E-001**: Dashboard loads with no incidents in period → display "No incidents in this period" with empty KPI cards (zeros)
- **E-002**: User applies filters that match zero incidents → show "No incidents matching filters" + reset link
- **E-003**: Cache expires mid-request → new query runs; user sees updated data (transparent)
- **E-004**: SVG tooltip positioned near viewport edge → clamp to viewport bounds (no overflow)
- **E-005**: User selects multiple teams but filter returns zero results → show empty state with available teams as pills

---
