# Research: Incident Data Model — Production-Ready Schema

**Feature**: 008-incident-data-model  
**Date**: 2026-04-01

---

## Finding 1: `type_=None` bugs do NOT exist in the current codebase

**Decision**: No "fix" migration is needed for existing schema bugs. Create all new tables correctly from the start.

**Rationale**: The spec's bug list (`type_=None` in `semgrep_rule`, `scan`, `advisory`, `synthesis_candidate`, `tenant`) refers to tables that **do not yet exist** in this project. The only existing table is `incidents` (migration `001`), which already has correct SQLAlchemy types throughout (`Boolean NOT NULL DEFAULT false`, `DateTime(timezone=True)`, etc.). Migration `002` will be the first operational timestamp addition to the existing `incidents` table.

**Alternatives considered**: Create a `002_fix_type_none.py` migration as originally specified — rejected because there is nothing to fix; all future tables will be created correctly by design.

---

## Finding 2: Directory structure is `apps/api/`, not `packages/`

**Decision**: All new files follow the existing `apps/api/src/` layout. No `packages/` monorepo structure exists.

**Rationale**: The spec was informed by an analysis of a different project (Oute Muscle). The Loop uses a two-app monorepo (`apps/web/`, `apps/api/`). The correct paths are:
- Migrations: `apps/api/alembic/versions/`
- Domain models: `apps/api/src/domain/models.py`
- ORM models: `apps/api/src/adapters/postgres/models.py`
- Enums: stay in `apps/api/src/domain/models.py` (no separate enums package)
- Scripts: `apps/api/scripts/` (new directory)

**Alternatives considered**: Create `packages/` structure as spec suggested — rejected as it would contradict the existing project layout and introduce unnecessary restructuring scope.

---

## Finding 3: Multi-tenancy is out of scope for all new tables

**Decision**: New tables (`incident_timeline_events`, `incident_responders`, `incident_action_items`, `incident_attachments`) do NOT include a `tenant_id` column.

**Rationale**: The existing `incidents` table has no `tenant_id`. The platform is currently single-tenant (one authenticated user, @renatobardi). Adding `tenant_id` now would be a speculative abstraction with no FK target (no `tenants` table exists). Adding it to new tables but not to `incidents` would create an inconsistent schema.

**Alternatives considered**: Add `tenant_id` to all new tables as specified — rejected because it creates FK-less columns, breaks schema consistency with the parent `incidents` table, and violates Mandamento X (no speculative interfaces).

---

## Finding 4: User references are Firebase UUIDs — no FK constraint

**Decision**: All "user reference" fields (`recorded_by`, `incident_lead_id`, `owner_id`, `uploaded_by`, `completed_by`, `user_id` in responders) are stored as `UUID` columns **without FK constraints** to a users table.

**Rationale**: Authentication is provided by Firebase Auth. There is no `users` table in PostgreSQL — user identity lives in Firebase. The existing pattern (`created_by UUID NOT NULL` in `incidents`) confirms this convention. FK constraints to a non-existent table would break migrations.

**Alternatives considered**: Create a `users` table as FK target — rejected as out of scope; user management is Firebase's responsibility.

---

## Finding 5: New domain entities follow the existing hexagonal pattern

**Decision**: Each new entity gets: a Pydantic domain model (frozen, `domain/models.py`) → a Protocol port (`ports/`) → a PostgreSQL adapter (`adapters/postgres/`) → a FastAPI route file (`api/routes/`). New service classes in `domain/services.py`.

**Rationale**: The existing `Incident` architecture provides a proven, consistent template. Diverging from it would violate Clean Code (Mandamento IX) and Hexagonal Architecture (Mandamento X). All four new entities are genuine domain boundaries: they have their own lifecycle, validation rules, and query patterns.

**Alternatives considered**: Fold new entities into `IncidentService` with direct DB access — rejected because it would create a god-service and make testing significantly harder (existing tests mock at the service boundary).

---

## Finding 6: Alembic revision chain starts from `001`

**Decision**: New migrations use revision IDs `002` through `006` with `down_revision` chaining. All implement `upgrade()` and `downgrade()`.

**Migration sequence**:
```
001 (exists) → 002 (operational timestamps) → 003 (JSONB fields) 
→ 004 (timeline_events table) → 005 (responders + action_items tables) 
→ 006 (attachments table)
```

**Rationale**: The spec originally proposed 7 migrations (001–007) but since migration 002 (`fix_type_none`) is not needed, we collapse to 5 new migrations (002–006). The operational timestamps and JSONB fields are kept separate (002 and 003) to allow independent rollback.

---

## Finding 7: `from __future__ import annotations` + slowapi incompatibility

**Decision**: New route files use `from __future__ import annotations` (consistent with all existing source files). Rate limiting with `@limiter.limit()` is applied to all new endpoints, matching the existing pattern.

**Rationale**: All existing `src/` files use `from __future__ import annotations`. The slowapi rate limiter is already configured via `middleware.py`. The incompatibility between slowapi and `from __future__ import annotations` in `@limiter.limit` decorator arguments is a known issue that is already worked around in the codebase by importing `from __future__ import annotations` at the top (the decorator string args are not affected).

---

## Finding 8: `Incident` domain model uses `ConfigDict(frozen=True)` — new models match

**Decision**: All new domain models (`IncidentTimelineEvent`, `IncidentResponder`, `IncidentActionItem`, `IncidentAttachment`) use `ConfigDict(frozen=True)`, consistent with `Incident`.

**Rationale**: Frozen models prevent accidental mutation of domain objects in service logic. The existing convention must be preserved for consistency.

---

## Finding 9: Backfill script goes in `apps/api/scripts/`

**Decision**: Backfill script created at `apps/api/scripts/backfill_started_at.py`. Existing `apps/api/scripts/seed.py` confirms the scripts directory is the right location.

**Rationale**: The script needs DB access, uses the same `DATABASE_URL` env var, and is run as a standalone Python script like the existing `seed.py`.
