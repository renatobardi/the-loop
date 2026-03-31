# Implementation Plan: Waitlist Source Tracking + Pricing CTAs

**Branch**: `004-waitlist-pricing-ctas` | **Date**: 2026-03-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-waitlist-pricing-ctas/spec.md`

## Summary

Add differentiated source tracking (`"hero"` / `"cta-bottom"`) to the waitlist signup flow. The current implementation hardcodes `source: 'landing'` for all submissions. This change threads a `source` prop through `WaitlistForm` → hidden field → server action → `addToWaitlist()` → Firestore. Pricing card CTAs, badges, i18n keys, and accessible labels already exist — this plan verifies them and adds unit test coverage.

## Technical Context

**Language/Version**: TypeScript 5.x, Svelte 5 (runes)
**Primary Dependencies**: SvelteKit 2.50, @inlang/paraglide-sveltekit 0.16.1, Tailwind CSS 4, Zod, firebase-admin
**Storage**: Firestore (project: `theloopoute`, collection: `waitlist`)
**Testing**: Vitest with jsdom environment, `$lib`/`$app` path aliases
**Target Platform**: GCP Cloud Run (adapter-node), browser
**Project Type**: Web application (SvelteKit SSR + CSR)
**Performance Goals**: N/A — no new endpoints or heavy processing
**Constraints**: Rate limiting 5 req/60s per IP (existing), Zod validation (existing)
**Scale/Scope**: Landing page, ~100s of waitlist signups — minimal scale

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Mandamento | Status | Notes |
|------------|--------|-------|
| I. Trunk-Based Development | PASS | Feature branch → PR → main |
| II. Design System Imutável | PASS | Uses existing Button variants and Badge from `lib/ui/` — no new tokens |
| III. Taxonomia de Branches | PASS | `004-waitlist-pricing-ctas` follows speckit numeric prefix convention |
| IV. Main Protegida | PASS | No direct push to main |
| V. Merge Controlado | PASS | @renatobardi merges |
| VI. Sem Ambiente de Dev | PASS | Single production environment |
| VII. CI Rigoroso | PASS | All gates (lint, type-check, test, build, vuln scan, docs-check) will run |
| VIII. Segurança Mandatória | PASS | Server-side Zod validation of source field against allowlist; rate limiting unchanged |
| IX. Clean Code | PASS | Small, focused changes; source allowlist as named constant |
| X. Arquitetura Hexagonal | N/A | Phase 0 — hexagonal not applicable |
| XI. Pasta .project/ | N/A | No .project/ changes needed |
| XII. Documentação e Código | PASS | Minimal structural change; docs-check CI gate will verify |

**Gate result**: PASS — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/004-waitlist-pricing-ctas/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── spec.md              # Feature specification
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code (repository root)

```text
apps/web/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   ├── WaitlistForm.svelte    # ADD: source prop + hidden input
│   │   │   ├── Hero.svelte            # MODIFY: pass source="hero" to WaitlistForm
│   │   │   ├── WaitlistCta.svelte     # MODIFY: pass source="cta-bottom" to WaitlistForm
│   │   │   └── Pricing.svelte         # VERIFY: existing CTAs, badge, i18n
│   │   ├── server/
│   │   │   ├── schemas.ts             # MODIFY: add source to WaitlistSchema
│   │   │   └── waitlist.ts            # MODIFY: accept source param, remove hardcoded value
│   │   └── ui/
│   │       └── Input.svelte           # VERIFY: sr-only label already works
│   ├── routes/
│   │   └── +page.server.ts            # MODIFY: extract source from form data
│   └── app.css                        # NO CHANGE
├── messages/
│   ├── en.json                        # VERIFY: all keys present
│   ├── pt.json                        # VERIFY: all keys present
│   └── es.json                        # VERIFY: all keys present
└── tests/unit/
    └── server.test.ts                 # MODIFY: add source tracking tests
```

**Structure Decision**: All changes within existing `apps/web/` monorepo structure. No new files created — 6 files touched: 5 modified (schemas.ts, waitlist.ts, +page.server.ts, WaitlistForm.svelte, server.test.ts) + Hero.svelte and WaitlistCta.svelte updated to pass the new `source` prop. Pricing.svelte, Input.svelte, and i18n JSON files are verification-only (no changes expected).

## Complexity Tracking

> No violations to justify — Constitution Check passed clean.
