# Research: Public Constitution Page

**Branch**: `005-constitution-page` | **Date**: 2026-03-31

## R1: Localized URL Slugs via Paraglide Pathnames

**Decision**: Use Paraglide-SvelteKit's built-in `pathnames` config in `createI18n()`.

**Rationale**: The installed version (`@inlang/paraglide-sveltekit@0.16.1`) supports a `pathnames` option that maps canonical SvelteKit route paths to locale-specific slugs. The existing `reroute` hook in `src/hooks.ts` already calls `i18n.reroute()`, which handles pathname translation automatically. No new dependencies or route structure changes needed.

**How it works**:
- Define a single canonical route at `src/routes/constitution/`
- Add pathnames config to `src/lib/i18n.ts`:
  ```typescript
  pathnames: {
    "/constitution": {
      en: "/constitution",
      pt: "/constituicao",
      es: "/constitucion"
    }
  }
  ```
- The reroute hook transparently maps `/pt/constituicao/` → canonical `/constitution` route
- Paraglide translates `<a href="/constitution">` links to the correct locale slug automatically

**Alternatives considered**:
- Dynamic `[slug]` route with manual locale-slug mapping: More complex, requires custom logic for each route, doesn't integrate with Paraglide's link translation.
- Three separate route directories (`constitution/`, `constituicao/`, `constitucion/`): Extreme duplication, impossible to maintain.

## R2: Waitlist Form Action on Constitution Route

**Decision**: Create a `+page.server.ts` in the Constitution route that replicates the waitlist form action from the landing page.

**Rationale**: SvelteKit form actions are route-scoped. The existing waitlist action lives in `src/routes/+page.server.ts`. The Constitution page needs its own `+page.server.ts` with the same `waitlist` action. The server-side logic (rate limiting, Zod validation, Firestore write) is already extracted into `$lib/server/` modules, so the Constitution route's action is just re-wiring the same imports.

**Alternatives considered**:
- Posting the form to the landing page's action via `action="/?/waitlist"`: Would redirect to the landing page on non-JS fallback, breaking the Constitution page experience.
- Extracting a shared action helper: Premature abstraction for 2 routes with identical logic. Can be refactored later if more pages need waitlist forms.

## R3: Per-Page Meta Tags

**Decision**: Override the root layout's `<title>` and `<meta>` tags from the Constitution page using `<svelte:head>`.

**Rationale**: The root `+layout.svelte` sets `meta_title()` and `meta_description()` as defaults. SvelteKit's `<svelte:head>` in child routes overrides parent head elements with the same tag. The Constitution page will import its own `constitution_meta_title()` and `constitution_meta_description()` messages and render them in `<svelte:head>`, which overrides the layout defaults. OG tags and hreflang also need per-page overrides.

**Alternatives considered**:
- Passing meta data via `+page.ts` load function: Adds unnecessary complexity for static i18n strings that are already available client-side.

## R4: hreflang for Localized Pathnames

**Decision**: Add per-page hreflang `<link>` tags in the Constitution page's `<svelte:head>`, using `i18n.resolveRoute()` to generate correct locale-specific URLs.

**Rationale**: The root layout only has `x-default` hreflang pointing to `/en/`. The Constitution page needs all 4 hreflang alternates (en, pt, es, x-default) pointing to the correct locale-specific slugs. Using `i18n.resolveRoute("/constitution", locale)` ensures the URLs match the pathnames config.

**Alternatives considered**:
- Paraglide's built-in `AlternateLinks` component: Exists in the library but the root layout doesn't use it currently. Adding it globally would be a separate improvement; for now, manual hreflang in the Constitution page keeps the change scoped.

## R5: Footer Constitution Link

**Decision**: The Footer already uses `<a href="/constitution">` which Paraglide auto-translates via the ParaglideJS wrapper.

**Rationale**: The `ParaglideJS` component in `+layout.svelte` wraps the entire app and translates all `<a href>` attributes. Since the footer link already points to `/constitution` (not a GitHub URL), and we're adding `/constitution` to the `pathnames` config, Paraglide will automatically translate this link to the correct locale slug. No changes needed to Footer.svelte.

**Note**: The Footer currently has an `eslint-disable svelte/no-navigation-without-resolve` comment covering the Constitution link. Once pathnames are configured, the Constitution link will be properly resolved by Paraglide, but the eslint comment covers the GitHub and mailto links that remain external. No change needed.
