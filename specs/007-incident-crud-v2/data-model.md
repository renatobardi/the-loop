# Data Model: Incident Module — CRUD (Phase A, Revised)

**Branch**: `007-incident-crud-v2` | **Date**: 2026-03-31
**Carried from**: `006-incident-crud/data-model.md` — domain model unchanged.

## Entities

### Incident

The core entity. Immutable Pydantic model (frozen=True) in the domain layer.

| Field                 | Type                  | Required  | Constraints                                                         |
| --------------------- | --------------------- | --------- | ------------------------------------------------------------------- |
| id                    | UUID                  | Auto      | Primary key, generated server-side (uuid4)                          |
| title                 | string                | Yes       | 1-500 chars                                                         |
| date                  | date                  | No        | Nullable, date of the original incident                             |
| source_url            | string                | No        | Max 2048 chars, UNIQUE across non-deleted incidents, nullable       |
| organization          | string                | No        | Max 255 chars, nullable                                             |
| category              | Category (enum)       | Yes       | One of 12 fixed values                                              |
| subcategory           | string                | No        | Max 100 chars, nullable                                             |
| failure_mode          | string                | No        | Nullable, free text                                                 |
| severity              | Severity (enum)       | Yes       | One of 4 fixed values                                               |
| affected_languages    | list[string]          | No        | Default [], stored as JSONB array                                   |
| anti_pattern          | string                | Yes       | Min 1 char, no max                                                  |
| code_example          | string                | No        | Nullable, free text (code block)                                    |
| remediation           | string                | Yes       | Min 1 char, no max                                                  |
| static_rule_possible  | boolean               | No        | Default false                                                       |
| semgrep_rule_id       | string                | No        | Max 50 chars, format: `{category}-{NNN}`, nullable                  |
| embedding             | vector(768)           | No        | Always NULL in Phase A, pgvector type                               |
| tags                  | list[string]          | No        | Default [], stored as JSONB array                                   |
| version               | integer               | Auto      | >= 1, default 1, incremented atomically on update                   |
| deleted_at            | datetime (UTC)        | No        | Nullable, set on soft-delete                                        |
| created_at            | datetime (UTC)        | Auto      | Set on creation, immutable                                          |
| updated_at            | datetime (UTC)        | Auto      | Set on creation, updated on every modification                      |
| created_by            | UUID                  | Yes       | Firebase Auth UID, extracted from session (never user-supplied)      |

### Category (enum)

```
unsafe-regex
injection
deployment-error
missing-safety-check
race-condition
unsafe-api-usage
resource-exhaustion
data-consistency
missing-error-handling
cascading-failure
authentication-bypass
configuration-drift
```

### Severity (enum)

```
critical
high
medium
low
```

## Relationships

Phase A is single-entity — no foreign keys to other domain tables.

- `created_by` references a Firebase Auth UID (external system, not a local table).
- `semgrep_rule_id` is a soft reference (string format only, no FK). The linked rule lives in a future module.

## Indexes

| Index                        | Columns                          | Type          | Purpose                                    |
| ---------------------------- | -------------------------------- | ------------- | ------------------------------------------ |
| pk_incidents                 | id                               | PRIMARY KEY   | Row identity                               |
| ix_incidents_created_at      | created_at DESC                  | B-tree        | Default list ordering                      |
| ix_incidents_category        | category                         | B-tree        | Filter by category                         |
| ix_incidents_severity        | severity                         | B-tree        | Filter by severity                         |
| uq_incidents_source_url      | source_url                       | UNIQUE partial | WHERE deleted_at IS NULL AND source_url IS NOT NULL |
| ix_incidents_keyword_search  | title, anti_pattern, remediation | GIN (trigram) | ILIKE keyword search performance           |

**Note**: The embedding column has no index in Phase A. HNSW index deferred to Phase C.

## Validation Rules

### Create

- `title`: 1-500 chars, trimmed whitespace
- `category`: must be one of 12 enum values
- `severity`: must be one of 4 enum values
- `anti_pattern`: min 1 char after trim
- `remediation`: min 1 char after trim
- `source_url`: if provided, max 2048 chars, valid URL format, unique across non-deleted records
- `semgrep_rule_id`: if provided, must match `^{category}-\d{3}$` where `{category}` matches the incident's own category value
- `affected_languages`: each element must be a non-empty string
- `tags`: each element must be a non-empty string
- `embedding`: must be NULL in Phase A (rejected if provided)
- `created_by`: extracted from auth context, never accepted in request body

### Update

- Same field validations as Create
- `version` (required): must match current DB version, else 409 Conflict
- `category`: blocked if `semgrep_rule_id` is non-null (409 Conflict)
- `id`, `created_at`, `created_by`: immutable — rejected if included in update payload

### Soft-Delete

- Blocked if `semgrep_rule_id` is non-null (409 Conflict)
- Idempotent: re-deleting already-deleted record is a no-op (200 OK)

## State Transitions

```
              create
    ∅ ──────────────────► ACTIVE
                            │
                   update   │   soft-delete
                   (loop)   │   (if no semgrep_rule_id)
                     ◄──────┤──────────────► DELETED
                            │
                            │   category change
                            │   blocked if semgrep_rule_id set
```

States:
- **ACTIVE**: `deleted_at IS NULL` — visible in list and detail
- **DELETED**: `deleted_at IS NOT NULL` — excluded from list and detail, still in DB

## Domain Exceptions

| Exception                      | Trigger                                           | HTTP Status |
| ------------------------------ | ------------------------------------------------- | ----------- |
| `IncidentNotFoundError`        | GET/PUT/DELETE on non-existent or deleted ID       | 404         |
| `DuplicateSourceUrlError`      | Create/Update with source_url that already exists  | 409         |
| `OptimisticLockError`          | Update with stale version number                   | 409         |
| `IncidentHasActiveRuleError`   | Soft-delete or category change when semgrep_rule_id set | 409   |
| `ValidationError`              | Field validation failure (Pydantic)                | 422         |
