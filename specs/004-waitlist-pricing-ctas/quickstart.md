# Quickstart: Waitlist Source Tracking

**Branch**: `004-waitlist-pricing-ctas` | **Date**: 2026-03-30

## Setup

```bash
cd apps/web
npm install
npm run dev
```

Open http://localhost:5173/en/

## What to Change (5 files)

### 1. `src/lib/server/schemas.ts` — Add source to Zod schema

Add `VALID_SOURCES` constant and extend `WaitlistSchema` with an optional `source` field that defaults to `"unknown"` for invalid values.

### 2. `src/lib/server/waitlist.ts` — Accept source parameter

Change `addToWaitlist(email, locale)` signature to `addToWaitlist(email, locale, source)` and use the parameter instead of the hardcoded `'landing'`.

### 3. `src/routes/+page.server.ts` — Extract source from form data

Add `source: data.get('source')` to the raw object parsed from form data. Pass `result.data.source` to `addToWaitlist()`.

### 4. `src/lib/components/WaitlistForm.svelte` — Add source prop + hidden input

Add a `source` prop (default: `"unknown"`) and render `<input type="hidden" name="source" value={source} />` inside the form.

### 5. `src/lib/components/Hero.svelte` + `WaitlistCta.svelte` — Pass source prop

- `Hero.svelte`: `<WaitlistForm source="hero" />`
- `WaitlistCta.svelte`: `<WaitlistForm source="cta-bottom" />`

## Verification

```bash
npm run check      # TypeScript strict
npm run lint        # ESLint + Prettier
npm run test -- --run  # Unit tests
npm run build       # Production build
```

### Manual Testing

1. Open `/en/` → submit email in Hero form → check Firestore for `source: "hero"`
2. Scroll to bottom → submit different email → check Firestore for `source: "cta-bottom"`
3. Submit same email again → verify "already on the list" message
4. Click "Join the waitlist" on Free pricing card → page scrolls to `#waitlist`
5. Switch to `/pt/` and `/es/` → verify all strings are translated
