# Implementation Plan: Analytics Dashboard — Product Analytics Redesign

**Branch**: `019-product-analytics` | **Date**: 2026-04-05 | **Spec**: [spec.md](./spec.md)

---

## Summary

Transform `/analytics/` from a non-functional dashboard (3 components, 4 buggy endpoints) into a Product Analytics executive dashboard with real KPIs, in-memory 5-minute cache, multi-select filters, drill-down navigation, 2 new endpoints (severity-trend, top-rules), 2 new cards (rule effectiveness, severity trend chart), and 2 critical SQL bug fixes (QUERY_TIMELINE and QUERY_BY_TEAM ignoring team/category filters). Deliverable in 1 sprint (~14 days, 7 implementation phases).

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
| III. Branch Taxonomy | Branch name = `019-product-analytics` | ✅ Compliant |
| IV. Main Protected | No changes required to main branch protections | ✅ Compliant |
| XIII. Mandamento XIII — All Dependencies Explicit | All infra, APIs, DB, secrets, CI/CD deps must be explicit | ✅ Documented in Dependencies section |

**Re-check post-Phase 1**: Confirm no new tech choices violate Constitution.

---

## Implementation Phases

**Note**: tasks.md organizes work by 7 story-based phases (Phase 0–6) for execution sequencing. This plan uses 7 technical phases aligned with implementation order.

| Phase | Focus | Days | Story Dependencies |
|-------|-------|------|-------------------|
| 0 | Setup & Documentation | 1 | None |
| 1 | Foundational (SQL bugs, cache, design system) | 2 | Blocks all stories |
| 2 | US1: KPIs (8 cards, 2 endpoints) | 3 | Foundation complete |
| 3 | US2: Multi-Select Filters & Drill-Down | 2 | Phase 2 complete |
| 4 | US3: Severity Trend Chart | 1 | Phase 2 complete |
| 5 | US4: Rule Effectiveness Card | 1 | Phase 2 complete |
| 6 | Polish, Testing, Documentation | 2 | All phases complete |

**Total**: ~14 days | 7 phases | 1 sprint

---

## Critical Files to Modify

### Backend (9 new/modified files)

| File | Changes |
|------|---------|
| `apps/api/src/adapters/postgres/analytics_queries.py` | Fix QUERY_TIMELINE (add team/category filters); fix QUERY_BY_TEAM (add status/team/category); add QUERY_SEVERITY_TREND, QUERY_TOP_RULES |
| `apps/api/src/domain/models.py` | Add SeverityTrendPoint, RuleEffectivenessStats; update AnalyticsFilter |
| `apps/api/src/adapters/postgres/analytics_repository.py` | Update _build_params for array handling; add get_severity_trend(), get_top_rules() |
| `apps/api/src/ports/analytics.py` | Add get_severity_trend, get_top_rules to Protocol |
| `apps/api/src/domain/services.py` | Inject AnalyticsCache; wrap all 6 methods; add new service methods |
| `apps/api/src/api/models/analytics.py` | Add SeverityTrendResponse, RuleEffectivenessResponse |
| `apps/api/src/api/routes/analytics.py` | Remove `from __future__ import annotations`; add 2 new route handlers |
| `apps/api/src/api/deps.py` | Add AnalyticsCache singleton, init/get functions |
| `apps/api/src/adapters/postgres/analytics_cache.py` | NEW: AnalyticsCache class (5-min TTL, sorted key serialization) |

### Frontend (13 new/modified files)

| File | Changes |
|------|---------|
| `apps/web/src/lib/ui/Badge.svelte` | Add 'warning' variant |
| `apps/web/src/app.css` | Add 3 chart color tokens |
| `apps/web/src/lib/types/analytics.ts` | Add SeverityTrendPoint, RuleEffectiveness types |
| `apps/web/src/lib/services/analytics.ts` | Add getAnalyticsSeverityTrend(), getAnalyticsTopRules() |
| `apps/web/src/routes/analytics/+page.ts` | Use getAll() for multi-select; add new endpoints |
| `apps/web/src/routes/analytics/+page.svelte` | Update handleFiltersChange for array params |
| `apps/web/src/lib/components/analytics/DashboardGrid.svelte` | Add new component props, render new cards |
| `apps/web/src/lib/components/analytics/SummaryCard.svelte` | Redesign: 8 KPIs in 2×4 grid |
| `apps/web/src/lib/components/analytics/AnalyticsFilters.svelte` | Replace single-select with MultiSelectDropdown; add Reset button |
| `apps/web/src/lib/components/analytics/TeamHeatmap.svelte` | Replace spans with Badge; add drill-down onclick |
| `apps/web/src/lib/components/analytics/CategoryHeatmap.svelte` | Add drill-down onclick; import goto |
| `apps/web/src/lib/components/analytics/PatternTimeline.svelte` | Fix tooltip clamping |
| `apps/web/src/lib/components/analytics/MultiSelectDropdown.svelte` | NEW: Multi-select component |
| `apps/web/src/lib/components/analytics/RuleEffectivenessCard.svelte` | NEW: Top-5 rules card |
| `apps/web/src/lib/components/analytics/SeverityTrendChart.svelte` | NEW: Stacked area SVG chart |

### Testing (2 files)

| File | Changes |
|------|---------|
| `apps/api/tests/api/test_analytics.py` | Add bug fix tests (QUERY_TIMELINE, QUERY_BY_TEAM) |
| `apps/api/tests/api/test_analytics_new_endpoints.py` | NEW: Tests for severity-trend, top-rules, cache TTL |

---

## Dependencies

**Database**: PostgreSQL 16 + pgvector + pg_trgm (existing)  
**APIs**: None (internal endpoints only)  
**Secrets**: None (no new secrets)  
**CI/CD**: Existing GitHub Actions (no changes)  
**Cloud Services**: Existing Cloud Run (no new services)

---

## Key Gotchas

1. **`from __future__ import annotations` incompatibility**: Breaks slowapi rate limiting. Remove from analytics.py line 3.
2. **`ANY(:array)` with asyncpg**: Use `bindparam("team_array", type_=ARRAY(String()))` + `(:team_array IS NULL OR p.team_responsible = ANY(:team_array))`.
3. **Cache key consistency**: Sort arrays before converting to string: `sorted(team_array)` to ensure `["a","b"]` and `["b","a"]` produce same key.
4. **Button padding**: Filter bar buttons override `px-6 py-3` with `class="px-3 py-1.5 text-sm"`.
5. **Stacked area SVG**: ERROR area (bottom=0, top=error_count), WARNING area (bottom=error_count, top=error_count+warning_count). Render ERROR first.
6. **Multi-select URL**: `params.append()` serializes as repeated params (`?team=a&team=b`), not comma-separated.
7. **Tooltip overflow**: Clamp both X and Y positions to prevent viewport overflow on small screens.

---

## Risk Mitigation

| Risk | Severity | Mitigation |
|------|----------|-----------|
| SQL fixes break existing queries | High | Comprehensive unit/API tests; test both buggy & fixed paths |
| Cache causes stale data | Medium | 5-minute TTL acceptable for analytics; manual clear future feature |
| Multi-select URL state lost | Low | URL is canonical; filters reconstructed from params |
| SVG charts don't render | Low | Standard SVG APIs; all browsers supported |
| AnalyticsCache memory leak | Medium | TTL dict auto-evicts expired entries; monitor Cloud Run logs |

---

## Success Criteria (Phase Gates)

- [x] Constitution: All 5 Mandamentos satisfied
- [x] Requirements: All 11 FRs and 11 SCs defined
- [x] Task Coverage: All 22 FRs/SCs mapped to 53 tasks
- [x] Task Format: All tasks follow checklist format (53 tasks T001–T053)
- [x] Dependencies: Phase blocking documented (Phase 1 blocks all stories)
- [x] Parallelization: 20 tasks marked [P] for concurrent execution
- [ ] Phase 0–6 Completion: All phases complete <14 days
- [ ] Production Deployment: `/analytics/` loads <2s in Cloud Run
- [ ] Test Coverage: Backend ≥80%, Frontend ≥70%
