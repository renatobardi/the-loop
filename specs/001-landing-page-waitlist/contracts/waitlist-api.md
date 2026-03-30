# Contract: Waitlist Form Action

**Date**: 2026-03-30
**Feature**: 001-landing-page-waitlist
**Type**: SvelteKit Form Action (server-side)

## Endpoint

**Action**: `?/waitlist` (SvelteKit named action)
**Method**: POST
**Route**: `/[lang]/` (e.g., `/en/`, `/pt/`, `/es/`)
**Progressive enhancement**: Works without JavaScript via standard form POST

## Request

### Form Data

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | User's email address |

**Note**: `locale` is auto-detected from the route `[lang]` param, not submitted by the user.

### Headers

Standard browser form submission headers. No custom headers required.

## Responses

### Success (HTTP 200)

```typescript
{ success: true }
```

Displayed to user as: confirmation message ("You're on the list!" or localized equivalent).

### Validation Error (HTTP 400)

```typescript
{ error: string }
```

Possible error values:
- `"Please enter a valid email address"` — invalid email format
- `"Email is required"` — empty email field
- `"Email address is too long"` — exceeds 254 characters

Displayed to user as: inline validation error below the input field.

### Duplicate (HTTP 409)

```typescript
{ error: "already_registered" }
```

Displayed to user as: friendly message ("You're already on the list!" or localized equivalent).

### Rate Limited (HTTP 429)

```typescript
{ error: "rate_limited" }
```

Limit: 5 submissions per IP per 60 seconds.
Displayed to user as: "Too many attempts. Please try again in a minute."

### Server Error (HTTP 500)

```typescript
{ error: "server_error" }
```

Displayed to user as: "Something went wrong. Please try again."

## Data Flow

```
Browser POST → SvelteKit form action → Zod validation → Rate limit check
  → Firestore duplicate check → Firestore write → Response
```

1. User submits form (with or without JS)
2. SvelteKit form action receives FormData
3. Zod validates and transforms email (trim, lowercase, format check)
4. Rate limiter checks IP (5/min)
5. Firestore: check if document with email ID exists
6. If not exists: create document with email, locale, timestamp, source
7. Return success/error response

## Security

- CSRF: SvelteKit `checkOrigin: true` (same-origin enforcement)
- Validation: server-side Zod — never trust client input
- Rate limiting: per-IP, in-memory (Phase 0)
- Firestore: Admin SDK (bypasses security rules); rules protect against direct client access
- No secrets in response: error messages are generic, no stack traces
