# Research: Waitlist Source Tracking + Pricing CTAs

**Branch**: `004-waitlist-pricing-ctas` | **Date**: 2026-03-30

## Codebase Analysis

### Existing Implementation Status

Most requirements from the spec are already implemented. A full codebase audit identified the following:

| Requirement | File | Status | Action |
|-------------|------|--------|--------|
| Hero waitlist form | `Hero.svelte` (line 39) | Exists | Pass `source="hero"` |
| Section 7 waitlist form | `WaitlistCta.svelte` (line 18) | Exists | Pass `source="cta-bottom"` |
| WaitlistForm component | `WaitlistForm.svelte` | Exists | Add `source` prop + hidden input |
| Pricing card CTAs (Free/PAYG → #waitlist) | `Pricing.svelte` | Exists | Verify only |
| "Most popular" badge on PAYG | `Pricing.svelte` | Exists | Verify only |
| Enterprise "Contact us" CTA | `Pricing.svelte` | Exists | Verify only |
| Button variants (primary/secondary) | `Pricing.svelte` | Exists | Verify only |
| i18n: `pricing_join_waitlist` | `en/pt/es.json` | Exists | Verify only |
| i18n: `pricing_popular_badge` | `en/pt/es.json` | Exists | Verify only |
| i18n: `pricing_contact_cta` | `en/pt/es.json` | Exists | Verify only |
| i18n: `form_email_label` (sr-only) | `en/pt/es.json` | Exists | Verify only |
| i18n: `form_success`, `form_duplicate`, etc. | `en/pt/es.json` | Exists | Verify only |
| Input sr-only label support | `Input.svelte` (line 35) | Exists | Verify only |
| Zod email validation | `schemas.ts` | Exists | Extend with source field |
| Rate limiting (5/60s/IP) | `rateLimiter.ts` | Exists | No change |
| Duplicate detection | `waitlist.ts` (line 11) | Exists | No change |
| Firestore source field | `waitlist.ts` (line 19) | **Hardcoded to `'landing'`** | Make dynamic |
| Server action source extraction | `+page.server.ts` (line 21) | **Missing** | Add source extraction |

### Source Tracking Gap

**Decision**: Thread `source` as a prop through the component chain and as a hidden form field.

**Rationale**: The simplest approach that doesn't require JavaScript-only solutions. A hidden `<input name="source" value={source}>` works with progressive enhancement — no JS needed for the source to reach the server.

**Alternatives considered**:
- URL query parameter (`?source=hero`) — rejected: pollutes URL, not form-native
- JavaScript-only approach (set source in `use:enhance`) — rejected: breaks progressive enhancement
- Separate server actions per form — rejected: unnecessary duplication

### Source Validation

**Decision**: Validate source against an allowlist (`VALID_SOURCES = ['hero', 'cta-bottom']`) in the Zod schema. Invalid values default to `"unknown"`.

**Rationale**: Server must not trust client input (Constitution VIII — input validation). Using Zod `.transform()` with a fallback keeps the schema as the single source of truth for validation.

**Alternatives considered**:
- Enum validation that rejects invalid values — rejected: would cause form submission to fail for tampering, which is a worse UX than silently recording "unknown"
- No validation — rejected: violates Constitution VIII

### Smooth Scroll Behavior

**Decision**: Rely on existing `scroll-behavior: smooth` CSS or native browser behavior via `href="#waitlist"` anchor links.

**Rationale**: Already working in production — pricing card CTAs already use `href="#waitlist"` and scroll works. No JavaScript scroll library needed.
