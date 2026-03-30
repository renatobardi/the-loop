# Data Model: Landing Page & Waitlist

**Date**: 2026-03-30
**Feature**: 001-landing-page-waitlist

## Entities

### WaitlistEntry

**Storage**: Firestore collection `waitlist`
**Document ID**: Email address (lowercased) — enforces uniqueness at database level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | Email address, lowercased, max 254 chars. Also used as document ID. |
| `locale` | string | Yes | Language at time of signup. One of: `en`, `pt`, `es`. |
| `created_at` | timestamp | Yes | Server timestamp (`FieldValue.serverTimestamp()`). |
| `source` | string | Yes | Origin of signup. Fixed value: `"landing"` for Phase 0. |

**Validation rules** (enforced by Zod on server):
- `email`: valid email format, trimmed, lowercased, max 254 chars
- `locale`: must be one of `["en", "pt", "es"]`
- `source`: must be `"landing"`
- `created_at`: set by server, not user input

**Firestore Security Rules** (defense against direct client SDK access):
- `allow create`: field validation (email string, locale in allowed values, source == "landing", created_at is timestamp, email matches document ID)
- `allow read`: denied (`if false`)
- `allow update, delete`: denied (`if false`)

**Indexes**: No custom indexes needed. Document ID (email) provides direct lookups.

## State Transitions

WaitlistEntry has no state transitions — it is immutable once created. No updates or deletes from the application layer.

## Relationships

No relationships. WaitlistEntry is a standalone entity in Phase 0.

## Query Patterns

| Query | Purpose | Frequency |
|-------|---------|-----------|
| `doc(email).get()` | Duplicate detection before insert | Every form submission |
| `doc(email).set()` | Create new waitlist entry | Every successful submission |
| Collection count (admin) | Track total signups for SC-001 metric | Manual / occasional |
