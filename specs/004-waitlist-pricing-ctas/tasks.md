# Tasks: Waitlist Source Tracking + Pricing CTAs

**Input**: Design documents from `/specs/004-waitlist-pricing-ctas/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested — test tasks included only for the new source tracking logic (US1), which changes server behavior.

**Organization**: Tasks grouped by user story. US1 is the only story with new code; US2–US4 are verification of existing functionality.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new project setup needed — all infrastructure exists. This phase is a no-op.

**Checkpoint**: Ready to proceed to foundational changes.

---

## Phase 2: Foundational (Schema + Service Layer)

**Purpose**: Extend the Zod schema and Firestore write function to accept `source`. These changes block all user story work.

**CRITICAL**: No user story work can begin until this phase is complete.

- [x] T001 Add `VALID_SOURCES` constant and extend `WaitlistSchema` with optional `source` field (validated against allowlist, defaults to `"unknown"` per FR-010) in `apps/web/src/lib/server/schemas.ts`
- [x] T002 Change `addToWaitlist` signature to accept `source: string` parameter and use it instead of hardcoded `'landing'` in `apps/web/src/lib/server/waitlist.ts`
- [x] T003 Extract `source` from form data, include in Zod parse input, and pass `result.data.source` to `addToWaitlist()` in `apps/web/src/routes/+page.server.ts`

**Checkpoint**: Server-side source tracking pipeline complete. Forms still send no source (defaults to `"unknown"` until Phase 3).

---

## Phase 3: User Story 1 — Differentiated Source Tracking (Priority: P1) MVP

**Goal**: Each waitlist form sends its source identifier so Firestore records where signups originate.

**Independent Test**: Submit emails from Hero and Section 7 forms → verify correct `source` values in Firestore.

### Implementation for User Story 1

- [x] T004 [US1] Add `source` prop (type: `string`, default: `"unknown"`) and render `<input type="hidden" name="source" value={source} />` inside the form in `apps/web/src/lib/components/WaitlistForm.svelte`
- [x] T005 [P] [US1] Pass `source="hero"` to `<WaitlistForm>` in `apps/web/src/lib/components/Hero.svelte`
- [x] T006 [P] [US1] Pass `source="cta-bottom"` to `<WaitlistForm>` in `apps/web/src/lib/components/WaitlistCta.svelte`

### Tests for User Story 1

- [x] T007 [US1] Add unit tests for source tracking in `apps/web/tests/unit/server.test.ts`: (1) valid source `"hero"` passes schema, (2) valid source `"cta-bottom"` passes schema, (3) missing source defaults to `"unknown"`, (4) invalid source defaults to `"unknown"`

**Checkpoint**: Source tracking is fully functional. Submitting from Hero records `source: "hero"`, from Section 7 records `source: "cta-bottom"`.

---

## Phase 4: User Story 2 — Pricing Card CTAs Link to Waitlist (Priority: P2)

**Goal**: Verify that pricing card CTAs already link to `#waitlist` with correct button variants and badge.

**Independent Test**: Click CTAs on Free and PAYG pricing cards → page scrolls to `#waitlist` section.

### Implementation for User Story 2

- [x] T008 [US2] Verify and confirm in `apps/web/src/lib/components/Pricing.svelte` that: (1) Free card has secondary CTA linking to `#waitlist`, (2) PAYG card has primary CTA linking to `#waitlist`, (3) PAYG card displays "Most popular" badge, (4) Enterprise card has "Contact us" linking to `mailto:loop@oute.pro`

**Checkpoint**: All pricing cards have functional CTAs with correct variants.

---

## Phase 5: User Story 3 — Accessible Waitlist Forms (Priority: P2)

**Goal**: Verify that both waitlist forms have accessible sr-only labels announced by screen readers.

**Independent Test**: Screen reader announces email input label in the active locale on both forms.

### Implementation for User Story 3

- [x] T009 [US3] Verify and confirm in `apps/web/src/lib/components/WaitlistForm.svelte` that `Input` receives `label={form_email_label()}` and in `apps/web/src/lib/ui/Input.svelte` that the `<label>` has `class="sr-only"` and `for={inputId}`

**Checkpoint**: Both waitlist forms are accessible via screen reader.

---

## Phase 6: User Story 4 — Full i18n Coverage (Priority: P2)

**Goal**: Verify all user-facing strings exist in EN, PT-BR, and ES message files.

**Independent Test**: Switch to each locale and verify all strings render correctly.

### Implementation for User Story 4

- [x] T010 [US4] Verify the following keys exist and are correctly translated in `apps/web/messages/en.json`, `apps/web/messages/pt.json`, and `apps/web/messages/es.json`: `pricing_join_waitlist`, `pricing_popular_badge`, `pricing_contact_cta`, `form_email_label`, `form_success`, `form_duplicate`, `form_rate_limited`, `form_server_error`, `form_submit`, `form_submitting`, `hero_email_placeholder`. Document any missing keys and add if needed.

**Checkpoint**: All strings render correctly in all three locales.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation across all stories.

- [x] T011 Run `npm run check` (TypeScript strict) in `apps/web/`
- [x] T012 Run `npm run lint` (ESLint + Prettier) in `apps/web/`
- [x] T013 Run `npm run test -- --run` (all unit tests) in `apps/web/`
- [x] T014 Run `npm run build` (production build) in `apps/web/`
- [x] T015 Run quickstart.md manual validation steps (requires `FIREBASE_SERVICE_ACCOUNT` env var for Firestore verification)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No-op — skip
- **Foundational (Phase 2)**: T001 → T002 → T003 (sequential — each depends on prior)
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion. T004 first, then T005+T006 in parallel, then T007.
- **User Stories 2–4 (Phases 4–6)**: Independent of each other and of US1. Can run in parallel after Phase 2.
- **Polish (Phase 7)**: Depends on all stories complete. T011–T014 can run sequentially as CI pipeline.

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational (Phase 2) — the only story with new code
- **User Story 2 (P2)**: No code dependencies — verification only
- **User Story 3 (P2)**: No code dependencies — verification only
- **User Story 4 (P2)**: No code dependencies — verification only

### Parallel Opportunities

- T005 and T006 can run in parallel (different files)
- T008, T009, T010 can all run in parallel (verification tasks on different files)
- T011–T014 are CI gates, run sequentially

---

## Parallel Example: User Story 1

```bash
# After T004 (WaitlistForm source prop), launch in parallel:
Task T005: "Pass source='hero' to WaitlistForm in Hero.svelte"
Task T006: "Pass source='cta-bottom' to WaitlistForm in WaitlistCta.svelte"
```

## Parallel Example: Verification Stories (after Phase 2)

```bash
# All verification stories can run in parallel:
Task T008: "Verify Pricing card CTAs"
Task T009: "Verify accessible labels"
Task T010: "Verify i18n coverage"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (T001–T003)
2. Complete Phase 3: User Story 1 (T004–T007)
3. **STOP and VALIDATE**: Submit emails from both forms, verify source in Firestore
4. Run CI gates (T011–T014)
5. Deploy — source tracking is live

### Incremental Delivery

1. Phase 2 → Foundational ready
2. Phase 3 → Source tracking works (MVP!)
3. Phases 4–6 → Verify existing features, fix any gaps
4. Phase 7 → CI gates pass, ready for PR

---

## Notes

- This feature is unusually small: **5 files to modify** (schemas.ts, waitlist.ts, +page.server.ts, WaitlistForm.svelte, server.test.ts) + **2 files to update** (Hero.svelte, WaitlistCta.svelte) with the new `source` prop
- US2–US4 are primarily **verification** of existing functionality, not new code
- The `VALID_SOURCES` constant prevents magic strings (Constitution IX)
- Source validation uses Zod transform with fallback, not rejection (better UX for tampered inputs)
