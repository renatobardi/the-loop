# Implementation Plan: Analytics Dashboard — Product Analytics Redesign

**Branch**: `019-product-analytics` | **Date**: 2026-04-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/019-product-analytics/spec.md`

---

## Summary

Transform `/analytics/` from a non-functional dashboard (3 components, 4 buggy endpoints) into a Product Analytics executive dashboard with real KPIs, in-memory 5-minute cache, multi-select filters, drill-down navigation, 2 new endpoints (severity-trend, top-rules), 2 new cards (rule effectiveness, severity trend chart), and 2 critical SQL bug fixes (QUERY_TIMELINE and QUERY_BY_TEAM ignoring team/category filters). Deliverable in 1 sprint (~14 days, 9 phases).

---

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5+ / Svelte 5 (frontend)  
**Primary Dependencies**:  
- Backend: FastAPI 0.104+, SQLAlchemy 2.0 async, Pydantic v2, PostgreSQL 16 + pgvector
- Frontend: SvelteKit 2, Svelte 5 runes, Tailwind CSS 4, Firebase SDK 11
  
**Storage**: PostgreSQL 16 (existing postmortems, incidents, rule_versions, scan_findings tables)  
**Testing**: pytest (unit + API), Vitest (frontend unit)  
**Target Platform**: Cloud Run (GCP) for backend, Browser (SPA) for frontend  
**Project Type**: Web service + web application (monorepo)  
**Performance Goals**: Dashboard loads <2s; filter apply <500ms; cache hit <50ms  
**Constraints**: 60 req/min rate limit on analytics endpoints; 5-minute cache TTL; no Redis  
**Scale/Scope**: Single-org analytics; support <1000 concurrent users; ~10k-100k incidents historical

---

## Constitution Check

**GATE: PASS** — No violations detected.

| Mandamento | Requirement | Status |
|-----------|-------------|--------|
| I. Trunk-Based Development | PRs only to main, never direct push | ✅ Compliant |
| II. Design System Immutable | Use lib/ui components + design tokens only | ✅ Compliant (update Badge with 'warning' variant in lib/ui) |
| III. Branch Taxonomy | Branch name = `019-product-analytics` (feat/ prefix deferred to commit message) | ✅ Compliant |
| IV. Main Protected | No changes required to main branch protections | ✅ Compliant |
| XIII. Mandamento XIII — All Dependencies in Execution Plan | All infra, APIs, DB, secrets, CI/CD deps must be explicit in tasks | ✅ Will be addressed in tasks.md (Phase 2) |

**Re-check post-Phase 1**: Confirm no new tech choices violate Constitution.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (monorepo — 2-app structure)

```text
apps/api/src/
├── api/routes/analytics.py                    # MODIFY: add 2 new route handlers
├── adapters/postgres/
│   ├── analytics_queries.py                   # MODIFY: fix 2 SQL bugs; add 2 new queries
│   ├── analytics_repository.py                # MODIFY: add 2 new methods
│   └── analytics_cache.py                     # CREATE: Cache class
├── domain/models.py                           # MODIFY: add 2 new models
├── domain/services.py                         # MODIFY: extend AnalyticsService
├── ports/analytics.py                         # MODIFY: add 2 port methods
├── api/models/analytics.py                    # MODIFY: add 2 response models
└── api/deps.py                                # MODIFY: inject cache

apps/web/src/lib/
├── ui/Badge.svelte                            # MODIFY: add 'warning' variant
├── components/analytics/
│   ├── DashboardGrid.svelte                   # MODIFY: render new cards
│   ├── SummaryCard.svelte                     # MODIFY: expand to 8 KPIs
│   ├── AnalyticsFilters.svelte                # MODIFY: multi-select + Button
│   ├── CategoryHeatmap.svelte                 # MODIFY: drill-down click
│   ├── TeamHeatmap.svelte                     # MODIFY: Badge + drill-down
│   ├── PatternTimeline.svelte                 # MODIFY: fix tooltip overflow
│   ├── MultiSelectDropdown.svelte             # CREATE: multi-select component
│   ├── RuleEffectivenessCard.svelte           # CREATE: top-5 rules card
│   └── SeverityTrendChart.svelte              # CREATE: stacked area chart
├── types/analytics.ts                         # MODIFY: update types
├── services/analytics.ts                      # MODIFY: new functions
└── app.css                                    # MODIFY: add 3 chart tokens

tests/
├── apps/api/tests/api/test_analytics_new_endpoints.py   # CREATE
└── apps/web/tests/unit/... # MODIFY existing analytics tests
```

**Structure Decision**: Existing monorepo (apps/api + apps/web) maintained. No new packages created.

## Implementation Phases

| # | Phase | Duration | Deliverables |
|---|-------|----------|--------------|
| 1 | Backend Bug Fixes | 2 days | Fix QUERY_TIMELINE + QUERY_BY_TEAM |
| 2 | New Endpoints | 3 days | severity-trend + top-rules endpoints |
| 3 | Caching | 1 day | In-memory TTL cache |
| 4 | Design System | 1 day | Badge variant + chart tokens |
| 5 | Summary KPIs | 1 day | 8-KPI card |
| 6 | Multi-Select + Drill-Down | 2 days | MultiSelectDropdown + navigation |
| 7 | Rule Effectiveness Card | 2 days | Top-5 rules card |
| 8 | Severity Trend Chart | 1 day | Stacked area + tooltip fix |
| 9 | Tests + Docs | 1 day | Full coverage + CLAUDE.md update |

**Total**: 14 days (1 sprint)

## Complexity Tracking

No Constitution violations. All principles followed:
- ✅ Trunk-based dev (PRs only)
- ✅ Design system compliance (lib/ui + tokens)
- ✅ Hexagonal architecture maintained
- ✅ Dependencies explicit (Mandamento XIII)

---

## Data Model Overview

### Entities

**Postmortem** (existing, no schema changes):
- `id` (UUID PK)
- `incident_id` (UUID FK, unique)
- `root_cause_category` (RootCauseCategory enum: code_pattern, infrastructure, process_breakdown, third_party, unknown)
- `team_responsible` (String, required)
- `severity_for_rule` (PostmortumSeverity enum: error, warning)
- `related_rule_id` (String nullable — rule effectiveness linking)
- `created_at`, `updated_at`, `is_locked`

**Incident** (existing, no schema changes):
- `id` (UUID PK)
- `resolved_at` (DateTime nullable — null = unresolved)
- `deleted_at` (DateTime nullable — soft delete)

**AnalyticsCache** (new, in-memory only):
- Key: `endpoint_name:sorted_filter_params` (String)
- Value: `tuple[data: Any, expires_at: datetime]`
- TTL: 5 minutes (300 seconds)

### New Domain Models

**SeverityTrendPoint**:
```
week: str (ISO date)
error_count: int
warning_count: int
```

**RuleEffectivenessStats**:
```
rule_id: str
incident_count: int
avg_severity: float (0.5–1.0)
```

---

## Execution Readiness

### Prerequisites

- ✅ Spec-008 (Postmortem workflow) — Schema complete
- ✅ Spec-013 (Root cause categories) — Domain model in place
- ✅ Spec-016 (Scan history) — Rule linking infrastructure exists
- ⚠️ Data quality — Many postmortems missing `root_cause_category` and `team_responsible` (out of scope, but will cause "No incidents" dashboard state in prod until populated)

### Local Development

**Backend**:
```bash
cd apps/api
export DATABASE_URL="postgresql+asyncpg://theloop:theloop@localhost:5432/theloop"
alembic upgrade head
pytest tests/ -v
uvicorn src.main:app --reload
```

**Frontend**:
```bash
cd apps/web
npm install
npm run dev  # localhost:5173
```

### Deployment

- GitHub Actions CI: ruff + mypy + pytest (≥80% coverage) + build + Trivy
- Cloud Run: `theloop-api` (backend) + `the-loop` (web)
- No additional infra (in-memory cache, no Redis)

---

## Known Constraints & Gotchas

1. **`from __future__ import annotations` + slowapi incompatibility** — Must be removed from analytics.py (route files only). Python 3.12 native union syntax `str | None` is sufficient.

2. **`ANY(:array)` with asyncpg** — SQL condition: `(:team_array IS NULL OR p.team_responsible = ANY(:team_array))`. Use `bindparam("team_array", type_=ARRAY(String()))` from `sqlalchemy.dialects.postgresql`.

3. **Cache key collisions with arrays** — Sort array before stringifying: `str(sorted(v))` to ensure `["a","b"]` and `["b","a"]` produce same cache key.

4. **SVG tooltip overflow on mobile** — Clamp positions within viewport: `Math.min(x + 12, viewport_width - tooltip_width)`.

5. **Stacked area SVG path construction** — ERROR area: 0 → error_count. WARNING area: error_count → error_count + warning_count (stacked on top).

---

## Next Steps

1. **Phase 0** — Resolve any NEEDS CLARIFICATION markers (none currently)
2. **Phase 1** — Generate `research.md`, `data-model.md`, `quickstart.md` (if needed)
3. **Phase 2** — Run `/speckit.tasks` to generate `tasks.md` with dependency-ordered execution checklist
4. **Implementation** — Execute tasks in order per `/speckit.implement`
