# Data Model: Waitlist Source Tracking

**Branch**: `004-waitlist-pricing-ctas` | **Date**: 2026-03-30

## Entities

### Waitlist Entry (Firestore: `waitlist/{email}`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | User's email, lowercase, trimmed. Document ID. |
| `locale` | string | Yes | Detected from route: `"en"`, `"pt"`, `"es"` |
| `source` | string | Yes | Which CTA originated the signup: `"hero"`, `"cta-bottom"`, or `"unknown"` |
| `created_at` | timestamp | Yes | Firestore server timestamp |

**Identity**: Email is the unique identifier (used as document ID).

**Lifecycle**: Write-once. Once created, the document is never updated — duplicate submissions return `'duplicate'` without modifying the existing record.

### Changes from Current Model

| Field | Before | After |
|-------|--------|-------|
| `source` | Hardcoded `"landing"` | Dynamic: `"hero"` \| `"cta-bottom"` \| `"unknown"` |

All other fields remain unchanged.

## Validation Rules

### WaitlistSchema (Zod)

| Field | Rule | Error behavior |
|-------|------|----------------|
| `email` | `string().trim().toLowerCase().email().max(254)` | Return 400 with error message |
| `source` | `string().optional()`, transformed: if value is in `VALID_SOURCES`, keep it; otherwise default to `"unknown"` | Never fails — invalid values silently become `"unknown"` |

**VALID_SOURCES**: `["hero", "cta-bottom"]` — named constant, not magic strings.
