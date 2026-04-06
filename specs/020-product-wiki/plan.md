# Implementation Plan: Product Wiki

**Branch**: `feat/020-product-wiki` | **Date**: 2026-04-05 | **Spec**: [spec.md](./spec.md)

---

## Summary

Build a 10-section public documentation wiki at `/docs/` using SvelteKit static pages and the existing design system. No backend changes, no new dependencies. Content covers all 6 personas (developer, IT manager, operator, support, QA, security) and all major platform capabilities. Estimated 3–4 days, 1 sprint.

---

## Technical Context

**Language/Version**: TypeScript 5+ / Svelte 5 runes  
**Primary Dependencies**: SvelteKit 2, Tailwind CSS 4 (existing — no new deps)  
**Storage**: N/A — static content only  
**Testing**: Vitest (unit tests for any interactive components), `npm run check` (type safety)  
**Target Platform**: Browser (SSR enabled — public pages, no auth)  
**Project Type**: Frontend-only feature (new routes + components)  
**Performance Goals**: All doc pages render <1s (static HTML, no API calls)  
**Constraints**: No new npm packages; no new backend endpoints; design tokens only  
**Scale/Scope**: 10 routes, ~5 new components, 1 navbar change

---

## Constitution Check

**GATE: PASS** — No violations detected.

| Mandamento | Requirement | Status |
|-----------|-------------|--------|
| I. Trunk-Based Development | PRs only to main, never direct push | ✅ Compliant |
| II. Design System Immutable | Use lib/ui tokens only — no ad-hoc styling | ✅ Compliant |
| III. Branch Taxonomy | `feat/020-product-wiki` | ✅ Compliant |
| VI. Single Environment | No new infra — same Cloud Run, same deploy | ✅ Compliant |
| VII. CI Gates | No new CI jobs needed; `docs-check` unaffected | ✅ Compliant |
| XII. Docs & Code | Structural change (new routes) → CLAUDE.md must be updated in same PR | ✅ Planned in Phase 5 |
| XIII. All Dependencies Explicit | No external deps; Navbar change is the only cross-cutting impact | ✅ Documented |

---

## Project Structure

```
apps/web/src/
├── routes/
│   └── docs/
│       ├── +layout.svelte              # WikiLayout wrapper (sidebar + content)
│       ├── +page.svelte                # Home: persona picker + feature index
│       ├── getting-started/
│       │   └── +page.svelte
│       ├── incidents/
│       │   └── +page.svelte
│       ├── postmortems/
│       │   └── +page.svelte
│       ├── analytics/
│       │   └── +page.svelte
│       ├── semgrep/
│       │   └── +page.svelte
│       ├── api-keys/
│       │   └── +page.svelte
│       ├── rules/
│       │   └── +page.svelte
│       ├── administration/
│       │   └── +page.svelte
│       ├── security/
│       │   └── +page.svelte
│       └── api-reference/
│           └── +page.svelte
└── lib/
    └── components/
        └── wiki/
            ├── WikiSidebar.svelte      # Section nav with active link highlight
            ├── PersonaPicker.svelte    # 6-role card grid (home page only)
            ├── CodeBlock.svelte        # <pre><code> with copy-to-clipboard
            └── DocSection.svelte      # Heading + prose block (reusable)
```

**Cross-cutting change**: `src/lib/components/Navbar.svelte` — add "Docs" link.

---

## Implementation Phases

| Phase | Focus | Deliverables |
|-------|-------|-------------|
| 0 | Foundation | `+layout.svelte`, `WikiSidebar`, `DocSection`, `CodeBlock`, Navbar link |
| 1 | Home + Getting Started | `/docs/` persona picker, `/docs/getting-started/` |
| 2 | Core product docs | `/docs/incidents/`, `/docs/postmortems/`, `/docs/analytics/` |
| 3 | Platform integration docs | `/docs/semgrep/`, `/docs/api-keys/`, `/docs/rules/` |
| 4 | Admin & security docs | `/docs/administration/`, `/docs/security/`, `/docs/api-reference/` |
| 5 | Polish & validation | SEO meta per page, a11y audit, CLAUDE.md update, full `npm run check` |

---

## Content Outline Per Section

### `/docs/` — Home
- Intro paragraph: what The Loop is
- **PersonaPicker** grid: 6 role cards → on select, highlights relevant links below
- Feature index: 10 sections as cards (icon + title + one-line description)

### `/docs/getting-started/`
- Prerequisites (Firebase account, team invite)
- Create your first incident (step-by-step)
- Navigate the dashboard
- Invite your team

### `/docs/incidents/`
- Incident lifecycle diagram (text-based, no images)
- Creating an incident (fields explained: title, severity, category, team, status)
- Managing an incident (status transitions, responders, action items)
- Closing an incident (required fields before close)
- Timeline events (automatic vs manual)
- Attachments

### `/docs/postmortems/`
- When to write a postmortem
- Available templates (5-Whys, Fishbone, etc.)
- Fields explained (root cause category, summary, timeline)
- Locking a postmortem (irreversible action)
- AI summary field (async, populated automatically)

### `/docs/analytics/`
- Dashboard overview (what each of the 8 KPI cards means)
- Filters: period, team, category, severity, status
- Drill-down navigation (click category → filtered view)
- PatternTimeline: how to read incident frequency
- SeverityTrend: errors vs warnings per week
- Rule Effectiveness: top 10 triggered rules

### `/docs/semgrep/`
- Overview: how The Loop distributes rules
- CI/CD setup (GitHub Actions workflow snippet)
- Version pinning (`THELOOP_RULES_VERSION` variable)
- Fallback behavior (`.semgrep/theloop-rules.yml.bak`)
- ERROR vs WARNING findings
- Scan history: what gets logged

### `/docs/api-keys/`
- What an API key is (scope, TTL)
- Creating an API key (UI walkthrough)
- Using an API key in CI (`Authorization: Bearer tlp_...`)
- Rotating / revoking a key
- Key format: `tlp_` prefix
- Project whitelist: how rules are filtered per key

### `/docs/rules/`
- Rule versioning (v0.1.0 → v0.4.0)
- Rule browser: `/rules/latest/`
- Rule severity: ERROR blocks merge, WARNING is advisory
- Languages covered (Python, JS/TS, Go, Java, C#, PHP, Ruby, Kotlin, Rust, C/C++)
- How to request a new rule

### `/docs/administration/`
- Team management (invite, remove)
- Configuration: rate limits (60 req/min analytics, 5 req/min waitlist)
- API base URL and environment info
- Firebase project: `theloopoute`

### `/docs/security/`
- Auth model: 4 tiers (anonymous, API key, Firebase JWT, admin)
- Token formats: `tlp_` vs `eyJ`
- Data isolation (single-org, per-incident access)
- Security headers (HSTS, CSP, X-Frame-Options)
- Firebase Security Rules (Firestore: write-only waitlist)
- Secrets management (GCP Secret Manager — no env files)
- Compliance: audit logging via Cloud Audit Logs

### `/docs/api-reference/`
- Base URL: `https://api.loop.oute.pro`
- Auth header: `Authorization: Bearer <token>`
- Endpoint index table (method, path, auth tier, description) for all major endpoints:
  - Incidents CRUD
  - Sub-resources (timeline, responders, action items, attachments)
  - Postmortems
  - Analytics (6 endpoints)
  - Rules (3 endpoints)
  - API Keys (4 endpoints)
  - Scans (2 endpoints)
  - Health check
- Response envelope: `{"items": [...], "total": N}` for lists
- Error format: `{"detail": "..."}`

---

## Cross-Cutting Concerns

### Navbar
Add "Docs" between "Analytics" and "Constitution" in `Navbar.svelte`. Uses existing nav link pattern. Active state via `$page.url.pathname.startsWith('/docs/')`.

### SEO
Every `+page.svelte` includes:
```svelte
<svelte:head>
  <title>{pageTitle} — The Loop Docs</title>
  <meta name="description" content="..." />
</svelte:head>
```

### Accessibility
- `WikiSidebar` uses `<nav aria-label="Documentation">` with `<ul>` list
- Active link has `aria-current="page"`
- `CodeBlock` copy button has `aria-label="Copy code"`

### Trailing Slashes
All routes follow `trailingSlash: 'always'` (enforced globally in `+layout.ts`). Route files must not override this.

---

## Dependencies

| Dependency | Type | Status |
|-----------|------|--------|
| Existing design tokens (`app.css`) | Frontend | ✅ Available |
| `lib/ui` components (Container, Section, Card, Badge, Tabs) | Frontend | ✅ Available |
| `Navbar.svelte` | Frontend (change) | Edit required |
| SvelteKit routing | Framework | ✅ No config change |
| No new npm packages | — | ✅ Confirmed |
| No backend routes | — | ✅ Confirmed |
| No DB migrations | — | ✅ Confirmed |
| No CI changes | — | ✅ Confirmed |
