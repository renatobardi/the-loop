# Feature Specification: Incident Data Model — Production-Ready Schema

**Feature Branch**: `008-incident-data-model`  
**Created**: 2026-04-01  
**Status**: Draft  

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Data Integrity Guaranteed by Schema (Priority: P1)

An incident registry with silent type errors and missing constraints produces unreliable data. Engineers and the detection system cannot trust the data they read or write. This story ensures the schema enforces correctness at the storage level — no more silent failures, no more constraint bypasses.

**Why this priority**: Without correct types and constraints, all downstream features (MTTR calculation, RAG quality, SLA tracking) are built on a broken foundation. This is a prerequisite for everything else.

**Independent Test**: Can be tested by verifying that the system rejects data that violates constraints (e.g., a negative customers_affected value, a null type on a required boolean) and that type information is accurate when queried.

**Acceptance Scenarios**:

1. **Given** an incident is created with a missing value for a field that has a defined default, **When** the record is persisted, **Then** the default value is applied automatically without requiring the caller to provide it.
2. **Given** a field has a defined numeric constraint (e.g., confidence must be between 0 and 1), **When** a value outside the range is submitted, **Then** the system rejects the submission with a clear validation error.
3. **Given** a boolean field with a default value, **When** a record is created without specifying that field, **Then** the stored value reflects the correct default — not null.

---

### User Story 2 - Incident Responders Can Calculate MTTR and MTTD (Priority: P2)

Incident responders and engineering managers need to measure how fast the team detects and resolves incidents. Today, only the calendar date of an incident is stored — no start time, no detection time, no resolution time. This makes it impossible to calculate Mean Time to Detect (MTTD) or Mean Time to Resolve (MTTR) at any meaningful granularity.

**Why this priority**: MTTR and MTTD are key SLO/SLA metrics. Without timestamps, the platform cannot serve its core mission of incident prevention through measurement and learning.

**Independent Test**: Create an incident with start, detection, and resolution timestamps. Verify the system computes and exposes MTTD (time from start to detection) and MTTR (time from start to resolution) as derived values without requiring the caller to compute them manually.

**Acceptance Scenarios**:

1. **Given** an incident with a known start time and resolution time, **When** the incident is retrieved, **Then** the system returns a computed duration in minutes without requiring the caller to do the math.
2. **Given** an incident was created using only the legacy date field (day-level precision), **When** the system is queried for timestamps, **Then** the start timestamp is populated from the legacy date with no data loss.
3. **Given** an incident where start and detection timestamps are provided, **When** the start is after the detection, **Then** the system rejects the record with a temporal consistency error.
4. **Given** an incident with only a start timestamp (resolution not yet recorded), **When** duration is requested, **Then** the system returns null for duration rather than an incorrect computed value.

---

### User Story 3 - Postmortem Lifecycle Tracked End-to-End (Priority: P3)

After an incident is resolved, the team needs to produce a postmortem document. Today there is no way to track where a postmortem is in its lifecycle (draft → under review → approved → published) or who is responsible for it and by when. This story allows teams to manage the full postmortem lifecycle within the platform.

**Why this priority**: Postmortems are the primary mechanism for organizational learning. Without lifecycle tracking, they get lost or deprioritized. This directly impacts the platform's value proposition.

**Independent Test**: Create an incident, advance its postmortem through each status transition, and verify the system enforces the correct flow and records timestamps at each milestone.

**Acceptance Scenarios**:

1. **Given** a newly resolved incident, **When** a postmortem is started, **Then** the postmortem status begins as "draft" by default.
2. **Given** a postmortem in "approved" status, **When** it is published, **Then** the published timestamp is recorded automatically and the status transitions to "published".
3. **Given** an incident with a postmortem due date, **When** the due date passes without the postmortem reaching "approved", **Then** the overdue condition can be detected by querying incidents where due date is past and status is not approved.

---

### User Story 4 - Incident Timeline Events Captured (Priority: P4)

During an incident, key events happen in sequence: detection, escalation, mitigation, resolution, review. Currently, none of this chronology is captured. Responders, managers, and the AI detection layers need this ordered event log to understand how incidents unfold and how the team responded.

**Why this priority**: The event timeline is the raw material for SLA reporting and future Slack integration. It also provides the narrative structure for high-quality postmortem embeddings.

**Independent Test**: Create an incident and attach a sequence of timeline events with timestamps. Verify they can be retrieved in chronological order and that deleting the parent incident also removes all associated events.

**Acceptance Scenarios**:

1. **Given** an incident with multiple timeline events, **When** events are retrieved, **Then** they are ordered chronologically by the time each event occurred.
2. **Given** an incident is deleted, **When** the timeline events are queried, **Then** all events associated with that incident are also removed.
3. **Given** a timeline event with an optional reference to an external system (e.g., a link to a communication thread), **When** the event is created without that reference, **Then** the event is stored successfully with the reference as null.

---

### User Story 5 - Incident Responders Tracked with Roles (Priority: P5)

It is currently impossible to know who participated in an incident response and what role they played. This information is needed for audit trails, workload analysis, and recognition.

**Why this priority**: Responder tracking enables accountability and future analytics on team engagement and response patterns.

**Independent Test**: Assign two responders with different roles to an incident. Verify the system prevents the same person from being added twice to the same incident, and that role information is preserved.

**Acceptance Scenarios**:

1. **Given** an incident, **When** the same person is added as a responder twice, **Then** the system rejects the duplicate with a conflict error.
2. **Given** a responder with a recorded join time, **When** a departure time is provided that is before the join time, **Then** the system rejects the record.
3. **Given** a responder is assigned a role, **When** the incident is retrieved, **Then** the role is returned alongside the responder's identity.

---

### User Story 6 - Action Items Tracked to Closure (Priority: P6)

After a postmortem, follow-up action items need to be created, assigned, and tracked to completion. Without this, learnings from incidents do not translate into preventive action.

**Why this priority**: Closing the loop from incident → learning → action is the core promise of the platform's name. Action items make this concrete and measurable.

**Independent Test**: Create an action item for an incident, assign it to a user, mark it as completed. Verify the completion timestamp and responsible user are recorded.

**Acceptance Scenarios**:

1. **Given** an action item in "open" status, **When** it is marked as completed, **Then** the completion timestamp and completing user are recorded.
2. **Given** an action item with a priority of "critical", **When** it is retrieved, **Then** the priority is preserved and filterable.
3. **Given** an incident is deleted, **When** its action items are queried, **Then** all associated action items are also removed.

---

### User Story 7 - Postmortem Documents Attached to Incidents (Priority: P7)

Teams produce postmortem documents as PDFs, screenshots, and exported logs. Currently there is no way to associate these files with the incident they document. This story allows file attachments to be linked to incidents for future text extraction and embedding.

**Why this priority**: Attachment storage is the prerequisite for the Attachment Processor (text extraction pipeline). The schema must exist before the worker can be built.

**Independent Test**: Attach a file reference to an incident. Verify the attachment metadata (filename, type, storage path) is persisted and retrievable. Verify the extraction status starts as "pending".

**Acceptance Scenarios**:

1. **Given** an incident, **When** a file attachment is registered, **Then** the attachment's extraction status defaults to "pending".
2. **Given** an attachment with a file size, **When** a size of zero or negative is submitted, **Then** the system rejects the record.
3. **Given** an incident is deleted, **When** its attachments are queried, **Then** all associated attachments are also removed.

---

### User Story 8 - RAG Advisory Receives Rich Incident Content (Priority: P8)

The AI detection layer (L2 RAG Advisory) queries the incident registry to find similar past incidents. Its accuracy depends directly on the richness of each incident record. Currently, only a short anti-pattern description (~300 chars) is available. This story adds two structured content fields that significantly increase the quality of semantic matching.

**Why this priority**: Without rich content, the RAG layer has limited signal. This directly impacts detection precision for the platform's core AI feature.

**Independent Test**: Create an incident with structured postmortem content and technology context. Verify both fields are stored and retrieved without data loss. Verify incidents without these fields remain fully functional.

**Acceptance Scenarios**:

1. **Given** an incident created without the rich content fields, **When** it is retrieved, **Then** the missing fields return null without causing errors.
2. **Given** an incident with structured postmortem content, **When** it is updated, **Then** the full content is preserved including all nested fields.
3. **Given** an incident with technology context (languages, frameworks, infrastructure), **When** it is retrieved, **Then** all technology context is returned intact.

---

### Edge Cases

- What happens when a `started_at` timestamp is provided but `detected_at` or `ended_at` are null — computed metrics return null rather than incorrect values.
- What happens when an incident's legacy `date` field is null and no `started_at` is provided — backfill uses `created_at` as fallback.
- What happens when action items reference a deleted user as `owner_id` — the UUID persists as-is (no FK to a users table, no cascade); the action item is preserved with the original UUID intact.
- What happens when an attachment file size check is bypassed at the API level — the storage layer enforces the constraint independently.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST enforce correct types, NOT NULL constraints, and CHECK constraints on all new fields introduced by this spec. (Note: existing incident fields already have correct type annotations — no pre-existing `type_=None` bugs were found in the current codebase.)
- **FR-002**: System MUST apply default values (e.g., false for boolean flags, "draft" for postmortem status) automatically when a record is created without specifying optional fields.
- **FR-003**: System MUST store incident timestamps at sub-day precision with timezone awareness for start, detection, end, and resolution moments.
- **FR-004**: System MUST compute and expose MTTD (time from start to detection) and MTTR (time from start to resolution) as derived values from stored timestamps.
- **FR-005**: System MUST enforce temporal ordering — detection cannot precede start; resolution cannot precede end.
- **FR-006**: System MUST support backfilling timestamp data from the existing day-level date field for all historical incidents.
- **FR-007**: System MUST preserve the existing `date` field and continue accepting it alongside the new timestamp fields (backward compatibility).
- **FR-008**: System MUST track postmortem lifecycle status through the states: draft, in_review, approved, published. Transitions between states are free — no ordering is enforced; any valid status value may be set at any time.
- **FR-009**: System MUST record when a postmortem is published and by when it is due.
- **FR-010**: System MUST store operational incident metadata: impact summary, number of customers affected, SLA/SLO breach flags, detection method, external tracking identifier, and incident lead.
- **FR-011**: System MUST support a chronological event log per incident, with each event recording its type, description, when it occurred, and who recorded it.
- **FR-012**: System MUST remove all events, responders, action items, and attachments when a parent incident is deleted.
- **FR-013**: System MUST track which users responded to each incident, their roles, when they joined, and when they left.
- **FR-014**: System MUST prevent the same user from being recorded as a responder on the same incident more than once.
- **FR-015**: System MUST support creating, assigning, prioritizing, and completing follow-up action items for each incident.
- **FR-016**: System MUST record who completed an action item and when.
- **FR-017**: System MUST allow binary files (documents, screenshots, logs) to be registered as attachments to incidents, with each attachment tracking its storage location, type, size, and text extraction status.
- **FR-018**: System MUST default attachment extraction status to "pending" and enforce that file size is a positive value.
- **FR-019**: System MUST store structured postmortem narrative content per incident (summary, timeline, root cause, impact, remediation, prevention) as an optional enrichment field.
- **FR-020**: System MUST store technology context per incident (languages, frameworks, infrastructure, services, tools) as an optional enrichment field.
- **FR-021**: All new fields MUST be optional or carry defaults so that existing incident creation flows require no changes.

### Key Entities

- **Incident**: The core registry entry. Gains precise timestamps, operational metadata, postmortem lifecycle state, and two optional rich-content fields. Remains the parent of all related entities.
- **Incident Timeline Event**: A timestamped event in the incident response chronology. Belongs to one incident. Has a type, description, recorder, and optional external reference.
- **Incident Responder**: A person who participated in responding to a specific incident. Has a role, join time, and optional departure time. One person can only appear once per incident.
- **Incident Action Item**: A follow-up task created after an incident. Has a title, owner, priority, status, and due date. Tracks who completed it and when.
- **Incident Attachment**: A file registered against an incident. Tracks storage location, file metadata, content type, and text extraction status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero incidents in the registry have null values in fields that carry defined defaults after the migration runs.
- **SC-002**: 100% of incidents created before this change have their `started_at` timestamp populated (backfill completes with no data loss).
- **SC-003**: MTTD and MTTR are computable for any incident where the required timestamps exist — no manual calculation required.
- **SC-004**: All four new related tables (timeline events, responders, action items, attachments) accept writes and cascade deletes correctly.
- **SC-005**: Zero breaking changes to existing incident creation — all previously valid payloads continue to work unchanged.
- **SC-006**: The type validation suite passes with no failures related to missing or incorrect type annotations on incident-related data models.
- **SC-007**: Constraint violations (temporal ordering, negative file size, duplicate responder, negative customers_affected) are rejected with actionable error messages.
- **SC-008**: All sub-resource listing endpoints return the complete set of records for an incident in a single response with `{"items": [...], "total": N}` shape — no pagination required.

## Assumptions

- The existing incident table and its current fields remain intact — no fields are renamed or removed in this change.
- The `date` field is deprecated but not removed; it will be sunset in a future spec after a migration window.
- The vector index for semantic search (HNSW) is out of scope — it will be added when the embedding pipeline is operational.
- Automatic text extraction from attachments is out of scope — attachments are registered with "pending" status; the extraction worker is a separate feature.
- Revenue impact tracking is out of scope pending compliance review.
- SLA/SLO target configuration (thresholds) is out of scope — only breach flags (true/false) are captured here.
- New tables do **not** include a `tenant_id` column — the existing `incidents` table has no `tenant_id`, and all new tables are consistent with that single-tenant schema.
- The user reference used in all FK relationships (responder, action item owner, incident lead) refers to the identity already managed by the authentication system. Any syntactically valid UUID is accepted without validating existence against Firebase — consistent with the existing `created_by` field behavior.
- Authorization for all sub-resource endpoints (timeline events, responders, action items, attachments) follows the same model as the existing incident endpoints: any authenticated user may create, update, or delete records on any incident. No ownership-based access control is applied at this stage.

## Clarifications

### Session 2026-04-01

- Q: Should sub-resource endpoints (timeline, responders, action items, attachments) restrict operations to the incident owner/lead, or allow any authenticated user? → A: Any authenticated user may operate on any incident (inherits existing behavior — single-tenant, single operator).
- Q: Should listing endpoints for sub-resources support pagination? → A: No pagination — return all records with `{"items": [...], "total": N}` envelope. Volume per incident is naturally bounded.
- Q: How should the system handle `incident_lead_id`, `recorded_by`, `owner_id`, and similar user UUID fields when the UUID does not correspond to a known Firebase user? → A: Accept any syntactically valid UUID without validating existence against Firebase — consistent with existing `created_by` field behavior.
- Q: What is the latency SLO for the new sub-resource endpoints? → A: No explicit SLO — inherits platform defaults (single-tenant, low volume, no formal target required at this stage).
- Q: Should new endpoints emit structured logs beyond what the existing request/response middleware already captures? → A: No — middleware logging is sufficient; no domain-level event logging added.
