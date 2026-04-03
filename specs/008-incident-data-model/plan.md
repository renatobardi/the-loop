# Implementation Plan: Incident Data Model — Production-Ready Schema

**Branches**: 5 separate `feat/` branches (Phases 1–2 are sequential; Phases 3–10 can overlap once Phase 2 completes)  
**Date**: 2026-04-01 | **Spec**: [spec.md](spec.md)

| Branch | Scope | Tasks | Execution |
|---|---|---|---|
| `feat/incident-data-model-schema-phase-1` | Enums + all migrations + backfill | T001–T008 | Sequential (Phase 1) |
| `feat/incident-data-model-schema-phase-2` | Extended Incident: US1 constraints, US2 MTTR, US3 postmortem, US8 JSONB | T009–T032, T080 | Sequential (Phase 2) |
| `feat/incident-data-model-schema-phase-3` | Timeline events full stack | T033–T042 | Can overlap with Phase 4–5 after Phase 2 |
| `feat/incident-data-model-schema-phase-4` | Responders + Action items | T043–T062 | Can overlap with Phase 3, 5 after Phase 2 |
| `feat/incident-data-model-schema-phase-5` | Attachments + Polish + Deploy | T063–T079 | Can overlap with Phase 3–4 after Phase 2 |

## Summary

Extend the incident registry with precise operational timestamps (enabling MTTR/MTTD calculation), postmortem lifecycle tracking, rich JSONB content for RAG quality, and four new related tables (timeline events, responders, action items, attachments). All changes are backward-compatible. Implemented as 5 sequential Alembic migrations + domain/ORM/API/test layers following the existing hexagonal architecture.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic, pgvector  
**Storage**: PostgreSQL 16 + pgvector (Cloud SQL `theloopoute:southamerica-east1:theloop-db`)  
**Testing**: pytest, real PostgreSQL (no mocks for DB layer)  
**Target Platform**: GCP Cloud Run (`theloop-api`)  
**Performance Goals**: existing 60 req/min rate limit preserved on all new endpoints  
**Constraints**: zero breaking changes to existing API consumers; `main` = production  
**Scale/Scope**: single-tenant; extends 1 existing table, adds 4 new tables; 5 migrations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Mandamento | Gate | Status | Notes |
|---|---|---|---|
| I. Trunk-Based | All code via PR on `008-incident-data-model` → `main` | ✅ PASS | Spec branch is correct entry point |
| III. Branch Taxonomy | Spec branch uses `NNN-name` convention per CLAUDE.md | ✅ PASS | Accepted speckit convention |
| VI. No Dev Environment | Migrations run against production Cloud SQL on deploy | ✅ PASS | `alembic upgrade head` before Cloud Run restart |
| VII. CI Gates | ruff + mypy strict + pytest (≥80% coverage) + Docker + Trivy | ✅ PASS | All existing gates must still pass |
| IX. Clean Code | Each migration file has one responsibility; services are lean | ✅ PASS | Plan enforces single-responsibility per file |
| X. Hexagonal Architecture | New entities follow domain → port → adapter → API pattern | ✅ PASS | 4 new domain models, 4 new ports, 4 new adapters |
| XII. Docs | `apps/api/src/api/routes/` has new router files; `main.py` updated | ✅ PASS | Doc updates included in implementation tasks |
| XIII. Dependencies | Migrations listed BEFORE service/API tasks; deploy order explicit | ✅ PASS | See execution order in tasks — infra first |

**Post-design re-check** (after Phase 1):

| Decision | Mandamento Satisfied |
|---|---|
| No `tenant_id` (not in current schema) | X — no speculative interfaces |
| No FK to `users` table (Firebase auth) | X — no speculative interfaces |
| Separate port per new entity | X — real boundary: different lifecycle, test isolation |
| `type_=None` migration skipped (bugs not present) | IX — no unnecessary code |

## Project Structure

### Documentation (this feature)

```text
specs/008-incident-data-model/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/
│   └── api.md           ← Phase 1 output
└── tasks.md             ← Phase 2 output (/speckit.tasks)
```

### Source Code Layout

```text
apps/api/
├── alembic/
│   └── versions/
│       ├── 001_create_incidents_table.py           (existing)
│       ├── 002_add_operational_timestamps.py       (new)
│       ├── 003_add_jsonb_fields.py                 (new)
│       ├── 004_add_incident_timeline_events.py     (new)
│       ├── 005_add_incident_responders_actions.py  (new)
│       └── 006_add_incident_attachments.py         (new)
│
├── scripts/
│   ├── seed.py                                     (existing)
│   └── backfill_started_at.py                      (new)
│
└── src/
    ├── domain/
    │   ├── models.py       ← extend Incident + add 4 new models + new enums
    │   ├── services.py     ← extend IncidentService + add 4 new service classes
    │   └── exceptions.py   ← add new exceptions (DuplicateResponderError, etc.)
    │
    ├── ports/
    │   ├── incident_repo.py             (existing — no changes needed)
    │   ├── timeline_event_repo.py       (new)
    │   ├── responder_repo.py            (new)
    │   ├── action_item_repo.py          (new)
    │   └── attachment_repo.py           (new)
    │
    ├── adapters/
    │   └── postgres/
    │       ├── models.py       ← extend IncidentRow + add 4 new *Row classes
    │       └── repository.py   ← existing IncidentRepository unchanged
    │           timeline_event_repository.py  (new)
    │           responder_repository.py       (new)
    │           action_item_repository.py     (new)
    │           attachment_repository.py      (new)
    │
    └── api/
        ├── deps.py         ← add get_* dependency factories for new services
        └── routes/
            ├── incidents.py     ← update request/response schemas + new fields
            ├── timeline.py      (new)
            ├── responders.py    (new)
            ├── action_items.py  (new)
            └── attachments.py   (new)
```

**Structure Decision**: Single `apps/api/` project. New entities each get dedicated files for port, adapter, and route — consistent with hexagonal pattern. All domain enums and models in `domain/models.py` to avoid circular imports.

## Complexity Tracking

| Decision | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Separate port per new entity | Different query patterns (chronological ordering for timeline, UNIQUE constraint for responders, status filtering for action items) and independent test isolation | Single god-port would require test doubles for all 5 entities in every test; violates SRP |
| 5 separate migrations (002–006) | Each can be rolled back independently; reduces blast radius per deploy | Single mega-migration would be unrollbackable in production if any step fails mid-run |
| `backfill_started_at.py` as standalone script | Backfill runs exactly once per environment, separately from schema changes | Running inside migration is dangerous: if backfill fails, entire migration rolls back including the DDL; standalone script is idempotent and retryable |

## Execution Order (Mandamento XIII)

**Phase A — Database** (must precede all other phases):
1. Migration `002`: Add operational timestamps + fields to `incidents`
2. Run `backfill_started_at.py` in production (populate `started_at` from `date`)
3. Migration `003`: Add JSONB fields to `incidents`
4. Migration `004`: Create `incident_timeline_events` table
5. Migration `005`: Create `incident_responders` + `incident_action_items` tables
6. Migration `006`: Create `incident_attachments` table

**Phase B — Domain + Ports** (after all migrations):
7. Update `domain/models.py`: add new enums, extend `Incident`, add 4 new domain models
8. Update `domain/exceptions.py`: add `DuplicateResponderError`, `ActionItemNotFoundError`, `TimelineEventNotFoundError`, `AttachmentNotFoundError`
9. Update `domain/services.py`: extend `IncidentService` for new fields; add `TimelineEventService`, `ResponderService`, `ActionItemService`, `AttachmentService`
10. Create ports: `ports/timeline_event_repo.py`, `ports/responder_repo.py`, `ports/action_item_repo.py`, `ports/attachment_repo.py`

**Phase C — Adapters** (after ports):
11. Update `adapters/postgres/models.py`: extend `IncidentRow` + add 4 new `*Row` classes
12. Create adapters: `adapters/postgres/timeline_event_repository.py`, `responder_repository.py`, `action_item_repository.py`, `attachment_repository.py`

**Phase D — API** (after adapters):
13. Update `api/deps.py`: add dependency factories for 4 new services
14. Update `api/routes/incidents.py`: add new fields to request/response schemas
15. Create routes: `api/routes/timeline.py`, `api/routes/responders.py`, `api/routes/action_items.py`, `api/routes/attachments.py`
16. Update `main.py`: register 4 new routers

**Phase E — Tests** (alongside Phase B–D):
17. Unit tests: domain model validation, computed properties, new enum values
18. API tests: all new endpoints (CRUD + error cases for each entity)
19. Migration test: verify schema after all migrations applied

**Phase F — CI/Deploy**:
20. Verify `ruff check`, `ruff format`, `mypy --strict` pass
21. Verify `pytest --cov=src` with coverage ≥ 80%
22. PR → review → merge → production deploy via GitHub Actions
23. Run `alembic upgrade head` on Cloud SQL **before** Cloud Run restart
24. Run `backfill_started_at.py` on Cloud SQL if production has existing incidents with `date != NULL`
