# Spec-013: Postmortem Workflow

**Status**: 📋 Ready for Planning  
**Timeline**: 1-2 weeks (9 intense days)  
**Total Tasks**: 62 across 6 phases  

---

## Vision

Transform incident response from **reactive** to **proactive**:

```
BEFORE (Spec-012):
Incident → 20 Semgrep rules block pattern → Future PRs safe ✓
But: Lost knowledge, no continuous improvement

AFTER (Spec-013):
Incident → User fills postmortem (root cause) → Dashboard shows patterns
→ Product prioritizes fixes → More rules → Better prevention ✓

The Loop closes: incident → knowledge → prevention → fewer incidents
```

---

## What's Implemented

### ✅ spec.md
- **6 functional requirements**: Postmortem form, templates, read-only, analytics foundation
- **4 user stories**: Describe how teams use postmortems
- **Success criteria**: Measurable acceptance conditions
- **Edge cases**: Error handling, validation

### ✅ plan.md
- **Domain model**: Postmortem, RootCauseCategory, PostmortumSeverity, RootCauseTemplate
- **Database**: PostgreSQL table with constraints, migration 008
- **Hexagonal architecture**: Domain → Ports → Adapters → API → Frontend
- **API contracts**: 5 endpoints (POST, GET, PUT, templates, summary)
- **Tech decisions**: Why hardcoded templates, why read-only, why async-ready

### ✅ tasks.md
- **62 tasks** across 6 sequential phases:
  - Phase 1: Domain + Database (T001-T010)
  - Phase 2: Repository + Service (T011-T025)
  - Phase 3: API Routes (T026-T045)
  - Phase 4: Incident Integration (T046-T050)
  - Phase 5: Frontend UI (T051-T062)
  - Phase 6: Testing + Docs (T063-T073)

- **Parallelization**: 30+ tasks marked [P] for parallel execution
- **Checkpoints**: Validation gates after each phase

### ✅ CLAUDE.md
- **Design patterns**: Hexagonal layers, repository, service, API
- **Code examples**: Full implementations for domain, API, frontend
- **Error handling**: Typed exceptions → HTTP status codes
- **Testing patterns**: Unit + API test examples
- **Common gotchas**: Unique constraint, enum storage, frozen models

---

## Key Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Postmortem | Obrigatório | Forces knowledge capture |
| Templates | Hardcoded (15) | MVP simplicity, no admin UI |
| Templates future | Dinâmico (Spec-015) | Allow customization later |
| Analytics | Globais + por-team | Both exec + team visibility |
| Webhooks | Assíncrono com retry | Reliable delivery, no blocking |
| Read-only | Após resolve | Audit trail, prevent retroactive changes |
| Unique constraint | 1 postmortem/incident | Clear relationship, no duplicates |

---

## Implementation Flow

### Phase 1-2: Domain + Repository (Days 1-3)
```
Pydantic models + Alembic migration → Database ready
```

### Phase 3: API (Days 4-5)
```
POST /postmortem, GET /postmortem, PUT /postmortem
GET /templates, GET /summary
```

### Phase 4: Incident Integration (Day 5)
```
Cannot resolve incident without postmortem
Postmortem locked after resolution
```

### Phase 5: Frontend (Days 6-7)
```
Form + template picker + validation + submit
Read-only view after resolution
```

### Phase 6: Testing + Docs (Days 8-9)
```
Coverage ≥80%, E2E tests, CLAUDE.md
```

---

## Ready for Implementation

All specs written. No planning needed — just execute tasks in order:

```bash
# Phase 1: Domain + Database
T001-T010: Models, migration, templates

# Phase 2: Repository + Service
T011-T025: CRUD, validation, tests

# Phase 3: API
T026-T045: 5 endpoints, error handling, tests

# Phase 4: Integration
T046-T050: Incident status enforcement

# Phase 5: Frontend
T051-T062: Form, templates, E2E tests

# Phase 6: Polish
T063-T073: Coverage, docs, merge
```

---

## What Comes After

### Spec-014: Analytics Dashboard
- Reads postmortem summaries from this spec
- Shows top patterns, team metrics, rule effectiveness
- Timeline of incidents

### Spec-015: Webhooks + Admin
- Send postmortem events to Slack, GitHub
- Allow custom templates (make hardcoded dynamic)
- Retry logic for async delivery

---

## References

- **spec.md**: Requirements, stories, AC
- **plan.md**: Architecture, decisions, patterns
- **tasks.md**: 62 task breakdown, checkpoints
- **CLAUDE.md**: Implementation examples, gotchas

---

**Next Step**: Ready to start Phase 1 (T001-T010)?
