# Tasks: Product Wiki (Spec-020)

**Branch**: `feat/020-product-wiki`  
**Total**: 38 tasks | 5 phases | ~4 days

Legend: `[ ]` pending · `[x]` done · `[~]` in progress

---

## Phase 0 — Foundation (day 1)

### Wiki layout & shared components

- [ ] **T001** — Create `apps/web/src/routes/docs/+layout.svelte` with two-column layout: `WikiSidebar` (left, 240px) + `<slot />` (right, flex-1). Use `Container` from `lib/ui`.
- [ ] **T002** — Create `apps/web/src/lib/components/wiki/WikiSidebar.svelte`. Props: `items: { label: string; href: string }[]`. Active link detected via `$page.url.pathname`. Uses `aria-label="Documentation"` nav + `aria-current="page"` on active item.
- [ ] **T003** — Create `apps/web/src/lib/components/wiki/DocSection.svelte`. Props: `title: string; id: string; children`. Renders `<section id={id}>` with `<h2>` and prose wrapper using `text-text` token.
- [ ] **T004** — Create `apps/web/src/lib/components/wiki/CodeBlock.svelte`. Props: `code: string; language?: string`. Renders `<pre><code>` with `bg-bg-elevated border-border` styling. Copy-to-clipboard button using `navigator.clipboard.writeText`, aria-label="Copy code".
- [ ] **T005** — Add "Docs" link to `apps/web/src/lib/components/Navbar.svelte` between Analytics and Constitution. Active state: `$page.url.pathname.startsWith('/docs/')`.
- [ ] **T006** — Create `apps/web/src/lib/components/wiki/PersonaPicker.svelte`. Props: `onselect: (persona: string) => void; selected: string | null`. Renders 6 `Card` components in a 2×3 grid. Personas: Developer, IT Manager, Operator, Support, QA, Security. Selected card gets `border-accent` ring.

### Sidebar navigation data

- [ ] **T007** — Define sidebar nav items as a typed constant in `apps/web/src/lib/components/wiki/nav.ts`:
  ```ts
  export const WIKI_NAV = [
    { label: 'Getting Started', href: '/docs/getting-started/' },
    { label: 'Incidents', href: '/docs/incidents/' },
    { label: 'Postmortems', href: '/docs/postmortems/' },
    { label: 'Analytics', href: '/docs/analytics/' },
    { label: 'Semgrep Integration', href: '/docs/semgrep/' },
    { label: 'API Keys', href: '/docs/api-keys/' },
    { label: 'Rules', href: '/docs/rules/' },
    { label: 'Administration', href: '/docs/administration/' },
    { label: 'Security', href: '/docs/security/' },
    { label: 'API Reference', href: '/docs/api-reference/' },
  ]
  ```

---

## Phase 1 — Home + Getting Started (day 1–2)

- [ ] **T008** — Create `/docs/+page.svelte` (home). Include `<svelte:head>` with title "The Loop — Documentation" and meta description. Render intro paragraph + `PersonaPicker`. Below picker, render feature index as 10 `Card` components in a 2×5 grid. When a persona is selected, apply `text-accent` highlight class to its relevant cards. No routing on persona select — purely visual.
- [ ] **T009** — Define persona→section mapping in `/docs/+page.svelte` (or co-located `persona-map.ts`):
  ```ts
  const PERSONA_SECTIONS: Record<string, string[]> = {
    developer:   ['/docs/semgrep/', '/docs/api-keys/', '/docs/rules/', '/docs/api-reference/'],
    'it-manager': ['/docs/getting-started/', '/docs/analytics/', '/docs/administration/'],
    operator:    ['/docs/incidents/', '/docs/postmortems/', '/docs/getting-started/'],
    support:     ['/docs/incidents/', '/docs/postmortems/'],
    qa:          ['/docs/semgrep/', '/docs/rules/'],
    security:    ['/docs/security/', '/docs/api-keys/', '/docs/rules/', '/docs/administration/'],
  }
  ```
- [ ] **T010** — Create `/docs/getting-started/+page.svelte`. Sections: Prerequisites, Create your first incident (step-by-step list), Navigate the dashboard, Invite your team. Uses `DocSection` + `CodeBlock` for any CLI/config snippets.

---

## Phase 2 — Core product docs (day 2)

- [ ] **T011** — Create `/docs/incidents/+page.svelte`. Sections: Incident lifecycle, Creating an incident (all fields explained), Status transitions, Responders, Action Items, Timeline events, Attachments, Closing checklist.
- [ ] **T012** — Create `/docs/postmortems/+page.svelte`. Sections: When to write one, Available templates (5-Whys, Fishbone, Timeline, Pre/Mortem, OODA, PDCA with one-line description each), Fields explained, Locking (irreversible — warn box), AI summary field.
- [ ] **T013** — Create `/docs/analytics/+page.svelte`. Sections: Dashboard overview, 8 KPI cards explained (total incidents, MTTD, MTTR, open count, by severity, by category, by team, rule hits), Filters (period/team/category/severity/status), PatternTimeline, SeverityTrend chart, Rule Effectiveness table.

---

## Phase 3 — Platform integration docs (day 3)

- [ ] **T014** — Create `/docs/semgrep/+page.svelte`. Sections: How rule distribution works, GitHub Actions workflow snippet (full YAML with CodeBlock), Version pinning (`THELOOP_RULES_VERSION`), Fallback behavior (`.semgrep/theloop-rules.yml.bak`), ERROR vs WARNING, Scan history logging, Local testing commands.
- [ ] **T015** — Create `/docs/api-keys/+page.svelte`. Sections: What an API key is (scope explanation), Creating via UI (steps), Using in CI (`Authorization: Bearer tlp_...`), Key format (`tlp_` prefix), Project whitelist (how rules are filtered), Rotating / revoking.
- [ ] **T016** — Create `/docs/rules/+page.svelte`. Sections: Rule versioning history (v0.1.0→v0.4.0, rule counts per version), Rule browser at `/rules/latest/`, Severity model (ERROR blocks merge, WARNING advisory), Languages covered (10 languages, 122 rules), How to request a new rule, Rule ID format.

---

## Phase 4 — Admin, Security, API Reference (day 3–4)

- [ ] **T017** — Create `/docs/administration/+page.svelte`. Sections: Team management, Rate limits (60 req/min analytics, 5 req/min waitlist), API base URL (`https://api.loop.oute.pro`), Environment info (single env = production), Firebase project (`theloopoute`).
- [ ] **T018** — Create `/docs/security/+page.svelte`. Sections: Auth tiers table (anonymous/API key/Firebase JWT/admin), Token formats (`tlp_` vs `eyJ`), Data isolation model, Security headers (HSTS, CSP, X-Frame-Options, Permissions-Policy), Firebase Security Rules, Secrets management (GCP Secret Manager), Cloud Audit Logs.
- [ ] **T019** — Create `/docs/api-reference/+page.svelte`. Render endpoint index as a table: Method | Path | Auth Tier | Description. Cover all major endpoint groups: Incidents, Sub-resources, Postmortems, Analytics (6), Rules (3), API Keys (4), Scans (2), Health. Include: base URL, auth header format, list envelope `{"items":[],"total":N}`, error format `{"detail":"..."}`.

---

## Phase 5 — Polish & Validation (day 4)

### SEO & Accessibility audit

- [ ] **T020** — Verify every `+page.svelte` in `/docs/` has `<svelte:head>` with unique `<title>` (`{Section} — The Loop Docs`) and `<meta name="description">`.
- [ ] **T021** — Audit `WikiSidebar` accessibility: `<nav aria-label="Documentation">`, `<ul>` structure, `aria-current="page"` on active link, keyboard navigable.
- [ ] **T022** — Audit `PersonaPicker` accessibility: all 6 cards are `<button>` or have `role="button"` with descriptive `aria-label`, keyboard activatable, selected state communicated via `aria-pressed`.
- [ ] **T023** — Audit `CodeBlock` copy button: `aria-label="Copy code"`, focus ring visible, success feedback (button text changes to "Copied!" for 2s).

### Tests

- [ ] **T024** — Write `apps/web/tests/unit/wiki/WikiSidebar.test.ts`: renders all nav items, marks active item with `aria-current="page"`, no active item when path doesn't match.
- [ ] **T025** — Write `apps/web/tests/unit/wiki/PersonaPicker.test.ts`: renders 6 cards, clicking a card calls `onselect` with correct persona key, selected card has `aria-pressed="true"`.
- [ ] **T026** — Write `apps/web/tests/unit/wiki/CodeBlock.test.ts`: renders code content, copy button exists with correct aria-label.

### Final checks

- [ ] **T027** — Run `npm run check` from `apps/web/` — zero type errors.
- [ ] **T028** — Run `npm run lint` from `apps/web/` — zero lint errors.
- [ ] **T029** — Run `npm run build` from `apps/web/` — build succeeds.
- [ ] **T030** — Run `npm run test -- --run` from `apps/web/` — all tests pass.
- [ ] **T031** — Manually verify all 10 `/docs/*` routes render without 404/500 on `npm run dev`.
- [ ] **T032** — Verify Navbar "Docs" link appears on `/`, `/incidents/`, `/analytics/`, `/constitution/` — active state correct on `/docs/*`.
- [ ] **T033** — Update `CLAUDE.md`: add `/docs/` route to Frontend Architecture section, list wiki components in `lib/components/wiki/`.
- [ ] **T034** — Clean up `specs/020-product-wiki/` — no leftover placeholder text.

### PR

- [ ] **T035** — Open PR `feat/020-product-wiki` → `main`. Title: `feat(wiki): add product documentation wiki (/docs/)`.
- [ ] **T036** — Confirm all CI gates pass: lint, check, test, build, Trivy, docs-check.
- [ ] **T037** — Request review from @renatobardi.
- [ ] **T038** — Merge after approval + all checks green.
