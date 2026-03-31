# Tasks: Landing Page Design Polish

**Input**: Design documents from `/specs/002-landing-page-polish/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested — test tasks omitted. Manual testing via quickstart.md checklist.

**Organization**: Tasks grouped by user story (8 stories from spec.md, priorities P1–P3).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `apps/web/src/` (SvelteKit)
- **i18n**: `apps/web/messages/` (Paraglide JSON)
- **Tests**: `apps/web/tests/unit/`

---

## Phase 1: Setup (i18n Keys)

**Purpose**: Add all new i18n message keys needed by subsequent phases

- [x] T001 Add new i18n keys to `apps/web/messages/en.json`: `nav_features`, `nav_pricing`, `nav_waitlist`, `nav_menu_open`, `nav_menu_close`, `skip_to_content`, `form_email_label`, `pricing_join_waitlist`, `pricing_popular_badge`, `hero_scroll_hint`, `hero_product_name`
- [x] T002 [P] Add same i18n keys with Portuguese translations to `apps/web/messages/pt.json`
- [x] T003 [P] Add same i18n keys with Spanish translations to `apps/web/messages/es.json`

---

## Phase 2: Foundational (Design System & Shared Component Changes)

**Purpose**: Core design system and component changes that multiple user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Adjust `--color-text-subtle` from `#71717a` to `#8b8b95` in `apps/web/src/app.css` for WCAG AA compliance (4.5:1 against both `#0a0a0b` and `#141416`)
- [x] T005 [P] Add optional `label` prop to Input component in `apps/web/src/lib/ui/Input.svelte` — when provided, render a visually-hidden `<label>` element (class `sr-only`) associated with the input via `id`/`for` attributes
- [x] T006 [P] Remove `min-h-screen` and `flex items-center` from default Section class in `apps/web/src/lib/ui/Section.svelte` — keep `py-20 lg:py-32` padding and the reveal animation. Add an optional `hero` prop that restores `min-h-screen flex items-center` when true
- [x] T006b [P] Fix typo in Section.svelte reveal animation: change `prefers-reduce-motion` to `prefers-reduced-motion` in the matchMedia query (`apps/web/src/lib/ui/Section.svelte`)
- [x] T007 [P] Add `tag` prop to `apps/web/src/lib/components/LanguageSelector.svelte` (default: `'nav'`). When `tag="div"`, render a `<div role="group" aria-label="Language selector">` instead of `<nav>`. Add `min-h-[44px] min-w-[44px]` padding to each language link for 44x44px touch targets
- [x] T008 Add `smooth-scroll` CSS rule to `apps/web/src/app.css`: `html { scroll-behavior: smooth }` with `@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto } }`

**Checkpoint**: Design system tokens updated, shared components ready for story implementation

---

## Phase 3: User Story 1 — Visitor Identifies the Product (Priority: P1) MVP

**Goal**: Product name "The Loop" visible above the fold on all viewports

**Independent Test**: Load `/en/`, `/pt/`, `/es/` — verify "The Loop" text visible without scrolling on desktop and mobile

### Implementation for User Story 1

- [x] T009 [US1] Add product name to Hero in `apps/web/src/lib/components/Hero.svelte` — add `<p class="text-lg md:text-xl font-semibold text-accent tracking-wide uppercase">{hero_product_name()}</p>` above the `<h1>`, import `hero_product_name` from messages

**Checkpoint**: Product name visible above the fold on all locales and viewports

---

## Phase 4: User Story 2 — Visitor Switches Language Successfully (Priority: P1)

**Goal**: Language selector links navigate correctly without doubled prefixes

**Independent Test**: Click each language (EN/PT/ES) in header and footer on each locale — verify URL is `/{locale}/` not `/{locale}/{locale}/`

### Implementation for User Story 2

- [x] T010 [US2] Verify language selector on current branch works correctly in `apps/web/src/lib/components/LanguageSelector.svelte` — the `href="/"` + `hreflang` pattern should produce correct URLs via Paraglide's `translateHref()`. If the bug persists, debug the Paraglide link translation pipeline. Run dev server and click each language link on each locale to confirm

**Checkpoint**: All 9 language switch combinations (3 source x 3 target locales) produce correct URLs

---

## Phase 5: User Story 3 — Screen Reader Accessibility (Priority: P1)

**Goal**: Email inputs have proper labels, skip-to-content link exists as first focusable element

**Independent Test**: Use VoiceOver/NVDA to navigate the page — verify email inputs announced as "Email address", skip link is first Tab target

### Implementation for User Story 3

- [x] T011 [P] [US3] Create `apps/web/src/lib/ui/SkipLink.svelte` — a visually-hidden link (`sr-only focus:not-sr-only`) targeting `#main-content` that becomes visible on focus. Style: `fixed top-2 left-2 z-[100] bg-accent text-white px-4 py-2 rounded-lg`. Use `skip_to_content` i18n message for text
- [x] T012 [P] [US3] Update `apps/web/src/lib/components/WaitlistForm.svelte` — pass `label={form_email_label()}` prop to the `<Input>` component, import `form_email_label` from messages
- [x] T013 [US3] Export `SkipLink` from `apps/web/src/lib/ui/index.ts`
- [x] T014 [US3] Add SkipLink to `apps/web/src/routes/+layout.svelte` — import and render `<SkipLink />` as the first child inside `<ParaglideJS>`, before any other content
- [x] T015 [US3] Add `id="main-content"` to the `<main>` element in `apps/web/src/routes/+page.svelte`

**Checkpoint**: Screen reader announces "Email address" on form focus; Tab key hits skip link first; skip link scrolls to main content

---

## Phase 6: User Story 4 — Cohesive Narrative Scroll (Priority: P2)

**Goal**: Sections flow as a continuous narrative — no full-viewport empty gaps between them

**Independent Test**: Scroll desktop (1440px) and mobile — next section heading is partially visible before current section exits viewport

### Implementation for User Story 4

- [x] T016 [US4] Update Hero to use the `hero` prop on Section in `apps/web/src/lib/components/Hero.svelte` — add `hero` attribute to `<Section>` so only the Hero retains `min-h-screen` centering behavior
- [x] T017 [US4] Add scroll-down indicator to Hero in `apps/web/src/lib/components/Hero.svelte` — below the "by Oute" text, add an animated SVG chevron (`animate-bounce`) wrapped in a button with `aria-label={hero_scroll_hint()}` that scrolls to the next section. Import `hero_scroll_hint` from messages. Handle edge case: hide or fade out the chevron once the user scrolls past the hero (e.g., IntersectionObserver on hero section)
- [x] T018 [US4] Verify all section components have `id` attributes for anchor targets in `apps/web/src/routes/+page.svelte` — ensure Hero has `id="hero"`, Problem has `id="problem"`, Layers has `id="features"` (the anchor target for nav), HowItWorks has `id="how-it-works"`, Integrations has `id="integrations"`, Pricing has `id="pricing"`, WaitlistCta has `id="waitlist"`

**Checkpoint**: Scrolling through the page feels like a continuous narrative; no "page ended" gaps

---

## Phase 7: User Story 5 — Pricing CTAs and Tier Hierarchy (Priority: P2)

**Goal**: Every pricing card has a CTA; Pay-as-you-go is visually elevated as "Most popular"

**Independent Test**: Scroll to pricing — verify Free and PAYG have "Join the waitlist" buttons, PAYG has a "Most popular" badge and accent border

### Implementation for User Story 5

- [x] T019 [US5] Update pricing data in `apps/web/src/lib/components/Pricing.svelte` — add `cta: { text: pricing_join_waitlist(), href: '#waitlist' }` to Free and Pay-as-you-go plans. Change Pay-as-you-go to `highlighted: true` (and Enterprise to `highlighted: false`). Add a `popular` boolean field (true only for Pay-as-you-go). Import `pricing_join_waitlist` and `pricing_popular_badge` from messages
- [x] T020 [US5] Update card rendering in `apps/web/src/lib/components/Pricing.svelte` — for highlighted card, add accent border (`border-accent`) and glow shadow. Add a Badge with `variant="accent"` displaying `pricing_popular_badge()` above the card title when `plan.popular` is true. For `#waitlist` href CTAs, use `Button variant="primary"` (not secondary) to drive conversion
- [x] T021 [US5] Ensure CTA anchor links (`href="#waitlist"`) use smooth scroll (already handled by T008 CSS rule) and work correctly with Paraglide — add ESLint disable comment for anchor links if needed

**Checkpoint**: All three pricing cards have action buttons; PAYG is visually distinguished with badge and accent styling

---

## Phase 8: User Story 6 — Sticky Navigation (Priority: P2)

**Goal**: Sticky nav bar with product name, 3 anchor links, language selector; hamburger menu on mobile

**Independent Test**: Click Features/Pricing/Waitlist links — verify smooth scroll to correct sections. Resize to mobile — verify hamburger menu works

### Implementation for User Story 6

- [x] T022 [US6] Create `apps/web/src/lib/ui/Navbar.svelte` — sticky nav component with: (1) Desktop: product name "The Loop" (left, links to `#hero`), 3 anchor links from i18n (Features→`#features`, Pricing→`#pricing`, Waitlist→`#waitlist`), LanguageSelector (right). Style: `fixed top-0 w-full z-50 bg-bg/80 backdrop-blur-md border-b border-border/50`. (2) Mobile (< md): product name + hamburger icon button (`nav_menu_open`/`nav_menu_close` aria-labels). Tap toggles a dropdown panel with the 3 links + LanguageSelector. Use Svelte 5 `$state` for open/close toggle. Handle edge cases: close hamburger menu on resize to desktop; ensure nav degrades gracefully if sections are conditionally hidden
- [x] T023 [US6] Export `Navbar` from `apps/web/src/lib/ui/index.ts`
- [x] T024 [US6] Update `apps/web/src/routes/+layout.svelte` — remove the existing fixed LanguageSelector div (`<div class="fixed top-4 right-4 z-50">`), import and add `<Navbar />` as the first child inside `<ParaglideJS>` (after SkipLink). Add `pt-16` to the content wrapper to offset the fixed nav height
- [x] T025 [US6] Pass `tag="div"` to LanguageSelector in `apps/web/src/lib/components/Footer.svelte` — uses the tag prop from T007 to render as `<div role="group">` instead of nested `<nav>`

**Checkpoint**: Sticky nav visible at all scroll positions; anchor links smooth-scroll to correct sections; hamburger menu works on mobile; footer has no nested nav issue

---

## Phase 9: User Story 7 — Readable Content / WCAG Contrast (Priority: P3)

**Goal**: All body text meets WCAG AA contrast (4.5:1 normal, 3:1 large)

**Independent Test**: Run Lighthouse accessibility audit — verify 90+ score and zero contrast failures

### Implementation for User Story 7

- [x] T026 [US7] Audit all text color usage across components — verify that `text-text-subtle` (now `#8b8b95` from T004) meets 4.5:1 on both `bg` (`#0a0a0b`) and `bg-surface` (`#141416`). If "by Oute" in Hero still fails, either bump its color to `text-text-muted` or remove it from the hero (keep only in footer)
- [x] T027 [US7] Verify focus indicators exist on all interactive elements — buttons, links, and inputs should have visible focus rings (`:focus-visible` outline). Add `outline-accent` focus styles to `apps/web/src/app.css` if missing: `*:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px; }`

**Checkpoint**: Lighthouse Accessibility score 90+; zero contrast warnings; all interactive elements have visible focus states

---

## Phase 10: User Story 8 — Visual Consistency (Priority: P3)

**Goal**: All section headings centered, all cards use unified Card component styling

**Independent Test**: Scroll through all sections — verify all headings centered, all cards visually identical in border/padding/background

### Implementation for User Story 8

- [x] T028 [P] [US8] Center heading in `apps/web/src/lib/components/Problem.svelte` — add `text-center` to the section heading `<h2>` if not already present
- [x] T029 [P] [US8] Center heading in `apps/web/src/lib/components/HowItWorks.svelte` — add `text-center` to the section heading `<h2>` if not already present; also center the description paragraph below the flow diagram
- [x] T030 [P] [US8] Verify heading alignment in `apps/web/src/lib/components/Layers.svelte`, `apps/web/src/lib/components/Integrations.svelte`, `apps/web/src/lib/components/WaitlistCta.svelte` — ensure all `<h2>` headings have `text-center` class
- [x] T031 [US8] Verify all card usage across Layers, Integrations, and Pricing uses the shared `Card` component from `apps/web/src/lib/ui/Card.svelte` with no ad-hoc border/padding overrides. If any component applies its own card styling, refactor to use the shared Card

**Checkpoint**: All headings centered; all cards visually unified. Note: FR-012 (no nested nav in footer) is already resolved by T025 in Phase 8 (US6)

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final validation across all stories

- [x] T032 Run `npm run lint` in `apps/web/` — fix any ESLint/Prettier violations
- [x] T033 Run `npm run check` in `apps/web/` — fix any TypeScript/Svelte-check errors
- [x] T034 Run `npm run test` in `apps/web/` — ensure existing tests still pass
- [x] T035 Run `npm run build` in `apps/web/` — verify production build succeeds
- [x] T036 Run manual testing checklist from `specs/002-landing-page-polish/quickstart.md`
- [x] T037 Verify Paraglide codegen includes new i18n keys — run dev server, check all 3 locales render new text correctly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (i18n keys must exist for imports)
- **US1 (Phase 3)**: Depends on Phase 1 (i18n key `hero_product_name`)
- **US2 (Phase 4)**: Depends on Phase 2 (LanguageSelector `tag` prop, touch targets)
- **US3 (Phase 5)**: Depends on Phase 2 (Input `label` prop)
- **US4 (Phase 6)**: Depends on Phase 2 (Section `hero` prop, smooth scroll CSS)
- **US5 (Phase 7)**: Depends on Phase 1 (i18n keys for CTAs and badge)
- **US6 (Phase 8)**: Depends on Phase 2 (LanguageSelector `tag` prop) + Phase 5 (SkipLink in layout)
- **US7 (Phase 9)**: Depends on Phase 2 (color token fix)
- **US8 (Phase 10)**: Can start after Phase 2
- **Polish (Phase 11)**: Depends on all previous phases

### User Story Dependencies

- **US1 (P1)**: Independent — only needs i18n keys
- **US2 (P1)**: Independent — only needs foundational LanguageSelector changes
- **US3 (P1)**: Independent — only needs foundational Input changes
- **US4 (P2)**: Independent — only needs foundational Section changes
- **US5 (P2)**: Independent — only needs i18n keys
- **US6 (P2)**: Depends on US3 (SkipLink must be in layout before Navbar is added after it)
- **US7 (P3)**: Independent — only needs foundational color token
- **US8 (P3)**: Independent — pure CSS alignment changes

### Parallel Opportunities

After Phase 2 completes:
- US1, US2, US3, US4, US5, US7, US8 can all run in parallel
- US6 should run after US3 (layout ordering dependency)

---

## Parallel Example: After Foundational Phase

```text
# These can all run in parallel (different files, no dependencies):
T009 [US1] Hero product name
T010 [US2] Language selector verification
T011 [US3] SkipLink component
T012 [US3] WaitlistForm label
T019 [US5] Pricing CTAs
T026 [US7] Contrast audit
T028 [US8] Problem heading alignment
T029 [US8] HowItWorks heading alignment
```

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup (i18n keys)
2. Complete Phase 2: Foundational (design system + shared components)
3. Complete Phase 3: US1 (product name)
4. Complete Phase 4: US2 (language selector fix)
5. Complete Phase 5: US3 (accessibility)
6. **STOP and VALIDATE**: Run lint, check, test, build. Manual test P1 stories.
7. Deploy — critical bugs fixed, accessibility baseline met

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add P1 stories (US1+US2+US3) → Critical fixes deployed
3. Add P2 stories (US4+US5+US6) → UX improvements deployed
4. Add P3 stories (US7+US8) → Visual polish deployed
5. Polish phase → Final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- No new npm dependencies — all built with existing Tailwind + Svelte primitives
- Language selector bug may already be fixed on current branch (commit `a170987`) — T010 is verification
- Commit after each phase or logical group of completed tasks
