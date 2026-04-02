# Tasks: Incident Data Model — Production-Ready Schema

**Input**: Design documents from `specs/008-incident-data-model/`  
**Deployment Strategy**: 5 separate `feat/` branches — one PR + deploy per phase group

| Branch | Tasks | Scope |
|---|---|---|
| `feat/incident-data-model-schema-phase-1` | T001–T008 | Enums, exceptions, all migrations, backfill script |
| `feat/incident-data-model-schema-phase-2` | T009–T032, T080 | Extended Incident model (US1 constraints, US2 timestamps, US3 postmortem, US8 JSONB) |
| `feat/incident-data-model-schema-phase-3` | T033–T042 | Timeline events full stack |
| `feat/incident-data-model-schema-phase-4` | T043–T062 | Responders + Action items |
| `feat/incident-data-model-schema-phase-5` | T063–T079 | Attachments + Polish + Deploy |

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2...)
- Paths are relative to repo root

---

## Phase 1: Setup (Shared Infrastructure) — `feat/incident-data-model-schema-phase-1`

**Purpose**: Establish the new Python enums and exception classes used by all user stories. Pure Python — no DB required.

- [x] T001 Add new `StrEnum` classes to `apps/api/src/domain/models.py`: `PostmortemStatus`, `TimelineEventType`, `DetectionMethod`, `ResponderRole`, `ActionItemStatus`, `ActionItemPriority`, `AttachmentExtractionStatus`, `AttachmentType`
- [x] T002 Add new exception classes to `apps/api/src/domain/exceptions.py`: `TimelineEventNotFoundError`, `DuplicateResponderError`, `ResponderNotFoundError`, `ActionItemNotFoundError`, `AttachmentNotFoundError`

---

## Phase 2: Foundational (Database — Blocking All User Stories) — `feat/incident-data-model-schema-phase-1`

**Purpose**: All 5 Alembic migrations + backfill script. These are a strict dependency chain. **No user story implementation can be tested end-to-end until all migrations are applied.**

⚠️ **CRITICAL**: Apply migrations in order. Each migration sets `down_revision` to the previous revision ID.

- [x] T003 Create `apps/api/alembic/versions/002_add_operational_timestamps.py` with `revision="002"`, `down_revision="001"`. In `upgrade()`: `op.add_column` for `started_at`, `detected_at`, `ended_at`, `resolved_at` (all `DateTime(timezone=True) nullable`), and operational fields: `impact_summary` (Text nullable), `customers_affected` (Integer nullable), `sla_breached` (Boolean NOT NULL DEFAULT false), `slo_breached` (Boolean NOT NULL DEFAULT false), `postmortem_status` (String(50) NOT NULL DEFAULT 'draft'), `postmortem_published_at` (DateTime nullable), `postmortem_due_date` (Date nullable), `lessons_learned` (Text nullable), `why_we_were_surprised` (Text nullable), `detection_method` (String(50) nullable), `slack_channel_id` (String(50) nullable), `external_tracking_id` (String(255) nullable), `incident_lead_id` (Uuid nullable). Add CHECK constraints: `ck_incident_detect_after_start`, `ck_incident_end_before_resolve`, `ck_incident_customers_nonneg`. Add indexes on `started_at`, `detected_at`. Implement full `downgrade()`.
- [x] T004 Create `apps/api/alembic/versions/003_add_jsonb_fields.py` with `revision="003"`, `down_revision="002"`. In `upgrade()`: `op.add_column` for `raw_content` (JSONB nullable) and `tech_context` (JSONB nullable) on `incidents`. Full `downgrade()`.
- [x] T005 Create `apps/api/alembic/versions/004_add_incident_timeline_events.py` with `revision="004"`, `down_revision="003"`. In `upgrade()`: `op.create_table("incident_timeline_events", ...)` with all columns per `data-model.md`. `created_at` and `updated_at` must both have `server_default=sa.func.now()` in the DDL. FK `incident_id → incidents.id ON DELETE CASCADE`. Indexes: `(incident_id)`, `(occurred_at)`, composite `(incident_id, occurred_at)`. Full `downgrade()` with `op.drop_table`.
- [x] T006 Create `apps/api/alembic/versions/005_add_incident_responders_actions.py` with `revision="005"`, `down_revision="004"`. In `upgrade()`: create `incident_responders` table (FK `incident_id → incidents.id CASCADE`, UNIQUE `(incident_id, user_id)`, CHECK `(left_at IS NULL OR joined_at <= left_at)`, `created_at` and `updated_at` with `server_default=sa.func.now()`) and `incident_action_items` table (FK `incident_id → incidents.id CASCADE`, CHECK `char_length(title) > 0`, `created_at` and `updated_at` with `server_default=sa.func.now()`, all fields per `data-model.md`). Full `downgrade()` dropping both tables in reverse order.
- [x] T007 Create `apps/api/alembic/versions/006_add_incident_attachments.py` with `revision="006"`, `down_revision="005"`. In `upgrade()`: `op.create_table("incident_attachments", ...)` with FK `incident_id → incidents.id CASCADE`, CHECK `file_size_bytes > 0`, `server_default='pending'` on `extraction_status`, `created_at` and `updated_at` with `server_default=sa.func.now()`, all fields per `data-model.md`. Full `downgrade()`.
- [x] T008 Create `apps/api/scripts/backfill_started_at.py`. Script reads `DATABASE_URL` from environment, opens a sync SQLAlchemy session, and runs: `UPDATE incidents SET started_at = created_at AT TIME ZONE 'UTC' WHERE started_at IS NULL AND date IS NULL; UPDATE incidents SET started_at = CAST(date AS TIMESTAMPTZ) WHERE started_at IS NULL AND date IS NOT NULL`. Print counts of rows updated. Script must be idempotent.

**Checkpoint**: Run `alembic upgrade head` locally. All 6 migrations apply cleanly. `\dt incident_*` shows 4 new tables.

---

## Phase 3: User Story 1 — Data Integrity Guaranteed by Schema (Priority: P1) 🎯 MVP — `feat/incident-data-model-schema-phase-2`

**Goal**: All new schema objects have correct SQLAlchemy type annotations, NOT NULL constraints, CHECK constraints, and server defaults. mypy strict passes.

**Independent Test**: Apply migrations → inspect schema in psql → verify defaults (`sla_breached DEFAULT false`, `postmortem_status DEFAULT 'draft'`, `extraction_status DEFAULT 'pending'`) and CHECK constraints are enforced (submit negative `customers_affected`, get DB error).

- [x] T080 [P] [US1] Write backfill test in `apps/api/tests/unit/test_migrations.py`: `test_backfill_started_at_from_date` — insert incident with `date` set and `started_at=NULL`, run backfill script logic, verify `started_at` equals `CAST(date AS TIMESTAMPTZ)`; insert incident with `date=NULL` and `started_at=NULL`, verify `started_at` is populated from `created_at`. Covers SC-002.
- [x] T009 [P] [US1] Write migration schema test in `apps/api/tests/unit/test_migrations.py`: `test_incident_new_columns_have_correct_defaults` — create an `IncidentRow` without specifying `sla_breached`, `slo_breached`, `postmortem_status`; verify DB-level defaults are applied by refreshing the row.
- [x] T010 [P] [US1] Write migration constraint test in `apps/api/tests/unit/test_migrations.py`: `test_customers_affected_check_constraint` — attempt to insert an incident with `customers_affected = -1`; verify IntegrityError is raised.
- [x] T011 [US1] Write migration constraint test: `test_temporal_ordering_constraint` — attempt `started_at > detected_at`; verify IntegrityError. Attempt `started_at <= detected_at`; verify succeeds.

**Checkpoint**: `pytest apps/api/tests/unit/test_migrations.py` — 4 tests green.

---

## Phase 4: User Story 2 — Incident Responders Can Calculate MTTR and MTTD (Priority: P2) — `feat/incident-data-model-schema-phase-2`

**Goal**: Incidents store `started_at`, `detected_at`, `ended_at`, `resolved_at`. `GET /api/v1/incidents/{id}` response includes `duration_minutes`, `time_to_detect_minutes`, `time_to_resolve_minutes` as computed values.

**Independent Test**: POST incident with `started_at`, `detected_at`, `ended_at` → GET incident → verify `duration_minutes`, `time_to_detect_minutes` are correct integers. POST without timestamps → verify computed fields are `null`, not error.

- [x] T012 [P] [US2] Extend `Incident` Pydantic model in `apps/api/src/domain/models.py`: add `started_at: datetime | None = None`, `detected_at: datetime | None = None`, `ended_at: datetime | None = None`, `resolved_at: datetime | None = None`. Add `@model_validator(mode='after')` for temporal ordering constraints. Add three `@property` methods: `duration_minutes`, `time_to_detect_minutes`, `time_to_resolve_minutes` — each returns `int | None` (difference in whole minutes, or `None` if either timestamp is absent). Keep `model_config = ConfigDict(frozen=True)`.
- [x] T013 [US2] Extend `IncidentRow` in `apps/api/src/adapters/postgres/models.py`: add `started_at`, `detected_at`, `ended_at`, `resolved_at` as `Mapped[datetime | None]` with `DateTime(timezone=True)` type and `nullable=True`.
- [x] T014 [US2] Update `_row_to_domain()` in `apps/api/src/adapters/postgres/repository.py`: pass new timestamp fields when constructing `Incident`.
- [x] T015 [US2] Update `IncidentService.create()` in `apps/api/src/domain/services.py`: accept and forward `started_at`, `detected_at`, `ended_at`, `resolved_at` kwargs.
- [x] T016 [US2] Update `IncidentCreateRequest` in `apps/api/src/api/routes/incidents.py`: add `started_at`, `detected_at`, `ended_at`, `resolved_at` as `datetime | None = None` fields with ISO 8601 string annotations.
- [x] T017 [US2] Update `IncidentResponse` in `apps/api/src/api/routes/incidents.py`: add `started_at`, `detected_at`, `ended_at`, `resolved_at`, `duration_minutes`, `time_to_detect_minutes`, `time_to_resolve_minutes`. Update `from_domain()` to populate these from the domain object's properties.
- [x] T018 [US2] Update `IncidentUpdateRequest` in `apps/api/src/api/routes/incidents.py`: add timestamp fields as `datetime | None = None`. Update `IncidentService.update()` allowed_fields set to include them.
- [x] T019 [P] [US2] Write domain unit tests in `apps/api/tests/unit/domain/test_incident.py`: `test_duration_minutes_computed`, `test_time_to_detect_computed`, `test_duration_returns_none_when_end_missing`, `test_temporal_ordering_validator_rejects_detected_before_started`.
- [x] T020 [P] [US2] Write API tests in `apps/api/tests/api/test_incidents.py`: `test_create_incident_with_timestamps_returns_computed_metrics`, `test_get_incident_without_timestamps_returns_null_metrics`, `test_create_incident_legacy_payload_no_new_fields_succeeds` — POST with only the original required fields (title, category, severity, anti_pattern, remediation), no new fields; verify 201 and that all new fields return null or their defaults. Covers SC-005.

**Checkpoint**: `pytest apps/api/tests/ -k "timestamp or duration or detect"` — all green.

---

## Phase 5: User Story 3 — Postmortem Lifecycle Tracked End-to-End (Priority: P3) — `feat/incident-data-model-schema-phase-2`

**Goal**: Incidents expose postmortem lifecycle fields. `PUT /api/v1/incidents/{id}` can advance `postmortem_status`. `postmortem_published_at` is set automatically when status transitions to `"published"`.

**Independent Test**: Create incident → GET response shows `postmortem_status: "draft"`. PUT with `postmortem_status: "published"` → `postmortem_published_at` is populated automatically.

- [x] T021 [P] [US3] Extend `Incident` in `apps/api/src/domain/models.py`: add `impact_summary`, `customers_affected`, `sla_breached`, `slo_breached`, `postmortem_status`, `postmortem_published_at`, `postmortem_due_date`, `lessons_learned`, `why_we_were_surprised`, `detection_method`, `slack_channel_id`, `external_tracking_id`, `incident_lead_id` — all with correct Python types and defaults matching schema. Add `@field_validator` for `customers_affected >= 0`. Use `PostmortemStatus` and `DetectionMethod` enums.
- [x] T022 [US3] Extend `IncidentRow` in `apps/api/src/adapters/postgres/models.py`: add all operational/postmortem columns as `Mapped[...]` with correct SQLAlchemy types matching migration 002.
- [x] T023 [US3] Update `_row_to_domain()` in `apps/api/src/adapters/postgres/repository.py`: pass all new fields when constructing `Incident`.
- [x] T024 [US3] Update `IncidentService.create()` and `update()` in `apps/api/src/domain/services.py`: accept and forward all new operational/postmortem fields. In `update()`, when `postmortem_status` transitions to `PostmortemStatus.PUBLISHED` and `postmortem_published_at` is not already set, auto-populate `postmortem_published_at = datetime.now(UTC)`. Note: status transitions are **free** — no ordering enforced; any valid `PostmortemStatus` value is accepted in any order.
- [x] T025 [US3] Update `IncidentCreateRequest` and `IncidentUpdateRequest` in `apps/api/src/api/routes/incidents.py`: add all postmortem + operational fields as optional. Update `IncidentService.create()` call to pass new fields. Update `allowed_fields` in `IncidentService.update()`.
- [x] T026 [US3] Update `IncidentResponse.from_domain()` in `apps/api/src/api/routes/incidents.py`: expose all new fields.
- [x] T027 [P] [US3] Write domain unit tests in `apps/api/tests/unit/domain/test_incident.py`: `test_customers_affected_negative_rejected`, `test_postmortem_status_default_is_draft`.
- [x] T028 [P] [US3] Write API tests in `apps/api/tests/api/test_incidents.py`: `test_create_incident_defaults_postmortem_status_draft`, `test_update_postmortem_status_to_published_sets_timestamp`.

**Checkpoint**: `pytest apps/api/tests/ -k "postmortem or operational"` — all green.

---

## Phase 6: User Story 8 — RAG Advisory Receives Rich Incident Content (Priority: P8) — `feat/incident-data-model-schema-phase-2`

**Goal**: Incidents accept and return `raw_content` and `tech_context` JSONB fields. Incidents without these fields continue to work normally (`null` returned).

**Independent Test**: POST incident with `raw_content` JSON object → GET → exact JSON preserved. POST without `raw_content` → GET → `null` (no error).

- [x] T029 [P] [US8] Extend `Incident` in `apps/api/src/domain/models.py`: add `raw_content: dict[str, object] | None = None` and `tech_context: dict[str, object] | None = None`.
- [x] T031a [US8] Extend `IncidentRow` in `apps/api/src/adapters/postgres/models.py`: add `raw_content` and `tech_context` as `Mapped[dict | None]` with `mapped_column(JSONB, nullable=True)`. Update `_row_to_domain()` in `apps/api/src/adapters/postgres/repository.py` to pass both fields.
- [x] T031b [US8] Update `IncidentService.create()` and `update()` in `apps/api/src/domain/services.py`: accept and forward `raw_content` and `tech_context`.
- [x] T031c [US8] Update `IncidentCreateRequest`, `IncidentUpdateRequest`, and `IncidentResponse.from_domain()` in `apps/api/src/api/routes/incidents.py`: expose `raw_content` and `tech_context` in request and response schemas.
- [x] T032 [P] [US8] Write API tests in `apps/api/tests/api/test_incidents.py`: `test_create_incident_with_raw_content_preserved`, `test_create_incident_without_raw_content_returns_null`.

**Checkpoint**: `pytest apps/api/tests/ -k "raw_content or tech_context or jsonb"` — all green.

---

## Phase 7: User Story 4 — Incident Timeline Events Captured (Priority: P4) — `feat/incident-data-model-schema-phase-3`

**Goal**: `POST /api/v1/incidents/{id}/timeline` creates timeline events. `GET` returns them in chronological order. Deleting an incident cascades to delete its events.

**Independent Test**: Create incident → add 3 timeline events with different `occurred_at` → GET timeline → events ordered chronologically. Delete incident → confirm cascade.

- [x] T033 [P] [US4] Add `IncidentTimelineEvent` domain model to `apps/api/src/domain/models.py`: `id`, `incident_id`, `event_type: TimelineEventType`, `description`, `occurred_at`, `recorded_by`, `duration_minutes`, `external_reference_url`, `created_at`, `updated_at`. `ConfigDict(frozen=True)`. Field validators: `description` not empty, `duration_minutes >= 0` if provided.
- [x] T034 [P] [US4] Create `apps/api/src/ports/timeline_event_repo.py`: `TimelineEventRepoPort` Protocol with methods `create(event) -> IncidentTimelineEvent`, `list_by_incident(incident_id, *, order_asc=True) -> list[IncidentTimelineEvent]`, `delete(event_id) -> None`.
- [x] T035 [US4] Add `IncidentTimelineEventRow` to `apps/api/src/adapters/postgres/models.py`: all columns matching migration 004. FK relationship via `incident_id` column. `updated_at` mapped column must include `onupdate=func.now()` so it refreshes automatically on every UPDATE.
- [x] T036 [US4] Create `apps/api/src/adapters/postgres/timeline_event_repository.py`: implement `TimelineEventRepoPort`. `list_by_incident` orders by `occurred_at ASC`. `delete` raises `TimelineEventNotFoundError` if not found.
- [x] T037 [US4] Create `apps/api/src/domain/services.py` additions: `TimelineEventService(repo: TimelineEventRepoPort)` with `create(incident_id, ...) -> IncidentTimelineEvent` (validates `event_type` is valid `TimelineEventType`) and `list_by_incident(incident_id) -> list[IncidentTimelineEvent]` and `delete(event_id) -> None`.
- [x] T038 [US4] Add dependency factories to `apps/api/src/api/deps.py`: `get_timeline_event_repository()` and `get_timeline_event_service()`.
- [x] T039 [US4] Create `apps/api/src/api/routes/timeline.py`: router with prefix `/api/v1/incidents/{incident_id}/timeline`. Implement `POST` (201), `GET` (list, 200), `DELETE /{event_id}` (200). All endpoints: `@limiter.limit("60/minute")`, `Depends(get_authenticated_user)`. `POST` validates incident existence via `Depends(get_incident_service)` + `await incident_service.get_by_id(incident_id)` — `IncidentNotFoundError` maps to 404. Same incident existence check on `GET` and `DELETE`. Request schema: `TimelineEventCreateRequest`. Response schema: `TimelineEventResponse` with `from_domain()`.
- [x] T040 [US4] Register `timeline_router` in `apps/api/src/main.py` with `app.include_router(timeline_router)`.
- [x] T041 [P] [US4] Write unit tests in `apps/api/tests/unit/domain/test_timeline_event.py`: `test_create_timeline_event`, `test_invalid_event_type_rejected`, `test_negative_duration_rejected`.
- [x] T042 [P] [US4] Write API tests in `apps/api/tests/api/test_timeline.py`: `test_create_timeline_event`, `test_list_timeline_events_ordered_chronologically` (assert response shape is `{"items": [...], "total": N}` — SC-008), `test_delete_timeline_event`, `test_timeline_for_unknown_incident_returns_404`, `test_delete_incident_cascades_to_timeline_events` (create incident + events, DELETE incident, confirm events gone — SC-004).

**Checkpoint**: `pytest apps/api/tests/ -k timeline` — all green.

---

## Phase 8: User Story 5 — Incident Responders Tracked with Roles (Priority: P5) — `feat/incident-data-model-schema-phase-4`

**Goal**: `POST /api/v1/incidents/{id}/responders` adds a responder. System rejects duplicate user on same incident with 409. `PUT /{id}/responders/{rid}` updates `left_at` and `contribution_summary`.

**Independent Test**: Add responder A (role=technical_lead) → add same user again → 409 conflict. Add responder B → list returns 2 responders. PUT to set `left_at` → updated timestamp preserved.

- [x] T043 [P] [US5] Add `IncidentResponder` domain model to `apps/api/src/domain/models.py`: `id`, `incident_id`, `user_id`, `role: ResponderRole`, `joined_at`, `left_at`, `contribution_summary`, `created_at`, `updated_at`. `ConfigDict(frozen=True)`. Validator: `left_at >= joined_at` if both present.
- [x] T044 [P] [US5] Create `apps/api/src/ports/responder_repo.py`: `ResponderRepoPort` Protocol with `create(responder) -> IncidentResponder`, `list_by_incident(incident_id) -> list[IncidentResponder]`, `get_by_id(responder_id) -> IncidentResponder | None`, `update(responder) -> IncidentResponder`, `delete(responder_id) -> None`.
- [x] T045 [US5] Add `IncidentResponderRow` to `apps/api/src/adapters/postgres/models.py`: all columns matching migration 005. UNIQUE constraint note in code comments. `updated_at` mapped column must include `onupdate=func.now()`.
- [x] T046 [US5] Create `apps/api/src/adapters/postgres/responder_repository.py`: implement `ResponderRepoPort`. `create` catches `IntegrityError` on UNIQUE violation and raises `DuplicateResponderError`. `update` and `delete` raise `ResponderNotFoundError` if not found.
- [x] T047 [US5] Add `ResponderService` to `apps/api/src/domain/services.py`: `add_responder(incident_id, ...) -> IncidentResponder`, `list_responders(incident_id) -> list[IncidentResponder]`, `update_responder(responder_id, **fields) -> IncidentResponder`, `remove_responder(responder_id) -> None`.
- [x] T048 [US5] Add dependency factories to `apps/api/src/api/deps.py`: `get_responder_repository()` and `get_responder_service()`.
- [x] T049 [US5] Create `apps/api/src/api/routes/responders.py`: router with prefix `/api/v1/incidents/{incident_id}/responders`. `POST` (201), `GET` (200), `PUT /{responder_id}` (200), `DELETE /{responder_id}` (200). All endpoints validate incident existence via `Depends(get_incident_service)` + `await incident_service.get_by_id(incident_id)` — `IncidentNotFoundError` maps to 404. `POST` also maps `DuplicateResponderError` → 409.
- [x] T050 [US5] Register `responders_router` in `apps/api/src/main.py`.
- [x] T051 [P] [US5] Write unit tests in `apps/api/tests/unit/domain/test_responder.py`: `test_create_responder`, `test_left_before_joined_rejected`.
- [x] T052 [P] [US5] Write API tests in `apps/api/tests/api/test_responders.py`: `test_add_responder`, `test_duplicate_responder_returns_409`, `test_update_responder_left_at`, `test_delete_responder`, `test_list_responders_returns_items_total_envelope` (assert `{"items": [...], "total": N}` shape — SC-008), `test_delete_incident_cascades_to_responders` (create incident + responder, DELETE incident, confirm responder gone — SC-004).

**Checkpoint**: `pytest apps/api/tests/ -k responder` — all green.

---

## Phase 9: User Story 6 — Action Items Tracked to Closure (Priority: P6) — `feat/incident-data-model-schema-phase-4`

**Goal**: `POST /api/v1/incidents/{id}/action-items` creates items with `status: "open"`. `PUT` with `status: "completed"` auto-populates `completed_at` and `completed_by`.

**Independent Test**: Create action item → status defaults to `open`. PUT `status=completed, completed_by=<uid>` → `completed_at` is set automatically. GET action items → filter by `?status=open` returns only open items.

- [x] T053 [P] [US6] Add `IncidentActionItem` domain model to `apps/api/src/domain/models.py`: all fields per `data-model.md`, using `ActionItemStatus` and `ActionItemPriority` enums. Validator: `title` not empty.
- [x] T054 [P] [US6] Create `apps/api/src/ports/action_item_repo.py`: `ActionItemRepoPort` Protocol with `create`, `list_by_incident(incident_id, *, status_filter=None)`, `get_by_id`, `update`, `delete`.
- [x] T055 [US6] Add `IncidentActionItemRow` to `apps/api/src/adapters/postgres/models.py`: all columns matching migration 005. `updated_at` mapped column must include `onupdate=func.now()`.
- [x] T056 [US6] Create `apps/api/src/adapters/postgres/action_item_repository.py`: implement `ActionItemRepoPort`. `list_by_incident` supports optional `status` filter. `update` and `delete` raise `ActionItemNotFoundError` if not found.
- [x] T057 [US6] Add `ActionItemService` to `apps/api/src/domain/services.py`: `create_action_item(incident_id, ...) -> IncidentActionItem`, `list_action_items(incident_id, *, status=None) -> list[IncidentActionItem]`, `update_action_item(item_id, **fields) -> IncidentActionItem` — when `status` transitions to `ActionItemStatus.COMPLETED`, auto-sets `completed_at = datetime.now(UTC)`. `completed_by` is provided by the caller in the PUT request body (UUID of the completing user) — the service stores it as-is, consistent with how `recorded_by` and `incident_lead_id` work.
- [x] T058 [US6] Add dependency factories to `apps/api/src/api/deps.py`: `get_action_item_repository()` and `get_action_item_service()`.
- [x] T059 [US6] Create `apps/api/src/api/routes/action_items.py`: router with prefix `/api/v1/incidents/{incident_id}/action-items`. `POST` (201), `GET` with optional `?status=` query param (200), `PUT /{item_id}` (200), `DELETE /{item_id}` (200). All endpoints validate incident existence via `Depends(get_incident_service)` + `await incident_service.get_by_id(incident_id)` — `IncidentNotFoundError` maps to 404. Also map `ActionItemNotFoundError` → 404 on PUT/DELETE.
- [x] T060 [US6] Register `action_items_router` in `apps/api/src/main.py`.
- [x] T061 [P] [US6] Write unit tests in `apps/api/tests/unit/domain/test_action_item.py`: `test_create_action_item_defaults_status_open`, `test_empty_title_rejected`.
- [x] T062 [P] [US6] Write API tests in `apps/api/tests/api/test_action_items.py`: `test_create_action_item`, `test_complete_action_item_sets_completed_at`, `test_list_action_items_filter_by_status`, `test_list_action_items_returns_items_total_envelope` (assert `{"items": [...], "total": N}` shape — SC-008), `test_delete_action_item`, `test_delete_incident_cascades_to_action_items` (create incident + action item, DELETE incident, confirm action item gone — SC-004).

**Checkpoint**: `pytest apps/api/tests/ -k action_item` — all green.

---

## Phase 10: User Story 7 — Postmortem Documents Attached to Incidents (Priority: P7) — `feat/incident-data-model-schema-phase-5`

**Goal**: `POST /api/v1/incidents/{id}/attachments` registers attachment metadata. `extraction_status` defaults to `"pending"`. Negative or zero `file_size_bytes` is rejected with 422.

**Independent Test**: POST attachment with valid metadata → `extraction_status: "pending"` in response. POST with `file_size_bytes: 0` → 422. DELETE incident → attachments gone.

- [x] T063 [P] [US7] Add `IncidentAttachment` domain model to `apps/api/src/domain/models.py`: all fields per `data-model.md`. Use `AttachmentExtractionStatus` and `AttachmentType` enums. Validator: `file_size_bytes > 0`.
- [x] T064 [P] [US7] Create `apps/api/src/ports/attachment_repo.py`: `AttachmentRepoPort` Protocol with `create`, `list_by_incident`, `get_by_id`, `delete`.
- [x] T065 [US7] Add `IncidentAttachmentRow` to `apps/api/src/adapters/postgres/models.py`: all columns matching migration 006. `updated_at` mapped column must include `onupdate=func.now()`.
- [x] T066 [US7] Create `apps/api/src/adapters/postgres/attachment_repository.py`: implement `AttachmentRepoPort`. `delete` raises `AttachmentNotFoundError` if not found.
- [x] T067 [US7] Add `AttachmentService` to `apps/api/src/domain/services.py`: `register_attachment(incident_id, ...) -> IncidentAttachment` — defaults `extraction_status = AttachmentExtractionStatus.PENDING`. `list_attachments(incident_id) -> list[IncidentAttachment]`. `delete_attachment(attachment_id) -> None`.
- [x] T068 [US7] Add dependency factories to `apps/api/src/api/deps.py`: `get_attachment_repository()` and `get_attachment_service()`.
- [x] T069 [US7] Create `apps/api/src/api/routes/attachments.py`: router with prefix `/api/v1/incidents/{incident_id}/attachments`. `POST` (201), `GET` (200), `DELETE /{attachment_id}` (200). All endpoints validate incident existence via `Depends(get_incident_service)` + `await incident_service.get_by_id(incident_id)` — `IncidentNotFoundError` maps to 404. Also map `AttachmentNotFoundError` → 404 on DELETE.
- [x] T070 [US7] Register `attachments_router` in `apps/api/src/main.py`.
- [x] T071 [P] [US7] Write unit tests in `apps/api/tests/unit/domain/test_attachment.py`: `test_create_attachment_defaults_extraction_pending`, `test_zero_file_size_rejected`, `test_negative_file_size_rejected`.
- [x] T072 [P] [US7] Write API tests in `apps/api/tests/api/test_attachments.py`: `test_register_attachment`, `test_zero_file_size_returns_422`, `test_list_attachments_returns_items_total_envelope` (assert `{"items": [...], "total": N}` shape — SC-008), `test_delete_attachment_returns_200`, `test_delete_incident_cascades_to_attachments` (create incident + attachment, DELETE incident, confirm attachment gone — SC-004).

**Checkpoint**: `pytest apps/api/tests/ -k attachment` — all green.

---

## Phase 11: Polish & Cross-Cutting Concerns — `feat/incident-data-model-schema-phase-5`

**Purpose**: Quality gates, CI validation, and production deploy.

- [x] T079 Verify all 4 new routers are registered in `apps/api/src/main.py`: confirm `timeline_router`, `responders_router`, `action_items_router`, `attachments_router` each appear in an `app.include_router()` call. Fix any missing registration before opening the phase-5 PR.
- [x] T073 Run `ruff check apps/api/src/ apps/api/tests/` — fix all lint errors. Run `ruff format apps/api/src/ apps/api/tests/` — apply formatting.
- [x] T074 Run `mypy apps/api/src/` — fix all strict mode errors. Confirm no `type_=None` or untyped field issues in any new model.
- [x] T075 Run `pytest apps/api/tests/ --cov=src --cov-report=term-missing` — confirm coverage ≥ 80%.
- [x] T076 [P] Run `bash scripts/generate-docs.sh` from repo root, then `git add` and commit all changes to generated docs. The `docs-check` CI gate always runs — docs output must be committed before opening the PR.
- [x] T077 Create one PR per branch (`feat/incident-data-model-schema-phase-N → main`). PR titles: `feat(api): incident data model phase N — <scope>`. Confirm all CI gates pass on each PR before merge: ruff, mypy, pytest, Docker build, Trivy.
- [x] T078 After PR merges: run `alembic upgrade head` against Cloud SQL production instance before Cloud Run restarts. Run `backfill_started_at.py` if production incidents table has rows with `date != NULL`.

**Checkpoint**: All CI gates green. Production migrated. `GET /api/v1/health` returns 200.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 (enums referenced in migrations)
- **Phase 3 (US1)**: Depends on Phase 2 (needs real DB to test constraints)
- **Phase 4–10 (US2–US7)**: Each depends on Phase 2 complete. Can proceed in any order after Phase 2.
- **Phase 11 (Polish)**: Depends on all story phases complete

### User Story Dependencies

- **US2 (P2)**: Independent after Phase 2. No dependency on US1.
- **US3 (P3)**: Shares migration 002 with US2 (same DB columns). Domain work is independent.
- **US4 (P4)**: Independent after Phase 2.
- **US5 (P5)**: Independent after Phase 2. Migration 005 also creates US6 table — apply migration before starting US5 or US6.
- **US6 (P6)**: Independent after Phase 2. Migration 005 shared with US5.
- **US7 (P7)**: Independent after Phase 2.
- **US8 (P8)**: Independent after Phase 2.

### Within Each Phase

- Domain model tasks `[P]` before service tasks
- Port tasks `[P]` before adapter tasks
- Adapter tasks before service tasks
- Service tasks before route tasks
- Route tasks before `main.py` registration

### Parallel Opportunities

- T001 and T002 can run in parallel (different files)
- T003–T007 are sequential (migration chain: each depends on previous revision)
- T033, T034 (US4 domain + port) can run in parallel
- T043, T044 (US5 domain + port) can run in parallel
- T053, T054 (US6 domain + port) can run in parallel
- T063, T064 (US7 domain + port) can run in parallel
- All test tasks marked `[P]` within a phase can run in parallel with their implementation

---

## Parallel Example: User Story 4 (Timeline Events)

```bash
# Step 1 — Run in parallel:
Task T033: Add IncidentTimelineEvent to domain/models.py
Task T034: Create ports/timeline_event_repo.py

# Step 2 — After T033 + T034 complete:
Task T035: Add IncidentTimelineEventRow to adapters/postgres/models.py

# Step 3 — After T035:
Task T036: Create adapters/postgres/timeline_event_repository.py

# Step 4 — After T036:
Task T037: Add TimelineEventService to domain/services.py
Task T038: Add deps to api/deps.py  (can run in parallel with T037)

# Step 5 — After T037 + T038:
Task T039: Create api/routes/timeline.py
Task T041: Write unit tests (can run in parallel with T039)
Task T042: Write API tests (can run in parallel with T039)

# Step 6 — After T039:
Task T040: Register router in main.py
```

---

## Implementation Strategy

### MVP First (US2 — MTTR/MTTD)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: All migrations (T003–T008)
3. Complete Phase 4: US2 timestamps (T012–T020)
4. **STOP and VALIDATE**: `POST /incidents` with timestamps → `duration_minutes` in response
5. Merge to production — MTTR/MTTD now measurable

### Incremental Delivery (recommended order)

1. Phase 1+2 → Foundation (migrations + backfill)
2. Phase 4 (US2) + Phase 5 (US3) → updated incident model (MTTR + postmortem)
3. Phase 6 (US8) → JSONB enrichment
4. Phase 7 (US4) → timeline events
5. Phase 8 (US5) + Phase 9 (US6) → responders + action items (same migration, same PR)
6. Phase 10 (US7) → attachments
7. Phase 11 → deploy

---

## Notes

- `[P]` = different files, no blocking dependencies
- Migrations T003–T007 are strictly sequential (Alembic revision chain)
- Migration 005 creates BOTH `incident_responders` and `incident_action_items` — apply it before starting US5 or US6
- `from __future__ import annotations` is required in all new source files (project convention)
- All new route files must use `@limiter.limit("60/minute")` from `src.api.middleware`
- Commit after each checkpoint — never mix migration commits with domain/API commits
