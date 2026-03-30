# Tasks: Landing Page & Waitlist

**Input**: Design documents from `/specs/001-landing-page-waitlist/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Included — Constitution Mandamento VII requires vitest tests to pass in CI.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `apps/web/src/` (SvelteKit landing page)
- **Server modules**: `apps/web/src/lib/server/`
- **Design system**: `apps/web/src/lib/ui/`
- **Components**: `apps/web/src/lib/components/`
- **i18n messages**: `apps/web/src/lib/i18n/messages/`
- **Routes**: `apps/web/src/routes/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, monorepo scaffolding, CI/CD pipeline, constitutional mandates

- [x] T001 Initialize SvelteKit project with adapter-node in `apps/web/` (npm create svelte, TypeScript strict, adapter-node in `svelte.config.js`)
- [x] T002 Configure Tailwind CSS 4 in `apps/web/tailwind.config.ts` and `apps/web/src/app.css`
- [x] T003 [P] Install and configure Paraglide-SvelteKit (`npx sv add paraglide`) with locales en/pt/es in `apps/web/`
- [x] T004 [P] Install production dependencies: `firebase-admin`, `zod`, `rate-limiter-flexible` in `apps/web/`
- [x] T005 [P] Install dev dependencies: `vitest`, `@testing-library/svelte`, `playwright` in `apps/web/`
- [x] T006 [P] Configure ESLint + Prettier in `apps/web/` with strict rules
- [x] T007 [P] Configure TypeScript strict mode in `apps/web/tsconfig.json`
- [x] T008 [P] Create `.github/CODEOWNERS` with `* @renatobardi`
- [x] T009 [P] Create `CONSTITUTION.md` at repo root (copy from `.specify/memory/constitution.md` with proper formatting)
- [x] T010 Create GitHub Actions CI workflow in `.github/workflows/ci.yml` (lint → type-check → test → build → vuln scan with trivy → docs-check)
- [x] T011 Create GitHub Actions deploy workflow in `.github/workflows/deploy.yml` (WIF auth → Docker build → push to Artifact Registry → deploy to Cloud Run on merge to main)
- [x] T012 [P] Create `apps/web/Dockerfile` (3-stage: deps → build → runner, node:22-alpine, non-root UID 1001)
- [x] T013 [P] Create `apps/web/.dockerignore` (exclude .git, node_modules, .svelte-kit, build, specs, .specify, .claude, *.md)
- [x] T014 [P] Create `.project/phases/00-landing/` directory structure with placeholder spec.md, plan.md, and `decisions/` directory
- [x] T015 [P] Create `scripts/generate-docs.sh` for docs-check CI gate (Constitution Mandamento XII)
- [x] T016 [P] Create `firestore.rules` at repo root with write-only waitlist collection rules (create only, no read/update/delete, field validation)

**Checkpoint**: Project builds, CI pipeline runs (may have no tests yet), Docker builds successfully.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Design system, server infrastructure, security headers, i18n framework — MUST complete before any user story

- [x] T017 Define design tokens in `apps/web/tailwind.config.ts`: colors (bg: near-black, text: white/gray, accent: #0066FF), typography (Geist font, bold weights), spacing scale, border-radius, shadows
- [x] T018 [P] Add Geist font files to `apps/web/static/fonts/` and configure @font-face in `apps/web/src/app.css`
- [x] T019 Create Button component (primary, secondary, ghost variants) in `apps/web/src/lib/ui/Button.svelte` using only design tokens
- [x] T020 [P] Create Input component (text, email variants) in `apps/web/src/lib/ui/Input.svelte` using only design tokens
- [x] T021 [P] Create Card component in `apps/web/src/lib/ui/Card.svelte` using only design tokens
- [x] T022 [P] Create Badge component in `apps/web/src/lib/ui/Badge.svelte` using only design tokens
- [x] T023 [P] Create Container component in `apps/web/src/lib/ui/Container.svelte` using only design tokens
- [x] T024 [P] Create Section component (full-viewport-height wrapper) in `apps/web/src/lib/ui/Section.svelte` using only design tokens
- [x] T025 Create barrel export in `apps/web/src/lib/ui/index.ts`
- [x] T026 Implement security headers in `apps/web/src/hooks.server.ts`: HSTS (2yr, includeSubDomains, preload), X-Frame-Options: DENY, X-Content-Type-Options: nosniff, Referrer-Policy: strict-origin-when-cross-origin, Permissions-Policy, CSP (self + googleapis.com), CORS (explicit origins only, no wildcard `*`)
- [x] T027 [P] Create Firebase Admin SDK singleton in `apps/web/src/lib/server/firebase.ts` (ADC for Cloud Run, env var for local dev, `getApps()` guard)
- [x] T028 [P] Create Zod validation schema for waitlist in `apps/web/src/lib/server/schemas.ts` (email: trim, lowercase, email format, max 254)
- [x] T029 [P] Create rate limiter singleton in `apps/web/src/lib/server/rateLimiter.ts` (RateLimiterMemory, 5 points / 60s)
- [x] T030 Create waitlist service in `apps/web/src/lib/server/waitlist.ts` (addToWaitlist: duplicate check via doc.get(), set with serverTimestamp, returns 'created' | 'duplicate')
- [x] T031 Create locale param matcher in `apps/web/src/params/lang.ts` (validate param is 'en', 'pt', or 'es')
- [x] T032 Add root redirect and unsupported locale handling in `apps/web/src/hooks.server.ts` (/ → /en/, /fr/ → /en/)
- [x] T033 Create root layout in `apps/web/src/routes/+layout.svelte` with dark mode base styles, Geist font, hreflang tags
- [x] T034 Create `[lang]` layout in `apps/web/src/routes/[lang]/+layout.svelte` with localized meta tags (title, description, og:*) and Paraglide context
- [x] T035 [P] Create EN translation messages in `apps/web/src/lib/i18n/messages/en.json` (all 8 sections: hero, problem, layers, howItWorks, integrations, pricing, waitlistCta, footer + common UI strings)
- [x] T036 [P] Create unit tests for design system components in `apps/web/tests/unit/ui.test.ts` (render each component, verify token usage)
- [x] T037 [P] Create unit tests for server modules in `apps/web/tests/unit/server.test.ts` (Zod schema validation, rate limiter behavior)

**Checkpoint**: Design system renders, security headers present, Firebase connected, i18n framework operational with EN locale, all unit tests pass.

---

## Phase 3: User Story 1 — Understand Value Proposition (Priority: P1)

**Goal**: Visitor understands what The Loop does in under 60 seconds from the hero section.

**Independent Test**: Have a developer visit the page and describe what The Loop does after reading the hero.

### Implementation for User Story 1

- [x] T038 [US1] Create Hero section component in `apps/web/src/lib/components/Hero.svelte` (headline, sub-headline, waitlist CTA placeholder, "by Oute" branding)
- [x] T039 [P] [US1] Create Problem section component in `apps/web/src/lib/components/Problem.svelte` (headline + body text)
- [x] T040 [P] [US1] Create HowItWorks section component in `apps/web/src/lib/components/HowItWorks.svelte` (headline, textual flow description: Incident → KB → Rule/Advisory → Code Protected → Loop Closes, body text — SVG diagram deferred to T062)
- [x] T041 [P] [US1] Create Footer component in `apps/web/src/lib/components/Footer.svelte` (logo "The Loop — by Oute", links: GitHub, Constitution, Contact loop@oute.pro, copyright, language selector)
- [x] T042 [US1] Create landing page in `apps/web/src/routes/[lang]/+page.svelte` assembling Hero, Problem, HowItWorks, Footer sections with Section wrappers
- [x] T043 [US1] Visual smoke check: verify Hero, Problem, HowItWorks, Footer render correctly and no elements are visually broken

**Checkpoint**: Landing page loads at /en/ with Hero, Problem, HowItWorks, Footer. Visitor can read and understand the value proposition. Page is responsive.

---

## Phase 4: User Story 2 — Join the Waitlist (Priority: P1)

**Goal**: Developer can submit email to waitlist and see confirmation. Duplicates and rate limiting handled.

**Independent Test**: Submit valid email → confirmation. Submit same email → "already on the list". Submit 6 times → rate limit message. Invalid email → validation error.

### Implementation for User Story 2

- [x] T044 [US2] Create WaitlistForm component in `apps/web/src/lib/components/WaitlistForm.svelte` (email input + submit button, client-side validation, success/error/duplicate/rate-limit states, use:enhance for progressive enhancement)
- [x] T045 [US2] Create WaitlistCta section component in `apps/web/src/lib/components/WaitlistCta.svelte` (headline "Be the first to close the loop", sub-headline, WaitlistForm)
- [x] T046 [US2] Implement waitlist form action in `apps/web/src/routes/[lang]/+page.server.ts` (action `?/waitlist`: extract IP, Zod validate, rate limit check, Firestore duplicate check, Firestore write, return success/fail responses per contracts/waitlist-api.md. Handle Firestore outage with try/catch — return fail(500, { error: 'server_error' }) and friendly message "Something went wrong. Please try again.")
- [x] T047 [US2] Integrate WaitlistForm into Hero section in `apps/web/src/lib/components/Hero.svelte` (email input + submit below sub-headline)
- [x] T048 [US2] Add WaitlistCta section to landing page in `apps/web/src/routes/[lang]/+page.svelte` (between Pricing and Footer)
- [x] T049 [P] [US2] Create unit tests for waitlist form action in `apps/web/tests/unit/waitlist.test.ts` (valid email, invalid email, duplicate, rate limit scenarios)

**Checkpoint**: Waitlist form works in Hero and CTA sections. Emails stored in Firestore. Duplicates, validation, and rate limiting all functional.

---

## Phase 5: User Story 3 — Explore Detection Layers (Priority: P2)

**Goal**: Developer can see and understand the 3 detection layers with visual distinction between blocking, consultive, and progressive behaviors.

**Independent Test**: Developer can describe what each layer does after scanning the section.

### Implementation for User Story 3

- [x] T050 [US3] Create Layers section component in `apps/web/src/lib/components/Layers.svelte` (headline "Three layers. Zero blind spots.", 3 layer cards with Label badges: "Layer 1 · Blocking", "Layer 2 · Consultive", "Layer 3 · Progressive", distinct visual treatment per layer)
- [x] T051 [US3] Add Layers section to landing page in `apps/web/src/routes/[lang]/+page.svelte` (between Problem and HowItWorks)

**Checkpoint**: Layers section renders with clear visual distinction between the 3 layers. Headlines convey the gist without reading body text.

---

## Phase 6: User Story 5 + User Story 6 — Pricing & Integrations (Priority: P3)

**Goal**: Manager understands pricing model and supported integrations.

**Independent Test**: Manager can describe pricing tiers and list supported platforms.

### Implementation for User Story 5

- [x] T052 [US5] Create Pricing section component in `apps/web/src/lib/components/Pricing.svelte` (headline "Start free. Pay as you grow.", 3 pricing cards: Free/$0/100 scans, Pay-as-you-go/per batch, Enterprise/Contact us with mailto:loop@oute.pro)

### Implementation for User Story 6

- [x] T053 [P] [US6] Create Integrations section component in `apps/web/src/lib/components/Integrations.svelte` (headline "Works where you work.", 3 integration items: GitHub App, IDEs via MCP, GitLab/Bitbucket/Jenkins REST API — each with SVG icon and one-line description)

### Assembly

- [x] T054 Add Integrations and Pricing sections to landing page in `apps/web/src/routes/[lang]/+page.svelte` (Integrations after HowItWorks, Pricing after Integrations, before WaitlistCta)

**Checkpoint**: All 8 sections now visible on the landing page in correct order: Hero, Problem, Layers, HowItWorks, Integrations, Pricing, WaitlistCta, Footer.

---

## Phase 7: User Story 4 — Read in Preferred Language (Priority: P2)

**Goal**: All page content available in EN, PT-BR, and ES with route-based locale switching.

**Independent Test**: Navigate to /pt/ → all text in Portuguese. Share /pt/ URL → loads in Portuguese.

### Implementation for User Story 4

- [x] T055 [US4] Create PT-BR translation messages in `apps/web/src/lib/i18n/messages/pt.json` (all sections + UI strings, matching en.json keys)
- [x] T056 [P] [US4] Create ES translation messages in `apps/web/src/lib/i18n/messages/es.json` (all sections + UI strings, matching en.json keys)
- [x] T057 [US4] Create LanguageSelector component in `apps/web/src/lib/components/LanguageSelector.svelte` (language codes EN/PT/ES with localizeHref, data-sveltekit-reload for locale switch)
- [x] T058 [US4] Integrate LanguageSelector into page header/nav area in `apps/web/src/routes/[lang]/+layout.svelte` and into Footer
- [x] T059 [US4] Add localized meta tags (og:title, og:description, og:url, twitter:card) per locale in `apps/web/src/routes/[lang]/+layout.svelte`
- [x] T060 [US4] Verify all visible text is localized — no hardcoded strings — by switching to /pt/ and /es/ and checking every section

**Checkpoint**: Page fully localized in 3 languages. URL reflects locale. Shared locale URLs work. No hardcoded strings.

---

## Phase 8: User Story 7 — Fast and Premium Experience (Priority: P2)

**Goal**: Page loads fast (LCP < 2.5s), animations smooth (60fps), fully responsive.

**Independent Test**: Lighthouse audit shows LCP < 2.5s. Scroll animations smooth. No broken elements on mobile.

### Implementation for User Story 7

- [x] T061 [US7] Add CSS scroll-triggered fade-in/slide-up animations to all Section components in `apps/web/src/lib/ui/Section.svelte` (CSS-only, respect `prefers-reduced-motion`)
- [x] T062 [US7] Replace textual flow in HowItWorks with SVG diagram in `apps/web/src/lib/components/HowItWorks.svelte` (Incident → KB → Rule/Advisory → Code Protected → Loop Closes, accent color highlights, responsive on all breakpoints)
- [x] T063 [US7] Optimize font loading: preload Geist font, use `font-display: swap` in `apps/web/src/app.css`
- [x] T064 [US7] Verify responsive design on all breakpoints (375px, 768px, 1280px) — fix spacing, typography scale, section heights
- [x] T065 [US7] Run Lighthouse audit, optimize for LCP < 2.5s (preload critical resources, minimize CLS, optimize images/SVGs)

**Checkpoint**: LCP < 2.5s, animations at 60fps respecting reduced-motion, fully responsive across all breakpoints.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, deployment, final validation

- [ ] T066 Create README.md at repo root (project description, setup instructions, architecture overview, link to CONSTITUTION.md)
- [ ] T067 [P] Copy spec.md, plan.md, and tasks.md to `.project/phases/00-landing/` (Constitution Mandamento XI)
- [ ] T068 [P] Add social meta tags (Open Graph, Twitter Card) with OG image as SVG/static asset in `apps/web/src/routes/[lang]/+layout.svelte`
- [ ] T069 Validate docs-check CI gate: run `scripts/generate-docs.sh` and verify `git diff --exit-code` passes
- [ ] T070 Validate all CI gates pass end-to-end: lint, type-check, test, build, vuln scan, docs-check
- [ ] T071 Configure Cloud Run deployment: Artifact Registry repo, WIF pool/provider, deployer service account, IAM roles (run.admin, artifactregistry.writer, datastore.user)
- [ ] T072 Configure Cloud Run domain: Global LB + Serverless NEG + Google-managed SSL cert for loop.oute.pro, HTTP→HTTPS redirect
- [ ] T073 Deploy to production via merge to main — verify loop.oute.pro serves the landing page
- [ ] T074 Post-deploy validation: Lighthouse audit on production, security headers check, waitlist form end-to-end test on production, verify all 3 locales work

**Checkpoint**: Production deploy complete. loop.oute.pro live. All constitutional mandates enforced. Ready for waitlist collection.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — Hero + Problem + HowItWorks
- **US2 (Phase 4)**: Depends on Foundational + US1 (Hero must exist to embed waitlist form)
- **US3 (Phase 5)**: Depends on Foundational — can run in parallel with US1
- **US5+US6 (Phase 6)**: Depends on Foundational — can run in parallel with US1/US3
- **US4 (Phase 7)**: Depends on ALL content phases (US1, US2, US3, US5, US6) — needs all EN text to exist before translating
- **US7 (Phase 8)**: Depends on ALL content phases — needs all sections to exist before polishing animations/performance
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: After Foundational — no dependencies on other stories
- **US2 (P1)**: After Foundational + US1 (Hero section must exist for embedded form)
- **US3 (P2)**: After Foundational — independent of US1/US2
- **US5+US6 (P3)**: After Foundational — independent of other stories
- **US4 (P2)**: After US1+US2+US3+US5+US6 — all EN content must exist
- **US7 (P2)**: After US1+US2+US3+US5+US6 — all sections must exist

### Parallel Opportunities

- T003, T004, T005, T006, T007, T008, T009, T012, T013, T014, T015, T016 — all Setup [P] tasks
- T018, T019-T024 — font + all UI components in parallel
- T027, T028, T029, T035, T036, T037 — server modules + translations + tests
- T039, T040, T041 — Problem, HowItWorks, Footer in parallel
- T050 + T052 + T053 — Layers + Pricing + Integrations in parallel (different files)
- T055, T056 — PT-BR and ES translations in parallel

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: US1 — Value Proposition (Hero, Problem, HowItWorks, Footer)
4. Complete Phase 4: US2 — Waitlist Form (form action, Firebase, rate limiting)
5. **STOP and VALIDATE**: Landing page communicates vision + collects emails
6. Deploy MVP if ready — English-only landing page with waitlist

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 → Hero/Problem/HowItWorks/Footer → Validate independently
3. US2 → Waitlist working → Deploy MVP
4. US3 → Layers section → Deploy
5. US5+US6 → Pricing + Integrations → Deploy (all 8 sections complete)
6. US4 → i18n (PT-BR + ES) → Deploy
7. US7 → Animations + Performance → Deploy
8. Polish → Docs, production domain, final audit → Launch

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Verify tests pass after each phase
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
