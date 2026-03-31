# Tasks: Public Constitution Page

**Input**: Design documents from `/specs/005-constitution-page/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md

**Tests**: Not explicitly requested — test tasks omitted. Quality validation via lint/check/build in Polish phase.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Includes exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Configure Paraglide pathnames for localized route slugs

- [x] T001 Add `pathnames` config to `apps/web/src/lib/i18n.ts` — map `/constitution` to `{ en: "/constitution", pt: "/constituicao", es: "/constitucion" }`

**Checkpoint**: `npm run dev` starts. Paraglide recognizes the new pathname mapping.

---

## Phase 2: Foundational (i18n Messages)

**Purpose**: Add all constitution i18n message keys — MUST complete before any component work

**⚠️ CRITICAL**: All components depend on these messages existing in Paraglide's generated runtime

- [x] T002 [P] Add constitution message keys to `apps/web/messages/en.json` — `constitution_headline`, `constitution_subheadline`, `constitution_mandate_1_title` through `constitution_mandate_12_title`, `constitution_mandate_1_desc` through `constitution_mandate_12_desc`, `constitution_transparency_text`, `constitution_transparency_link`, `constitution_meta_title`, `constitution_meta_description` (30 keys total)
- [x] T003 [P] Add constitution message keys to `apps/web/messages/pt.json` — same 30 keys with Portuguese translations from spec
- [x] T004 [P] Add constitution message keys to `apps/web/messages/es.json` — same 30 keys with Spanish translations from spec

**Checkpoint**: `npx paraglide-js compile` succeeds. All 30 keys available in `$lib/paraglide/messages.js`.

---

## Phase 3: User Story 1 + 2 — Browse Constitution & Mandate Content (Priority: P1) 🎯 MVP

**Goal**: Constitution page renders at `/en/constitution/`, `/pt/constituicao/`, `/es/constitucion/` with 12 mandate cards, hero section, responsive grid, per-page meta tags, and hreflang alternates. Mandate content presents engineering principles without internal implementation details.

**Independent Test**: Navigate to all 3 locale URLs. Verify 12 mandates render with roman numerals, titles, and descriptions. Verify meta tags and hreflang in page source. Verify responsive layout at 375px/768px/1280px. Verify language switching navigates to correct localized slug.

- [x] T005 [P] [US2] Create `apps/web/src/lib/components/MandateCard.svelte` — Card component with roman numeral in accent color, bold title, and description. Uses `Card` from `$lib/ui`. Props: `number` (string), `title` (string), `description` (string)
- [x] T006 [P] [US1] Create `apps/web/src/lib/components/ConstitutionHero.svelte` — Hero section using `Section` and `Container` from `$lib/ui`. Renders `constitution_headline()` and `constitution_subheadline()` messages. Centered text, matching landing page hero typography
- [x] T007 [US1] Create `apps/web/src/lib/components/MandatesGrid.svelte` — Responsive grid rendering 12 `MandateCard` instances. Imports all 24 mandate message functions (`constitution_mandate_N_title`, `constitution_mandate_N_desc`). Grid layout: 1 col mobile, 2 col `md:`, 3 col `lg:`. Uses `Section` and `Container` from `$lib/ui`
- [x] T008 [US1] Create `apps/web/src/routes/constitution/+page.svelte` — Page composition importing `ConstitutionHero`, `MandatesGrid`, and `Footer`. Includes `<svelte:head>` with per-page `<title>`, `<meta description>`, OG tags (`og:title`, `og:description`, `og:type`, `og:url`, `og:image`), Twitter card, and hreflang `<link>` alternates for all 3 locales + `x-default` using `i18n.resolveRoute("/constitution", locale)`. Wraps content in `<main id="main-content">`

**Checkpoint**: All 3 locale URLs render the Constitution page with 12 mandates, correct meta tags, and responsive layout. Footer link navigates to locale-correct Constitution page. Language switching works.

---

## Phase 4: User Story 3 — GitHub Transparency Link (Priority: P2)

**Goal**: Transparency section at the bottom of the Constitution page linking to the full CONSTITUTION.md on GitHub.

**Independent Test**: Scroll to transparency section, verify message text renders in current locale, verify GitHub link opens `https://github.com/renatobardi/the-loop/blob/main/CONSTITUTION.md` in new tab.

- [x] T009 [US3] Create `apps/web/src/lib/components/TransparencySection.svelte` — Section with `constitution_transparency_text()` and a link labeled `constitution_transparency_link()` pointing to `https://github.com/renatobardi/the-loop/blob/main/CONSTITUTION.md` (`target="_blank"`, `rel="noopener noreferrer"`). Uses `Section` and `Container` from `$lib/ui`
- [x] T010 [US3] Add `TransparencySection` to `apps/web/src/routes/constitution/+page.svelte` — insert between `MandatesGrid` and `Footer` (or before WaitlistCta if already added)

**Checkpoint**: Transparency section renders with correct locale text and functional GitHub link.

---

## Phase 5: User Story 4 — Waitlist CTA on Constitution Page (Priority: P2)

**Goal**: Waitlist signup form on the Constitution page with `source="constitution"` tracking, reusing existing `WaitlistCta` component.

**Independent Test**: Submit a valid email on the Constitution page. Verify success/duplicate/rate_limited responses. Check Firestore for `source: "constitution"` on new entry.

- [x] T011 [US4] Create `apps/web/src/routes/constitution/+page.server.ts` — Replicate waitlist form action from `src/routes/+page.server.ts`. Import `WaitlistSchema`, `waitlistLimiter`, `addToWaitlist`, `languageTag` from `$lib/server/` and `$lib/paraglide/runtime.js`. Same rate limit → Zod validation → Firestore write flow
- [x] T012 [US4] Add waitlist CTA to `apps/web/src/routes/constitution/+page.svelte` — import `WaitlistForm` from `$lib/components/WaitlistForm.svelte` (not `WaitlistCta`, which hardcodes `source="cta-bottom"`). Wrap in `Section` + `Container` with the same headline/subheadline pattern as `WaitlistCta.svelte`, passing `source="constitution"` to `WaitlistForm`. Insert between `TransparencySection` and `Footer`

**Checkpoint**: Waitlist form on Constitution page processes signups. Firestore entries show `source: "constitution"`.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quality checks, documentation, and CI readiness

- [x] T013 Run `npm run lint` from `apps/web/` and fix any issues
- [x] T014 Run `npm run check` from `apps/web/` and fix any TypeScript/Svelte errors
- [x] T015 Run `npm run build` from `apps/web/` and verify production build succeeds
- [x] T016 Run `bash scripts/generate-docs.sh` from repo root and update docs if needed — verify `git diff --exit-code` passes (Constitution XII compliance)
- [x] T017 Manual verification per `specs/005-constitution-page/quickstart.md` — all 3 locale URLs, footer link, waitlist form, responsive layout, and confirm wrong-locale slugs return 404 (e.g., `/en/constituicao/` must not resolve)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all component work (Paraglide needs compiled messages)
- **US1+US2 (Phase 3)**: Depends on Phase 2 — core MVP
- **US3 (Phase 4)**: Depends on Phase 3 (needs the page to exist) — can start after T008
- **US4 (Phase 5)**: Depends on Phase 3 (needs the page to exist) — can start after T008
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **US1+US2 (P1)**: Can start after Foundational — no dependencies on other stories
- **US3 (P2)**: Depends on US1 page existing (T008) — adds a section to it
- **US4 (P2)**: Depends on US1 page existing (T008) — adds CTA and form action
- **US3 and US4 can run in parallel** — they modify different parts of +page.svelte

### Within Phase 3

- T005 and T006 can run in parallel (different files)
- T007 depends on T005 (imports MandateCard)
- T008 depends on T006 and T007 (imports ConstitutionHero and MandatesGrid)

### Parallel Opportunities

```
Phase 2: T002 ║ T003 ║ T004  (3 message files in parallel)
Phase 3: T005 ║ T006          (MandateCard ║ ConstitutionHero)
         T007                  (MandatesGrid — needs T005)
         T008                  (Page — needs T006, T007)
Phase 4: T009 → T010
Phase 5: T011 ║ T012 can start after T008 (parallel with Phase 4)
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: i18n messages (T002–T004)
3. Complete Phase 3: Page + mandates (T005–T008)
4. **STOP and VALIDATE**: All 3 locale URLs render, 12 mandates display, responsive layout works
5. Deploy if ready — page is functional without transparency section or waitlist CTA

### Incremental Delivery

1. Setup + Foundational → Messages ready
2. Add US1+US2 → Constitution page live with mandates (MVP!)
3. Add US3 → Transparency section with GitHub link
4. Add US4 → Waitlist CTA for conversion
5. Polish → CI gates pass, docs updated

---

## Notes

- Footer.svelte needs NO changes — Paraglide auto-translates the existing `/constitution` link via pathnames config (FR-008 coverage by design decision D5)
- All new components must use design system tokens from `$lib/ui` and `app.css` — no ad-hoc styles (Constitution II)
- Commit after each task or logical group
