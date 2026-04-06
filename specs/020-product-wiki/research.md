# Research: Product Wiki (Spec-020)

**Date**: 2026-04-05

---

## Decision 1: Where does the wiki live?

**Decision**: In-product at `/docs/` (SvelteKit routes).  
**Rationale**: Zero extra infrastructure. Same domain, same deployment. Deep links from the app UI work natively. Consistent design system automatically. Indexed by search engines without extra config.  
**Alternatives considered**:
- GitHub Wiki — no design system, not linkable from in-app UI, separate auth context.
- Notion/Gitbook — external SaaS dependency, no design token compliance, data sovereignty concern.
- Separate docs site — additional Cloud Run service, DNS, CI pipeline (violates Mandamento XIII: all deps must be explicit and justified).

---

## Decision 2: Content rendering approach

**Decision**: Static SvelteKit `+page.svelte` components with content inline or as typed data objects. No MDsveX.  
**Rationale**: Project has no MDsveX — adding it introduces a new dep and a new build layer (violates the "no new deps without justification" principle). The constitution page (`/constitution/`) sets precedent: rich content as structured Svelte components, not markdown. Code examples use `<pre><code>` blocks styled with design tokens.  
**Alternatives considered**:
- MDsveX — allows writing docs in markdown but breaks type safety, adds a compiler plugin, and diverges from existing patterns.
- Fetching markdown from GitHub API at runtime — SSR complexity, external dependency, fragile.

---

## Decision 3: Navigation pattern

**Decision**: Left sidebar for section navigation + persona picker on the `/docs/` home page. No per-page persona filtering beyond the home.  
**Rationale**: The sidebar pattern is standard for documentation and does not require a new component — it can be built with the existing `Container`, `Section`, and `Card` components. The persona picker is a simple interactive grid of cards (no routing change, just state-based highlight of relevant links).  
**Alternatives considered**:
- Tabbed persona views for every page — over-engineering; most content is universal, only the entry point is persona-specific.
- Top navbar tabs — no room in the existing navbar which already has incidents/analytics/constitution.

---

## Decision 4: SSR vs CSR

**Decision**: SSR enabled (default SvelteKit behavior). No `ssr = false`.  
**Rationale**: Docs pages are fully static content — no Firebase Auth required. SSR gives better SEO and faster first paint. Opposite of `/analytics/` which needs auth.  
**Alternatives considered**: None — SSR is the default and the right choice for public content.

---

## Decision 5: New components needed

| Component | File | Purpose |
|-----------|------|---------|
| `WikiLayout.svelte` | `lib/components/wiki/WikiLayout.svelte` | Left sidebar + main content shell |
| `WikiSidebar.svelte` | `lib/components/wiki/WikiSidebar.svelte` | Section nav with active state |
| `PersonaPicker.svelte` | `lib/components/wiki/PersonaPicker.svelte` | 6-role card grid on `/docs/` home |
| `CodeBlock.svelte` | `lib/components/wiki/CodeBlock.svelte` | Styled `<pre><code>` with copy button |
| `DocSection.svelte` | `lib/components/wiki/DocSection.svelte` | Reusable heading + prose section |

All use existing design tokens only. No new CSS variables.

---

## Decision 6: Navbar integration

**Decision**: Add "Docs" link to the existing `Navbar.svelte` between "Analytics" and "Constitution".  
**Rationale**: Docs must be discoverable from every page. Navbar already has the pattern for nav links.  
**Risk**: Navbar is shared across the entire app — change must be tested across all routes.

---

## Decision 7: CI impact

**Decision**: The `docs-check` gate runs `scripts/generate-docs.sh` which generates API docs from route docstrings — this gate is **unaffected** by wiki pages (pure frontend, no new API routes).  
**Action**: No CI changes needed.
