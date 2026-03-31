# Tasks: Complete i18n Audit & Fix

**Input**: Design documents from `/specs/003-i18n-audit-fix/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not requested — no test tasks included.

**Organization**: Tasks grouped by user story. Locale file updates are foundational (required by all stories). Component changes map to specific user stories.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `apps/web/` is the SvelteKit app root
- Locale files: `apps/web/messages/{en,pt,es}.json`
- Components: `apps/web/src/lib/components/` and `apps/web/src/lib/ui/`
- Layout: `apps/web/src/routes/+layout.svelte`

---

## Phase 1: Foundational (Locale File Updates)

**Purpose**: Add new i18n keys and translate all existing untranslated values. This phase MUST complete before component changes, since components will reference these keys.

- [x] T001 Add 3 new keys (`meta_title`, `meta_description`, `footer_language_selector_label`) with English values to `apps/web/messages/en.json`
- [x] T002 [P] Update `apps/web/messages/pt.json` — add 3 new keys with PT values + translate 15 existing keys that currently have English values (integration descriptions, pricing values, footer strings per data-model.md)
- [x] T003 [P] Update `apps/web/messages/es.json` — add 3 new keys with ES values + translate 15 existing keys that currently have English values (integration descriptions, pricing values, footer strings per data-model.md)

**Checkpoint**: All three locale files have identical key sets. PT and ES files contain zero untranslated English values (excluding intentionally English terms per FR-010).

---

## Phase 2: US1+US2 — Full PT/ES Page Translation (Priority: P1)

**Goal**: Portuguese and Spanish visitors see every visible string in their language — no English text leaks in components.

**Independent Test**: Navigate to `/pt/` and `/es/`, scroll through entire page. All pricing values, footer text, and integration descriptions display in the correct language.

### Implementation

- [x] T004 [P] [US1] Replace hardcoded `"The Loop"` text with `hero_product_name()` import in `apps/web/src/lib/components/Footer.svelte` (line 10)
- [x] T005 [P] [US1] Replace hardcoded `"The Loop"` text with `hero_product_name()` import in `apps/web/src/lib/ui/Navbar.svelte` (line 25)

**Checkpoint**: With locale file updates (Phase 1) + component fixes, `/pt/` and `/es/` show fully translated pages. The `hero_product_name` key has identical value ("The Loop") across all locales, so EN is unaffected.

---

## Phase 3: US3 — SEO hreflang Tags + Meta Tag i18n (Priority: P2)

**Goal**: Search engines discover all language versions via hreflang `<link>` tags. Meta title and description use the i18n system instead of hardcoded Record objects.

**Independent Test**: View page source on `/en/`, `/pt/`, `/es/` — verify `<title>` and `<meta name="description">` are localized, and 4 hreflang `<link>` tags are present.

### Implementation

- [x] T006 [US3] Replace hardcoded `titles` and `descriptions` Record objects with `meta_title()` and `meta_description()` i18n message imports in `apps/web/src/routes/+layout.svelte` — remove the `const titles` and `const descriptions` objects and use direct message function calls in the `<svelte:head>` block
- [x] T007 [US3] Add 4 hreflang `<link rel="alternate">` tags to the `<svelte:head>` block in `apps/web/src/routes/+layout.svelte` — for `en`, `pt`, `es`, and `x-default` with absolute URLs (`https://loop.oute.pro/{locale}/`)

**Checkpoint**: Page source shows localized meta tags and hreflang links on all locale routes.

---

## Phase 4: US5 — Language Selector Accessibility (Priority: P3)

**Goal**: The language selector's aria-label is localized — screen readers in PT/ES hear "Idioma" instead of "Language selector".

**Independent Test**: Inspect the language selector HTML on `/pt/` — the `aria-label` attribute reads "Idioma". On `/en/` it reads "Language".

### Implementation

- [x] T008 [US5] Replace hardcoded `aria-label="Language selector"` with `footer_language_selector_label()` i18n message import in both the `<nav>` and `<div>` variants in `apps/web/src/lib/components/LanguageSelector.svelte` (lines 20 and 35)

**Checkpoint**: Language selector announces correct localized label in all three languages.

---

## Phase 5: Polish & Validation

**Purpose**: Verify all changes pass CI gates and visual inspection.

- [x] T009 Run CI checks from `apps/web/`: `npm run check && npm run lint && npm run build && npm run test -- --run`
- [x] T010 Hardcoded string audit — grep `apps/web/src/` for common English phrases in `.svelte` files (e.g., "All rights reserved", "Contact us", "Join the waitlist", "Skip to main content") to confirm zero hardcoded strings that should come from locale files
- [x] T011 Visual verification — navigate to `/en/`, `/pt/`, `/es/` and confirm: all sections translated, no English leaks (excluding FR-010 terms), meta tags localized, hreflang tags present, language selector accessible

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Foundational)**: No dependencies — start immediately
  - T002 and T003 can run in parallel (different files)
  - T001 should complete first (EN is the source locale for Paraglide codegen)
- **Phase 2 (US1+US2)**: Depends on Phase 1 (new keys must exist for imports)
  - T004 and T005 can run in parallel (different files)
- **Phase 3 (US3)**: Depends on Phase 1 (meta_title/meta_description keys must exist)
  - T006 must complete before T007 (both modify same file, T006 restructures the script block)
- **Phase 4 (US5)**: Depends on Phase 1 (footer_language_selector_label key must exist)
- **Phase 5 (Polish)**: Depends on all previous phases

### User Story Dependencies

- **US1+US2 (P1)**: Depends on Foundational only — no cross-story dependencies
- **US3 (P2)**: Depends on Foundational only — independent of US1/US2
- **US5 (P3)**: Depends on Foundational only — independent of all other stories
- **US4 (P2 — regression)**: Verified implicitly by all other stories + Phase 5 validation

### Parallel Opportunities

- **Phase 1**: T002 and T003 can run in parallel after T001
- **Phase 2**: T004 and T005 can run in parallel
- **Phases 2, 3, 4**: Can all run in parallel after Phase 1 completes (different files)

---

## Parallel Example: After Phase 1

```text
# These can all run simultaneously (different files):
Task: T004 — Footer.svelte (Phase 2)
Task: T005 — Navbar.svelte (Phase 2)
Task: T006 — +layout.svelte (Phase 3)
Task: T008 — LanguageSelector.svelte (Phase 4)
```

---

## Implementation Strategy

### MVP First (US1+US2 — Full Translation)

1. Complete Phase 1: Locale file updates
2. Complete Phase 2: Hardcoded string removal
3. **STOP and VALIDATE**: `/pt/` and `/es/` are fully translated
4. This delivers the core value — complete i18n coverage

### Incremental Delivery

1. Phase 1 → Locale files ready
2. Phase 2 → Full translation (MVP!)
3. Phase 3 → SEO hreflang + meta tags
4. Phase 4 → Accessibility polish
5. Phase 5 → Final validation + CI

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All translation values are defined in `data-model.md` — reference it during implementation
- "GitHub" link text in Footer stays hardcoded (brand name per FR-010)
- FR-004 from spec was dropped (no row-label keys needed — card layout, see research.md R2)
- Commit after each phase for clean git history
