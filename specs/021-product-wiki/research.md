# Research: Product Docs (Spec-021)

**Date**: 2026-04-06 (updated from 2026-04-05 to reflect role-based single-area architecture)

---

## Decision 1: Where does the docs live?

**Decision**: In-product at `/docs/` (SvelteKit routes).  
**Rationale**: Zero extra infrastructure. Same domain, same deployment. Deep links from in-app UI work natively. Consistent design system. Indexed by search engines for user sections.  
**Alternatives considered**: GitHub Wiki, Notion/Gitbook, separate docs site — all rejected (external deps, no design token compliance, extra infrastructure).

---

## Decision 2: Content rendering approach

**Decision**: Static SvelteKit `+page.svelte` components with inline content. No MDsveX.  
**Rationale**: No new dependencies. Follows the `/constitution/` precedent. Type-safe. Code examples use `<CodeBlock>` component styled with design tokens.  
**Alternatives considered**: MDsveX (adds compiler plugin, breaks type safety), GitHub API markdown fetch (external dep, fragile).

---

## Decision 3: Single `/docs/` area with role-based visibility

**Decision**: One URL prefix `/docs/` for all sections. Admin-only sections hidden from non-admin users via client-side auth check and server-side route group configuration.  
**Rationale**: Simpler URL structure. No second Navbar link needed. Admin content is non-sensitive documentation (not PII/secrets), so client-side gating is appropriate. Matches the existing pattern where `/analytics/` and other auth-required pages use `ssr = false` with client-side Firebase Auth.  
**Alternatives considered**: Separate `/docs/admin/` prefix — rejected because it adds URL complexity, requires a second Navbar link, and splits the docs experience unnecessarily.

---

## Decision 4: SvelteKit route group for admin sections

**Decision**: `routes/docs/(admin)/` route group with `+layout.ts` (`ssr = false`) and `+layout.svelte` (admin check + redirect).  
**Rationale**: Route groups encapsulate the `ssr = false` and admin redirect concern cleanly. Individual admin `+page.svelte` files contain only content — no auth boilerplate per page. The group layout handles the redirect before any child content renders.  
**Alternatives considered**: Per-page `ssr = false` + `$effect` auth check — more boilerplate, easier to forget on new pages. Server-side check in `+page.server.ts` — not viable because Firebase Auth is client-side only (no session cookie).

---

## Decision 5: Admin role check mechanism

**Decision**: Use the existing `lib/stores/auth.ts` user store. The admin flag is sourced from Firebase custom claims or a Firestore profile document — confirmed during implementation based on how the existing `require_admin` backend dependency works.  
**Rationale**: Reuses existing auth infrastructure. No new backend endpoint needed. The `(admin)` layout waits for auth to resolve before deciding to show content or redirect — prevents flash of content.  
**Alternatives considered**: New `GET /api/v1/me` endpoint — adds backend work for a frontend-only feature; rejected.

---

## Decision 6: Components directory name

**Decision**: `lib/components/docs/` (not `lib/components/wiki/`).  
**Rationale**: Matches the feature name "Product Docs". Consistent with the spec rename.  
**Alternatives considered**: `lib/components/wiki/` — outdated name, rejected.

---

## Decision 7: Sidebar filtering approach

**Decision**: The sidebar receives a pre-filtered `items: NavItem[]` prop. The layout passes only sections the current user is allowed to see. The sidebar is profile-agnostic.  
**Rationale**: Clean separation of concerns. Sidebar has no knowledge of auth state — easier to test.  
**Alternatives considered**: Sidebar reads auth store internally — couples component to auth.

---

## Decision 8: SSR strategy per section type

| Section type | SSR | Auth required | Reason |
|-------------|-----|---------------|--------|
| User sections (7) | ✅ Yes | No | Public content, SEO benefit, no Firebase Auth needed |
| Admin sections (3) | ❌ No (`ssr = false`) | Yes (admin role) | Firebase Auth is client-side only; same pattern as `/analytics/` |
| Home `/docs/` | ✅ Yes (static shell) | No | Static content SSR; admin section cards added reactively client-side after auth resolves |
