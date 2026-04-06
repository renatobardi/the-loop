# Tasks: Product Docs

**Input**: Design documents from `/specs/021-product-wiki/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Organization**: Tasks grouped by user story. US4 and US1 are P1 (MVP). US2, US3, US5 are P2.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- No test tasks — spec does not request TDD approach

---

## Phase 1: Setup

**Purpose**: Create directory structure and empty placeholder files

- [x] T001 Create stub files to establish `apps/web/src/routes/docs/` directory structure: empty `+layout.svelte`, `+page.svelte`, and one stub per section subfolder (e.g. `getting-started/+page.svelte`) per plan.md
- [x] T002 Create `apps/web/src/lib/components/docs/nav.ts` stub (empty export) to establish `lib/components/docs/` directory
- [x] T003 Create `apps/web/tests/unit/docs/.gitkeep` to establish the test directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete

- [x] T004 Create `apps/web/src/lib/components/docs/nav.ts` with `USER_SECTIONS`, `ADMIN_SECTIONS`, `PERSONA_SECTIONS` constants and `NavItem` type per plan.md data
- [x] T005 [P] Create `apps/web/src/lib/components/docs/DocSection.svelte` — reusable heading + prose wrapper component (props: `title: string`, `id: string`, renders `<section>` with `<h2>` and `{@render children()}`)
- [x] T006 [P] Create `apps/web/src/lib/components/docs/CodeBlock.svelte` — copy-to-clipboard `<pre><code>` block (props: `code: string`, `language?: string`, `label?: string`; copy button with `aria-label="Copy code"`, announces "Copied!" on success; WCAG 2.1 AA compliant)
- [x] T007 Create `apps/web/src/lib/components/docs/DocSidebar.svelte` — sidebar nav (props: `items: NavItem[]`; `<nav aria-label="Documentation">`; `aria-current="page"` on active link; active detection via `$page.url.pathname`; profile-agnostic — caller pre-filters items)
- [x] T008 Create `apps/web/src/lib/components/docs/PersonaPicker.svelte` — 6-role card grid (Developer, IT Manager, Operator, Support, QA, Security; `<button aria-pressed={active}>` for each; selecting a persona emits selected key; highlights relevant section cards via `ring-accent`)
- [x] T009 Create `apps/web/src/routes/docs/+layout.svelte` — DocLayout wrapping DocSidebar + `{@render children()}`; import `profile` from `$lib/stores/profile`; pass `USER_SECTIONS` to sidebar when `$profile` is null (unauthenticated or loading) and `[...USER_SECTIONS, ...ADMIN_SECTIONS]` when `$profile?.is_admin === true`; sidebar receives only sections the current user can see (unauthenticated users see USER_SECTIONS, same as regular users — FR-004 compliance)
- [x] T010 Edit `apps/web/src/lib/components/Navbar.svelte` — add authenticated "Docs" link between Analytics and Constitution; active state when `$page.url.pathname.startsWith('/docs/')`; link hidden on unauthenticated routes (use existing auth store check)

**Checkpoint**: Foundation ready — all shared components exist and Navbar has Docs link

---

## Phase 3: User Story 4 — New User Self-Onboards (Priority: P1) 🎯 MVP

**Goal**: A brand-new user can navigate `/docs/` and `/docs/getting-started/` to complete account setup → first incident → dashboard navigation → invite team

**Independent Test**: A brand-new user can follow `/docs/getting-started/` top-to-bottom and end up with their first incident created and their team invited

- [x] T011 [US4] Create `apps/web/src/routes/docs/+page.svelte` — docs home page with:
  - `<svelte:head>` with title "The Loop Docs" and meta description
  - 2-sentence intro to The Loop
  - `<PersonaPicker>` component (6 roles)
  - Feature index grid: SSR renders 7 user section cards initially; admin section cards added silently client-side after auth resolves (no skeleton, no loading state, no animation)
  - Admin cards visually grouped with subtle "Administration" label
  - Persona selection highlights relevant cards with `ring-accent`
- [x] T012 [US4] Create `apps/web/src/routes/docs/getting-started/+page.svelte` — SSR public page with:
  - `<svelte:head>` with title "Getting Started — The Loop Docs" and meta description
  - Sequential flow: account setup → create first incident → navigate dashboard → invite team
  - Uses `DocSection` and `CodeBlock` components throughout
  - Every step actionable without clicking away from the page

**Checkpoint**: US4 fully functional — new user can self-onboard via `/docs/getting-started/`; Docs link appears in authenticated Navbar

---

## Phase 4: User Story 1 — Developer Integration (Priority: P1)

**Goal**: A developer can navigate `/docs/`, select Developer persona, and follow Semgrep + API Keys + Rules docs to configure a working CI scan

**Independent Test**: A developer unfamiliar with The Loop can navigate to `/docs/`, select Developer role, and configure a working CI scan without asking for help

- [x] T013 [P] [US1] Create `apps/web/src/routes/docs/semgrep/+page.svelte` — SSR public page with:
  - `<svelte:head>` with title "Semgrep Integration — The Loop Docs" and meta description
  - Architecture overview
  - Full GitHub Actions workflow YAML in `CodeBlock` (complete, copy-able, produces a working scan)
  - Version pinning instructions
  - Fallback `.bak` behavior explanation
  - ERROR vs WARNING distinction
  - Scan history section
  - Local testing commands in `CodeBlock`
- [x] T014 [P] [US1] Create `apps/web/src/routes/docs/api-keys/+page.svelte` — SSR public page with:
  - `<svelte:head>` with title "API Keys — The Loop Docs" and meta description
  - What it is: scope, `tlp_` prefix explained
  - Step-by-step creation via UI
  - Usage in CI: `Authorization: Bearer tlp_…` header in `CodeBlock`
  - Project whitelist explanation
  - Rotating / revoking instructions
- [x] T015 [P] [US1] Create `apps/web/src/routes/docs/rules/+page.svelte` — SSR public page with:
  - `<svelte:head>` with title "Rules — The Loop Docs" and meta description
  - Version history (v0.1.0 → v0.4.0, rule counts per version)
  - Rule browser link to `/rules/latest/`
  - Severity model explanation
  - 10 languages covered
  - Rule ID format
  - How to request a new rule

**Checkpoint**: US1 fully functional — Developer persona highlights Semgrep/API Keys/Rules; all three pages are standalone and complete

---

## Phase 5: User Story 2 — IT Manager Analytics Value (Priority: P2)

**Goal**: An IT Manager can open `/docs/analytics/` and understand all 8 KPI cards and how to apply filters

**Independent Test**: An IT Manager can open `/docs/analytics/` and answer "what does the MTTR card mean and how do I filter it by team?" without clicking anywhere else

- [x] T016 [US2] Create `apps/web/src/routes/docs/analytics/+page.svelte` — SSR public page with:
  - `<svelte:head>` with title "Analytics — The Loop Docs" and meta description
  - Dashboard overview section
  - All 8 KPI cards explained in plain language (no technical jargon): MTTR, MTTD, total incidents, open incidents, resolved incidents, SLA breach rate, severity distribution, team workload
  - Filters section: period, team, category, severity, status — how each applies
  - Drill-down explanation
  - PatternTimeline chart description
  - SeverityTrend chart description
  - Rule Effectiveness table description

**Checkpoint**: US2 functional — IT Manager persona highlights Getting Started + Analytics; analytics page answers all KPI questions standalone

---

## Phase 6: User Story 3 — Operator Incident Lifecycle (Priority: P2)

**Goal**: An operator can open `/docs/incidents/` and `/docs/postmortems/` to understand the full incident and postmortem workflow

**Independent Test**: An operator can open `/docs/incidents/` and answer "what fields are required to close an incident?" in under 2 minutes

- [x] T017 [P] [US3] Create `apps/web/src/routes/docs/incidents/+page.svelte` — SSR public page with:
  - `<svelte:head>` with title "Incidents — The Loop Docs" and meta description
  - Lifecycle section: create → open → investigating → resolved → closed with status transition rules
  - Fields explained: title, severity, category, team, status
  - Responders section
  - Action Items section
  - Timeline events section
  - Attachments section
  - **Closing checklist**: clear list of required fields before an incident can be closed (answers the independent test directly)
- [x] T018 [P] [US3] Create `apps/web/src/routes/docs/postmortems/+page.svelte` — SSR public page with:
  - `<svelte:head>` with title "Postmortems — The Loop Docs" and meta description
  - When to write a postmortem
  - Template catalog: 5-Whys, Fishbone, Timeline, Pre/Mortem, OODA, PDCA — when to use each
  - Fields explained
  - Locking section: what it means, that it's irreversible (warning)
  - AI summary section

**Checkpoint**: US3 functional — Operator persona highlights Incidents/Postmortems/Getting Started; operator can answer closing questions standalone

---

## Phase 7: User Story 5 — Administrator Platform Config Docs (Priority: P2)

**Goal**: An admin user sees 3 additional sections (Administration, Security, API Reference) that are completely hidden from regular users

**Independent Test**: Admin user sees admin sections in sidebar/home; regular user does not; direct URL access by non-admin redirects to `/docs/`

- [x] T019 [US5] Create `apps/web/src/routes/docs/(admin)/+layout.ts` — export `const ssr = false` (CSR-only; Firebase Auth client-side requirement; same pattern as `/analytics/`)
- [x] T020 [US5] Create `apps/web/src/routes/docs/(admin)/+layout.svelte` — admin guard using the same pattern as `routes/admin/+layout.svelte`:
  - Import `user` from `$lib/stores/auth` (Firebase `User | null`) and `profile` from `$lib/stores/profile` (`UserProfile | null`)
  - `$effect`: when `$user === null` and Firebase auth has resolved → `goto('/login/')`; when `$profile !== null && !$profile?.is_admin` → `goto('/docs/')`; else → render `{@render children()}`
  - Show loading state while `$profile === null` and `$user !== null` (authenticated but profile not yet loaded — prevents flash of content)
  - Edge case: if `$profile?.is_admin` becomes `false` after being `true` (admin role revoked mid-session), the `$effect` re-evaluates on next render cycle and redirects to `/docs/`
- [x] T021 [P] [US5] Create `apps/web/src/routes/docs/(admin)/administration/+page.svelte` — admin-only page with:
  - `<svelte:head>` with title "Administration — The Loop Docs" and meta description
  - Team management section
  - Rate limits: 60 req/min analytics, 5 req/min waitlist
  - API base URL
  - Single-environment model explanation
  - Firebase project `theloopoute` reference
- [x] T022 [P] [US5] Create `apps/web/src/routes/docs/(admin)/security/+page.svelte` — admin-only page with:
  - `<svelte:head>` with title "Security — The Loop Docs" and meta description
  - Auth tiers table: Anonymous / API key / Firebase JWT / Admin
  - Token formats section
  - Security headers: HSTS, CSP, X-Frame-Options
  - Firebase Security Rules overview
  - Secrets management: GCP Secret Manager
  - Cloud Audit Logs section
- [x] T023 [P] [US5] Create `apps/web/src/routes/docs/(admin)/api-reference/+page.svelte` — admin-only page with:
  - `<svelte:head>` with title "API Reference — The Loop Docs" and meta description
  - Base URL + auth header section
  - Endpoint index table: Method / Path / Auth Tier / Description covering all groups (Health, Incidents, Sub-resources, Postmortems, Analytics×6, Rules×3, API Keys×4, Scans×2)
  - List envelope format: `{"items":[],"total":N}`
  - Error format: `{"detail":"..."}`
  - Rate limit headers section

**Checkpoint**: US5 functional — admin sees 10 sections; regular user sees 7; non-admin direct access to admin URLs redirects to `/docs/`; unauthenticated redirects to `/login/`

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Unit tests, accessibility audit, docs update, CI validation

- [x] T024 [P] Write `apps/web/tests/unit/docs/DocSidebar.test.ts` — renders correct items from `items` prop; marks active item with `aria-current="page"`; renders nothing extra when items list is empty
- [x] T025 [P] Write `apps/web/tests/unit/docs/PersonaPicker.test.ts` — renders 6 persona cards; `aria-pressed` toggles on selection; emits correct persona key on click
- [x] T026 [P] Write `apps/web/tests/unit/docs/CodeBlock.test.ts` — renders `code` content; copy button has `aria-label="Copy code"`; copy button click writes to clipboard
- [x] T027 [P] Write `apps/web/tests/unit/docs/AdminLayout.test.ts` — unauthenticated user (`$user === null`) → redirects to `/login/`; non-admin (`$profile.is_admin === false`) → redirects to `/docs/`; admin (`$profile.is_admin === true`) → renders children; shows loading while `$user !== null && $profile === null`; admin loses role mid-session (`is_admin` changes to `false` after mount) → redirects to `/docs/` on next re-evaluation
- [x] T028 Run `npm run check` from `apps/web/` — zero TypeScript errors across all new routes and components
- [x] T029 Run `npm run lint` from `apps/web/` — zero lint errors
- [x] T030 Run `npm run build` from `apps/web/` — production build passes
- [x] T031 Run `npm run test -- --run` from `apps/web/` — all unit tests pass including T024–T027
- [x] T032 WCAG 2.1 AA audit using Chrome DevTools Accessibility panel (or axe browser extension): verify `<nav aria-label="Documentation">` on DocSidebar; `aria-current="page"` on active link; `aria-pressed` on PersonaPicker buttons; `aria-label="Copy code"` on CodeBlock button; body text contrast ≥ 4.5:1 using design tokens; keyboard-navigate through sidebar and persona picker with no mouse
- [x] T033 Manually verify every `CodeBlock` in all docs pages against current production API/CLI per SC-006: run the GitHub Actions YAML snippet against a real scan, test the `Authorization: Bearer tlp_…` header, confirm rule version numbers match production. Update any outdated snippet before merging (Mandamento XII: in same PR)
- [x] T034 Update `CLAUDE.md` — add `routes/docs/` routes, `lib/components/docs/` components, and `(admin)` route group pattern to architecture section (Mandamento XII: same PR as code)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — **BLOCKS all user story phases**
- **Phase 3 (US4 P1)**: Depends on Phase 2 — start here for MVP
- **Phase 4 (US1 P1)**: Depends on Phase 2 — can run in parallel with Phase 3
- **Phase 5 (US2 P2)**: Depends on Phase 2 — can run after P1 stories
- **Phase 6 (US3 P2)**: Depends on Phase 2 — can run in parallel with Phase 5
- **Phase 7 (US5 P2)**: Depends on Phase 2 — T019+T020 must precede T021–T023
- **Phase 8 (Polish)**: Depends on all desired user stories complete

### User Story Dependencies

- **US4**: Requires T004–T010 (all foundation)
- **US1**: Requires T004, T005, T006, T007, T009 (no US4 dependency)
- **US2**: Requires T004, T005, T007, T009
- **US3**: Requires T004, T005, T007, T009
- **US5**: Requires T004, T007, T009 + T019, T020 (admin layout must exist first)

### Parallel Opportunities

- T005, T006, T007, T008 in Phase 2 — different files, no inter-dependency
- T013, T014, T015 in Phase 4 — different route files, parallel
- T017, T018 in Phase 6 — different route files, parallel
- T021, T022, T023 in Phase 7 — different route files, parallel (after T019+T020)
- T024, T025, T026, T027 in Phase 8 — different test files, parallel

---

## Implementation Strategy

### MVP (US4 + US1 — P1 stories only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundation (CRITICAL — blocks everything)
3. Complete Phase 3: US4 — `/docs/` home + `/docs/getting-started/`
4. Complete Phase 4: US1 — `/docs/semgrep/`, `/docs/api-keys/`, `/docs/rules/`
5. **STOP and VALIDATE**: Docs link works in Navbar; Developer persona highlights correct sections; getting-started page guides new user end-to-end
6. Deploy to `main`

### Full Delivery

After MVP: add Phase 5 (US2 analytics), Phase 6 (US3 incidents/postmortems), Phase 7 (US5 admin) in any order — each independently testable. Finish with Phase 8 polish.

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [US#] label maps task to user story for traceability
- Admin sections: `(admin)` route group handles all auth — **NO per-page auth boilerplate** (T019+T020 handle it once)
- All content must reflect **current production state only** (FR-014, SC-006)
- All styling via design tokens only — no ad-hoc colors or spacing
- `trailingSlash: 'always'` is set globally — no per-route overrides needed
- Total: 34 tasks | 8 phases | ~5 days
