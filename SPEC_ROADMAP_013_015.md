# The Loop: Spec-013 → 015 Roadmap

**Status**: Spec-012 ✅ Merged & Deployed (2026-04-03)  
**Next**: Spec-013 → 014 → 015 (4-5 weeks, Phase C.1-C.3)

---

## Executive Summary

Spec-012 (Phase B Semgrep API) closes the **prevention loop** — rules are versioned, dynamic, deployable via API.

Specs 013-015 close the **knowledge loop** — incidents → postmortems → analytics → more rules → fewer incidents.

```
┌─────────────────────────────────────────────────────────────────┐
│ INCIDENT                                                        │
│ - What happened?                                                │
│ - When? Impact?                                                 │
│ - Postmortem (WHY?) ← Spec-013                                 │
│ - Analytics dashboard ← Spec-014                               │
│ - Slack/GitHub notifications ← Spec-015                        │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │ POSTMORTEM WORKFLOW │
    │ - Root cause form   │
    │ - 15 templates      │
    │ - Read-only lock    │
    │ - Team assignment   │
    │ [Spec-013]          │
    └─────────┬───────────┘
              │
              ▼
    ┌─────────────────────┐
    │ ANALYTICS DASHBOARD │
    │ - Top patterns      │
    │ - Team heatmap      │
    │ - Rule effectiveness│
    │ - Timeline          │
    │ [Spec-014]          │
    └─────────┬───────────┘
              │
              ▼
    ┌─────────────────────┐
    │ WEBHOOK INTEGRATION │
    │ - Slack events      │
    │ - GitHub comments   │
    │ - Async delivery    │
    │ - Custom templates  │
    │ [Spec-015]          │
    └──────────┬──────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ PRODUCT OPTIMIZATION     │
    │ Insight-driven decisions │
    │ Data-driven rule updates │
    └──────────────────────────┘
```

---

## Spec-013: Postmortem Workflow

**Timeline**: 1-2 weeks | **Tasks**: 62 | **Phase**: C.1

### What It Does
- **Incident closes → Postmortem mandatory**: Why did it happen? What pattern?
- **15 templates**: Pre-filled forms (SQL injection, N+1 query, etc.)
- **Team tracking**: Which team caused/fixed incident?
- **Read-only after resolve**: Audit trail, no retroactive changes
- **Analytics foundation**: Data structured for Spec-014 queries

### Key Decisions
```
1. Postmortem obrigatório ← Enforce knowledge capture
2. Hardcoded templates (15) ← MVP: no admin UI yet
3. Dinâmico em Spec-015 ← Allow customization later
4. Globais + por-team ← Exec dashboard + team insights
5. Assíncrono com retry ← Webhooks (Spec-015)
```

### Deliverables
- Domain model + DB migration (Alembic 008)
- API: POST, GET, PUT postmortem + templates + summary
- Frontend: Form + template picker + read-only view
- Tests: 62 tasks → ≥80% coverage

### Success Metrics
- Every incident has postmortem
- Form completion <2 min (templates work)
- Ready for Spec-014 queries

---

## Spec-014: Incident Analytics

**Timeline**: 2 weeks | **Tasks**: 50-60 | **Phase**: C.2

### What It Does
- **Dashboard**: Top incident patterns (by frequency, severity)
- **Team heatmap**: Which team encounters which patterns?
- **Rule effectiveness**: How many PRs did rule X block?
- **Timeline**: When did pattern surge appear?
- **Data-driven decisions**: "SQL injection is 40% of incidents → prioritize rules"

### Dependencies
- Reads postmortem data from Spec-013 ✅
- Analyzes rule hits from Spec-012 API ✅

### Deliverables
- Analytics service (aggregation queries)
- API: GET /analytics/{patterns,teams,rules,timeline}
- Frontend dashboard (charts, filters)
- Tests: ≥80% coverage

### Success Metrics
- Dashboard loads <2s
- Accurate aggregations
- Team leads use for prioritization

---

## Spec-015: Webhooks + Admin

**Timeline**: 1 week | **Tasks**: 40-50 | **Phase**: C.3

### What It Does
- **Slack integration**: "New incident: SQL injection" → #incidents channel
- **GitHub integration**: PR comment when rule published
- **Dynamic templates**: Admin creates custom postmortem templates
- **Async delivery**: With retry logic (Bull queue or similar)

### Events
```
1. Incident.created
   → Slack: "Incident: SQL injection"
   
2. Postmortem.completed
   → Slack: "Root cause: N+1 query pattern"
   → GitHub: Comment on related PRs

3. RuleVersion.published (v0.2.1)
   → Slack: "New rule: path-traversal-002"
   → GitHub: "This PR would be blocked by new rule"
```

### Dependencies
- Spec-013 postmortem data ✅
- Spec-014 analytics context ✅

### Deliverables
- Webhook service + event system
- Slack formatter + GitHub API client
- Admin UI: Register/manage webhooks
- Retry logic with exponential backoff

### Success Metrics
- Slack messages arrive <5s
- GitHub comments helpful (link to incident)
- No lost events (async queue persists)

---

## Implementation Timeline

```
Week 1 (Apr 7-13):
  [Spec-013: Phase 1-3] Domain, API, Frontend basics

Week 2 (Apr 14-20):
  [Spec-013: Phase 4-6] Integration, testing, merge
  [Spec-014: Phase 1-2] Analytics queries, dashboard skeleton

Week 3 (Apr 21-27):
  [Spec-014: Phase 3-4] Dashboard UI, tests
  [Spec-015: Phase 1-2] Webhook service, Slack integration

Week 4 (Apr 28-May 4):
  [Spec-015: Phase 3-4] Admin UI, GitHub integration, tests
  Polish + docs + merge all

Timeline: 4 weeks (Spec-013 + 014 + 015)
```

---

## What Happens Next (Phase C.X)

### ❌ Redis Caching (Deferred)
- Reason: In-memory cache sufficient until 10+ replicas
- When: Needed if load requires it
- Decision: Revisit when telemetry shows cache miss rate >30%

### ❌ Admin Dashboard (Deferred to Spec-015)
- Rule management UI (create/publish/deprecate)
- Version history timeline
- Custom rule builder

### ❌ Advanced Workflow (Deferred to C.X)
- Version comparison API (`GET /compare?v1=x&v2=y`)
- Multi-region failover
- Custom rule templates (full editor)

---

## Success Criteria (All 3 Specs)

| Metric | Spec-013 | Spec-014 | Spec-015 |
|--------|----------|----------|----------|
| Coverage | ≥80% | ≥80% | ≥80% |
| Tests pass | ✅ | ✅ | ✅ |
| Ruff/mypy | 0 errors | 0 errors | 0 errors |
| Deployed | main | main | main |
| E2E working | ✅ | ✅ | ✅ |

---

## Decision Points

### Spec-013
- ✅ Postmortem obrigatório
- ✅ Templates hardcoded (15)
- ✅ Dinâmico em Spec-015
- ✅ Analytics: globais + por-team
- ✅ Async com retry (para Spec-015)

### Spec-014
- ⏳ Chart library (chart.js, D3, recharts)?
- ⏳ Real-time dashboard or hourly aggregations?
- ⏳ Export to CSV?

### Spec-015
- ⏳ Queue library (Bull, Celery, or custom)?
- ⏳ Webhook signature verification?
- ⏳ Rate limit webhooks?

---

## How to Execute

### Phase 1 (You are here)
- ✅ Spec-013 fully planned (spec.md, plan.md, tasks.md, CLAUDE.md)
- Ready to execute T001-T010 (Phase 1: Domain + Database)

### Next Steps
1. **Create feat/spec-013-postmortem branch**
2. **Execute Phase 1-2**: Domain + Repository (T001-T025)
3. **CI gates**: Ruff, mypy, pytest
4. **PR #56**: feat(spec-013): postmortem workflow phase 1-2
5. **Merge** → PR #57: phase 3-6
6. **Deploy** → Live

---

## References

- **Spec-013**: `/specs/013-postmortem-workflow/`
  - spec.md, plan.md, tasks.md, CLAUDE.md
- **Spec-012**: `/specs/012-phase-b-workflow-integration/`
  - Phase B API (live, 20 rules, versioning)
- **Roadmap**: `/_deepwiki/the-loop/ROADMAP.md`
  - Full product roadmap (Phase 0-E)

---

**Ready to start Spec-013?**

```bash
git checkout -b feat/spec-013-postmortem

# Phase 1: Domain + Database (T001-T010)
# - Create Pydantic models
# - Create Alembic migration 008
# - Run locally + test

# Phase 2: Repository + Service (T011-T025)
# - Implement CRUD
# - Unit tests

# ... [continue with phases 3-6]

# Merge when complete
```

**Status**: 📋 Ready for implementation — no blockers, all decisions made.

