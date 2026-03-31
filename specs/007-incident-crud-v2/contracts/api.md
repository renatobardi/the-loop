# API Contract: Incident Module — CRUD (Phase A)

**Branch**: `007-incident-crud-v2` | **Date**: 2026-03-31
**Carried from**: `006-incident-crud/contracts/api.md` — API contract unchanged.
**Base path**: `/api/v1`

## Authentication

All endpoints require a valid Firebase Auth token in the `Authorization: Bearer <token>` header. Unauthenticated requests receive `401 Unauthorized`.

## Rate Limiting

60 requests per minute per authenticated user. Exceeded requests receive `429 Too Many Requests` with `Retry-After` header.

---

## Endpoints

### POST /api/v1/incidents

Create a new incident.

**Request body** (JSON):

```json
{
  "title": "ReDoS in email validation regex",
  "date": "2025-11-15",
  "source_url": "https://example.com/postmortem/123",
  "organization": "Acme Corp",
  "category": "unsafe-regex",
  "subcategory": "backtracking",
  "failure_mode": "Catastrophic backtracking on crafted input",
  "severity": "high",
  "affected_languages": ["python", "javascript"],
  "anti_pattern": "Using unbounded repetition in email regex without possessive quantifiers",
  "code_example": "re.match(r'^(a+)+$', user_input)",
  "remediation": "Use possessive quantifiers or atomic groups. Set re2 as the regex engine.",
  "static_rule_possible": true,
  "semgrep_rule_id": "unsafe-regex-001",
  "tags": ["regex", "performance", "dos"]
}
```

**Required fields**: `title`, `category`, `severity`, `anti_pattern`, `remediation`

**Response** `201 Created`:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "ReDoS in email validation regex",
  "date": "2025-11-15",
  "source_url": "https://example.com/postmortem/123",
  "organization": "Acme Corp",
  "category": "unsafe-regex",
  "subcategory": "backtracking",
  "failure_mode": "Catastrophic backtracking on crafted input",
  "severity": "high",
  "affected_languages": ["python", "javascript"],
  "anti_pattern": "Using unbounded repetition in email regex without possessive quantifiers",
  "code_example": "re.match(r'^(a+)+$', user_input)",
  "remediation": "Use possessive quantifiers or atomic groups. Set re2 as the regex engine.",
  "static_rule_possible": true,
  "semgrep_rule_id": "unsafe-regex-001",
  "embedding": null,
  "tags": ["regex", "performance", "dos"],
  "version": 1,
  "deleted_at": null,
  "created_at": "2026-03-31T14:30:00Z",
  "updated_at": "2026-03-31T14:30:00Z",
  "created_by": "firebase-uid-abc123"
}
```

**Error responses**:
- `409 Conflict`: `{"detail": "source_url already exists", "source_url": "..."}`
- `422 Unprocessable Entity`: `{"detail": [{"field": "title", "message": "..."}]}`

---

### GET /api/v1/incidents

List incidents with filters and pagination.

**Query parameters**:

| Parameter | Type   | Default | Constraints      | Description                          |
| --------- | ------ | ------- | ---------------- | ------------------------------------ |
| page      | int    | 1       | >= 1             | Page number                          |
| per_page  | int    | 20      | 1-100            | Items per page                       |
| category  | string | —       | Valid enum value  | Filter by category                   |
| severity  | string | —       | Valid enum value  | Filter by severity                   |
| q         | string | —       | —                | Keyword search (title, anti_pattern, remediation) |

**Response** `200 OK`:

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "ReDoS in email validation regex",
      "category": "unsafe-regex",
      "severity": "high",
      "organization": "Acme Corp",
      "tags": ["regex", "performance", "dos"],
      "created_at": "2026-03-31T14:30:00Z",
      "updated_at": "2026-03-31T14:30:00Z",
      "version": 1
    }
  ],
  "total": 142,
  "page": 1,
  "per_page": 20
}
```

**Note**: List items return a subset of fields for performance. Full details via GET by ID.

---

### GET /api/v1/incidents/{id}

Get a single incident by ID.

**Response** `200 OK`: Full incident object (same shape as POST response).

**Error responses**:
- `404 Not Found`: `{"detail": "Incident not found"}` (also returned for soft-deleted incidents)

---

### PUT /api/v1/incidents/{id}

Update an incident. Requires `version` for optimistic locking.

**Request body** (JSON): Same fields as POST, plus required `version`. Fields `id`, `created_at`, `created_by` are ignored if sent.

```json
{
  "title": "Updated title",
  "category": "unsafe-regex",
  "severity": "critical",
  "anti_pattern": "...",
  "remediation": "...",
  "version": 1
}
```

**Response** `200 OK`: Full updated incident object with `version` incremented.

**Error responses**:
- `404 Not Found`: Incident doesn't exist or is soft-deleted
- `409 Conflict`: Version mismatch — `{"detail": "Incident was modified by another process", "current_version": 2}`
- `409 Conflict`: Category change blocked — `{"detail": "Cannot change category while semgrep_rule_id is set"}`
- `409 Conflict`: Duplicate source_url — `{"detail": "source_url already exists", "source_url": "..."}`
- `422 Unprocessable Entity`: Validation errors

---

### DELETE /api/v1/incidents/{id}

Soft-delete an incident.

**Response** `200 OK`: `{"detail": "Incident deleted", "id": "..."}`

**Idempotent**: Deleting an already-deleted incident returns `200 OK`.

**Error responses**:
- `404 Not Found`: Incident doesn't exist
- `409 Conflict`: Active rule — `{"detail": "Cannot delete incident with active Semgrep rule", "semgrep_rule_id": "unsafe-regex-001"}`

---

## Common Error Format

All error responses follow this structure:

```json
{
  "detail": "Human-readable error message",
  "field": "optional — field name for validation errors",
  "current_version": "optional — for optimistic lock conflicts"
}
```

Validation errors (422) return an array:

```json
{
  "detail": [
    {"field": "title", "message": "Title must be between 1 and 500 characters"},
    {"field": "category", "message": "Invalid category: 'foo'"}
  ]
}
```

## HTTP Status Code Summary

| Status | Meaning                          |
| ------ | -------------------------------- |
| 200    | Success (read, update, delete)   |
| 201    | Created (new incident)           |
| 401    | Unauthenticated                  |
| 404    | Not found (or soft-deleted)      |
| 409    | Conflict (version, rule, URL)    |
| 422    | Validation error                 |
| 429    | Rate limited                     |
| 500    | Internal server error            |
