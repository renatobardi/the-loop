# Data Model: Incident Data Model — Production-Ready Schema

**Feature**: 008-incident-data-model  
**Date**: 2026-04-01

---

## Overview

This feature extends the existing `incidents` table and adds 4 new tables. All changes are backward-compatible: new columns are either nullable or carry server-side defaults.

**Migration sequence**: `001` (existing) → `002` → `003` → `004` → `005` → `006`

---

## Existing Table: `incidents` — Extended

### New columns added by migration `002` (operational timestamps + fields)

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| `started_at` | `TIMESTAMPTZ` | yes | — | index |
| `detected_at` | `TIMESTAMPTZ` | yes | — | index |
| `ended_at` | `TIMESTAMPTZ` | yes | — | — |
| `resolved_at` | `TIMESTAMPTZ` | yes | — | — |
| `impact_summary` | `TEXT` | yes | — | — |
| `customers_affected` | `INTEGER` | yes | — | `CHECK >= 0` |
| `sla_breached` | `BOOLEAN` | no | `false` | — |
| `slo_breached` | `BOOLEAN` | no | `false` | — |
| `postmortem_status` | `VARCHAR(50)` | no | `'draft'` | — |
| `postmortem_published_at` | `TIMESTAMPTZ` | yes | — | — |
| `postmortem_due_date` | `DATE` | yes | — | — |
| `lessons_learned` | `TEXT` | yes | — | — |
| `why_we_were_surprised` | `TEXT` | yes | — | — |
| `detection_method` | `VARCHAR(50)` | yes | — | — |
| `slack_channel_id` | `VARCHAR(50)` | yes | — | — |
| `external_tracking_id` | `VARCHAR(255)` | yes | — | — |
| `incident_lead_id` | `UUID` | yes | — | — |

**DB-enforced constraints (new CHECK constraints)**:
```sql
CHECK (started_at IS NULL OR detected_at IS NULL OR started_at <= detected_at)
CHECK (ended_at IS NULL OR resolved_at IS NULL OR ended_at <= resolved_at)
CHECK (customers_affected IS NULL OR customers_affected >= 0)
```

**Computed properties (Python only — no DB column)**:
- `duration_minutes`: `(ended_at - started_at)` in minutes, or `None`
- `time_to_detect_minutes`: `(detected_at - started_at)` in minutes, or `None`
- `time_to_resolve_minutes`: `(resolved_at - started_at)` in minutes, or `None`

### New columns added by migration `003` (JSONB enrichment)

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `raw_content` | `JSONB` | yes | — | Rich postmortem narrative for embedding |
| `tech_context` | `JSONB` | yes | — | Technology stack for pre-RAG semantic filtering |

**Expected `raw_content` shape** (not enforced at DB level):
```json
{
  "summary": "string",
  "timeline": "string",
  "root_cause": "string",
  "contributing_factors": ["string"],
  "impact_details": "string",
  "remediation_steps": "string",
  "prevention": "string"
}
```

**Expected `tech_context` shape** (not enforced at DB level):
```json
{
  "languages": ["string"],
  "frameworks": ["string"],
  "infrastructure": ["string"],
  "services": ["string"],
  "tools": ["string"]
}
```

---

## New Table: `incident_timeline_events` — Migration `004`

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `UUID` | no | `gen_random_uuid()` | PK |
| `incident_id` | `UUID` | no | — | FK → `incidents.id` ON DELETE CASCADE |
| `event_type` | `VARCHAR(50)` | no | — | Enum values below |
| `description` | `TEXT` | no | — | — |
| `occurred_at` | `TIMESTAMPTZ` | no | — | index |
| `recorded_by` | `UUID` | no | — | Firebase user UUID (no FK) |
| `duration_minutes` | `INTEGER` | yes | — | Optional, for mitigation events |
| `external_reference_url` | `VARCHAR(2048)` | yes | — | Slack thread, PagerDuty, etc. |
| `created_at` | `TIMESTAMPTZ` | no | `now()` | — |
| `updated_at` | `TIMESTAMPTZ` | no | `now()` | — |

**Indexes**: `(incident_id)`, `(occurred_at)`, `(incident_id, occurred_at)` composite

**`event_type` valid values**: `detected` | `escalated` | `mitigated` | `resolved` | `reviewed` | `postmortem_published`

---

## New Table: `incident_responders` — Migration `005`

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `UUID` | no | `gen_random_uuid()` | PK |
| `incident_id` | `UUID` | no | — | FK → `incidents.id` ON DELETE CASCADE |
| `user_id` | `UUID` | no | — | Firebase user UUID (no FK) |
| `role` | `VARCHAR(50)` | no | — | Enum values below |
| `joined_at` | `TIMESTAMPTZ` | no | `now()` | — |
| `left_at` | `TIMESTAMPTZ` | yes | — | — |
| `contribution_summary` | `TEXT` | yes | — | — |
| `created_at` | `TIMESTAMPTZ` | no | `now()` | — |
| `updated_at` | `TIMESTAMPTZ` | no | `now()` | — |

**Constraints**:
- `UNIQUE (incident_id, user_id)` — one entry per user per incident
- `CHECK (left_at IS NULL OR joined_at <= left_at)`

**Indexes**: `(incident_id)`, `(user_id)`

**`role` valid values**: `incident_commander` | `technical_lead` | `communication_lead` | `remediation_lead` | `responder` | `postmortem_lead`

---

## New Table: `incident_action_items` — Migration `005`

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `UUID` | no | `gen_random_uuid()` | PK |
| `incident_id` | `UUID` | no | — | FK → `incidents.id` ON DELETE CASCADE |
| `title` | `VARCHAR(500)` | no | — | `CHECK (char_length(title) > 0)` |
| `description` | `TEXT` | yes | — | — |
| `owner_id` | `UUID` | yes | — | Firebase user UUID (no FK) |
| `status` | `VARCHAR(50)` | no | `'open'` | Enum values below |
| `priority` | `VARCHAR(20)` | no | `'medium'` | Enum values below |
| `due_date` | `DATE` | yes | — | — |
| `completed_at` | `TIMESTAMPTZ` | yes | — | — |
| `completed_by` | `UUID` | yes | — | Firebase user UUID (no FK) |
| `created_at` | `TIMESTAMPTZ` | no | `now()` | — |
| `updated_at` | `TIMESTAMPTZ` | no | `now()` | — |

**Indexes**: `(incident_id)`, `(owner_id)`

**`status` valid values**: `open` | `in_progress` | `completed` | `cancelled`  
**`priority` valid values**: `low` | `medium` | `high` | `critical`

---

## New Table: `incident_attachments` — Migration `006`

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `UUID` | no | `gen_random_uuid()` | PK |
| `incident_id` | `UUID` | no | — | FK → `incidents.id` ON DELETE CASCADE |
| `uploaded_by` | `UUID` | yes | — | Firebase user UUID (no FK) |
| `filename` | `VARCHAR(500)` | no | — | — |
| `mime_type` | `VARCHAR(100)` | no | — | — |
| `file_size_bytes` | `INTEGER` | no | — | `CHECK > 0` |
| `gcs_bucket` | `VARCHAR(255)` | no | — | — |
| `gcs_object_path` | `VARCHAR(1000)` | no | — | — |
| `content_text` | `TEXT` | yes | — | Extracted text (populated by future worker) |
| `extraction_status` | `VARCHAR(50)` | no | `'pending'` | Enum values below |
| `attachment_type` | `VARCHAR(50)` | no | — | Enum values below |
| `source_system` | `VARCHAR(100)` | yes | — | notion, confluence, datadog, etc. |
| `source_url` | `VARCHAR(2048)` | yes | — | Original URL |
| `created_at` | `TIMESTAMPTZ` | no | `now()` | — |
| `updated_at` | `TIMESTAMPTZ` | no | `now()` | — |

**Constraints**: `CHECK (file_size_bytes > 0)`

**Indexes**: `(incident_id)`

**`extraction_status` valid values**: `pending` | `processing` | `completed` | `failed`  
**`attachment_type` valid values**: `postmortem_doc` | `log_file` | `screenshot` | `monitoring_export` | `runbook` | `config_snapshot` | `slack_export` | `jira_export`

---

## New Python Enums (in `domain/models.py`)

```python
class PostmortemStatus(StrEnum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"

class TimelineEventType(StrEnum):
    DETECTED = "detected"
    ESCALATED = "escalated"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    REVIEWED = "reviewed"
    POSTMORTEM_PUBLISHED = "postmortem_published"

class DetectionMethod(StrEnum):
    MONITORING_ALERT = "monitoring_alert"
    CUSTOMER_REPORT = "customer_report"
    INTERNAL_TEST = "internal_test"
    AUTOMATED_SCAN = "automated_scan"
    MANUAL_DISCOVERY = "manual_discovery"
    EXTERNAL_REPORT = "external_report"

class ResponderRole(StrEnum):
    INCIDENT_COMMANDER = "incident_commander"
    TECHNICAL_LEAD = "technical_lead"
    COMMUNICATION_LEAD = "communication_lead"
    REMEDIATION_LEAD = "remediation_lead"
    RESPONDER = "responder"
    POSTMORTEM_LEAD = "postmortem_lead"

class ActionItemStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ActionItemPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AttachmentExtractionStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AttachmentType(StrEnum):
    POSTMORTEM_DOC = "postmortem_doc"
    LOG_FILE = "log_file"
    SCREENSHOT = "screenshot"
    MONITORING_EXPORT = "monitoring_export"
    RUNBOOK = "runbook"
    CONFIG_SNAPSHOT = "config_snapshot"
    SLACK_EXPORT = "slack_export"
    JIRA_EXPORT = "jira_export"
```

---

## Entity Relationships

```
incidents (existing)
├── incident_timeline_events  (1:N, CASCADE DELETE)
├── incident_responders       (1:N, CASCADE DELETE, UNIQUE per user)
├── incident_action_items     (1:N, CASCADE DELETE)
└── incident_attachments      (1:N, CASCADE DELETE)
```

All new tables reference `incidents.id` with `ON DELETE CASCADE`. No cross-references between the four new tables.

---

## Backward Compatibility

- The existing `date` column on `incidents` is preserved as-is (nullable `DATE`).
- All new columns on `incidents` are either nullable or have `server_default`.
- No existing columns are renamed, dropped, or made non-nullable.
- No existing indexes or constraints are modified.
- The `001` migration remains unchanged.
