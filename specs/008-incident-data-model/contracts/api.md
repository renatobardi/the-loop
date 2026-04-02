# API Contract: Incident Data Model — Production-Ready Schema

**Feature**: 008-incident-data-model  
**Date**: 2026-04-01  
**Base URL**: `/api/v1`  
**Auth**: Firebase Bearer token required on all endpoints

---

## Changes to Existing Endpoints

### `POST /api/v1/incidents` — Updated Request Body

All new fields are optional. Existing callers require no changes.

**New optional fields in request body**:

```json
{
  "started_at": "2026-03-15T14:00:00Z",
  "detected_at": "2026-03-15T14:05:00Z",
  "ended_at": "2026-03-15T15:30:00Z",
  "resolved_at": "2026-03-15T16:00:00Z",
  "impact_summary": "Payment processing unavailable for 1.5 hours",
  "customers_affected": 4200,
  "sla_breached": true,
  "slo_breached": true,
  "postmortem_status": "draft",
  "postmortem_due_date": "2026-03-22",
  "lessons_learned": "We lacked alerting on queue depth",
  "why_we_were_surprised": "Queue depth had never hit this threshold before",
  "detection_method": "monitoring_alert",
  "slack_channel_id": "C08EXAMPLE",
  "external_tracking_id": "JIRA:SEC-1234",
  "incident_lead_id": "uuid-of-firebase-user",
  "raw_content": {
    "summary": "...",
    "root_cause": "..."
  },
  "tech_context": {
    "languages": ["python"],
    "infrastructure": ["gcp", "postgres"]
  }
}
```

### `PUT /api/v1/incidents/{id}` — Updated Request Body

Same new optional fields as `POST`. Existing `version` field requirement unchanged.

### `GET /api/v1/incidents` and `GET /api/v1/incidents/{id}` — Updated Response

New fields added to the existing `IncidentResponse` schema:

```json
{
  "id": "uuid",
  "title": "...",
  "...existing fields...",

  "started_at": "2026-03-15T14:00:00Z",
  "detected_at": "2026-03-15T14:05:00Z",
  "ended_at": "2026-03-15T15:30:00Z",
  "resolved_at": "2026-03-15T16:00:00Z",
  "duration_minutes": 90,
  "time_to_detect_minutes": 5,
  "time_to_resolve_minutes": 120,

  "impact_summary": "Payment processing unavailable for 1.5 hours",
  "customers_affected": 4200,
  "sla_breached": true,
  "slo_breached": true,
  "postmortem_status": "draft",
  "postmortem_published_at": null,
  "postmortem_due_date": "2026-03-22",
  "lessons_learned": null,
  "why_we_were_surprised": null,
  "detection_method": "monitoring_alert",
  "slack_channel_id": null,
  "external_tracking_id": "JIRA:SEC-1234",
  "incident_lead_id": null,
  "raw_content": null,
  "tech_context": null
}
```

---

## New Endpoints: Timeline Events

### `POST /api/v1/incidents/{incident_id}/timeline`

Create a timeline event.

**Request**:
```json
{
  "event_type": "detected",
  "description": "Alert fired in Datadog for queue depth > 10k",
  "occurred_at": "2026-03-15T14:05:00Z",
  "recorded_by": "uuid-of-firebase-user",
  "duration_minutes": null,
  "external_reference_url": "https://app.datadoghq.com/monitors/123"
}
```

**Response** `201`:
```json
{
  "id": "uuid",
  "incident_id": "uuid",
  "event_type": "detected",
  "description": "Alert fired in Datadog for queue depth > 10k",
  "occurred_at": "2026-03-15T14:05:00Z",
  "recorded_by": "uuid",
  "duration_minutes": null,
  "external_reference_url": "https://...",
  "created_at": "...",
  "updated_at": "..."
}
```

**Errors**: `404` (incident not found), `422` (invalid event_type)

### `GET /api/v1/incidents/{incident_id}/timeline`

List all timeline events for an incident, ordered by `occurred_at` ascending.

**Response** `200`:
```json
{
  "items": [...],
  "total": 4
}
```

**Errors**: `404` (incident not found)

### `DELETE /api/v1/incidents/{incident_id}/timeline/{event_id}`

Delete a timeline event.

**Response**: `200` `{"detail": "Timeline event deleted", "id": "uuid"}`  
**Errors**: `404`

---

## New Endpoints: Responders

### `POST /api/v1/incidents/{incident_id}/responders`

Add a responder to an incident.

**Request**:
```json
{
  "user_id": "uuid-of-firebase-user",
  "role": "technical_lead",
  "joined_at": "2026-03-15T14:10:00Z",
  "contribution_summary": null
}
```

**Response** `201`: Full responder object  
**Errors**: `404` (incident not found), `409` (user already a responder), `422` (invalid role)

### `GET /api/v1/incidents/{incident_id}/responders`

List all responders for an incident.

**Errors**: `404` (incident not found)

### `PUT /api/v1/incidents/{incident_id}/responders/{responder_id}`

Update responder (e.g., set `left_at` or update `contribution_summary`).

**Request**:
```json
{
  "left_at": "2026-03-15T16:00:00Z",
  "contribution_summary": "Led database recovery"
}
```

### `DELETE /api/v1/incidents/{incident_id}/responders/{responder_id}`

Remove a responder.

---

## New Endpoints: Action Items

### `POST /api/v1/incidents/{incident_id}/action-items`

Create a follow-up action item.

**Request**:
```json
{
  "title": "Add queue depth alert with 5k threshold",
  "description": "Configure Datadog monitor...",
  "owner_id": "uuid-of-firebase-user",
  "priority": "high",
  "due_date": "2026-04-01"
}
```

**Response** `201`: Full action item object with `status: "open"` default  
**Errors**: `404`, `422`

### `GET /api/v1/incidents/{incident_id}/action-items`

List all action items. Optional query params: `?status=open&priority=high`

**Errors**: `404` (incident not found)

### `PUT /api/v1/incidents/{incident_id}/action-items/{item_id}`

Update an action item (title, description, owner, priority, status, due_date).

**Completing an item** — set `status: "completed"` and the system records `completed_at` automatically.

### `DELETE /api/v1/incidents/{incident_id}/action-items/{item_id}`

Delete an action item.

---

## New Endpoints: Attachments

### `POST /api/v1/incidents/{incident_id}/attachments`

Register an attachment (metadata only — actual file upload to GCS is handled client-side via signed URL, out of scope for this spec).

**Request**:
```json
{
  "filename": "postmortem-2026-03-15.pdf",
  "mime_type": "application/pdf",
  "file_size_bytes": 204800,
  "gcs_bucket": "loop-prod-attachments",
  "gcs_object_path": "incidents/uuid/postmortem-2026-03-15.pdf",
  "attachment_type": "postmortem_doc",
  "source_system": null,
  "source_url": null
}
```

**Response** `201`: Full attachment object with `extraction_status: "pending"`  
**Errors**: `404`, `422` (invalid type, zero/negative file size)

### `GET /api/v1/incidents/{incident_id}/attachments`

List all attachments for an incident.

**Errors**: `404` (incident not found)

### `DELETE /api/v1/incidents/{incident_id}/attachments/{attachment_id}`

Delete an attachment record (does NOT delete the GCS object — that is the caller's responsibility).

---

## Rate Limiting

All new endpoints: `60/minute` per authenticated user (consistent with existing endpoints).

---

## Error Format (unchanged)

```json
{ "detail": "Human-readable error message" }
```

For conflict errors:
```json
{ "detail": "User is already a responder for this incident", "user_id": "uuid" }
```
