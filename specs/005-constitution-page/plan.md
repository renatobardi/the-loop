# Implementation Plan: Public Constitution Page

**Branch**: `005-constitution-page` | **Date**: 2026-03-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-constitution-page/spec.md`

## Summary

Create a dedicated, i18n Constitution page (`/en/constitution/`, `/pt/constituicao/`, `/es/constitucion/`) presenting the 12 engineering mandates as public-facing principles. Uses Paraglide's `pathnames` config for locale-specific slugs, the existing design system for visual consistency, and reuses the waitlist form action for conversion. All content is static i18n — no new database entities.

## Technical Context

**Language/Version**: TypeScript 5.x, Svelte 5 (runes), SvelteKit 2.50
**Primary Dependencies**: @inlang/paraglide-sveltekit 0.16.1, Tailwind CSS 4
**Storage**: N/A (static content page; waitlist reuses existing Firestore)
**Testing**: Vitest with jsdom
**Target Platform**: Web (Cloud Run, Node adapter)
**Project Type**: Web application (SvelteKit)
**Performance Goals**: N/A (static content page, no dynamic data)
**Constraints**: All text via i18n, design system tokens only, no ad-hoc styles
**Scale/Scope**: 1 new route, ~5 new components, ~30 new i18n keys per locale

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Mandamento | Status | Notes |
|------------|--------|-------|
| I. Trunk-Based Development | PASS | Feature branch `005-constitution-page`, will merge via PR |
| II. Design System Imutável | PASS | All components consume existing tokens from `app.css` and `lib/ui/` — no ad-hoc styles |
| III. Taxonomia de Branches | PASS | Branch uses numeric prefix matching spec directory |
| IV. Main Protegida | PASS | No direct pushes; PR required |
| V. Merge Controlado | PASS | @renatobardi sole approver |
| VI. Sem Ambiente de Dev | PASS | main = production |
| VII. CI Rigoroso | PASS | lint + type-check + test + build + Trivy + docs-check must pass |
| VIII. Segurança Mandatória | PASS | No new secrets, no new external APIs. Waitlist reuses existing rate limiting + Zod validation |
| IX. Clean Code | PASS | Small single-responsibility components, descriptive names, no dead code |
| X. Arquitetura Hexagonal | N/A | Phase 0 — hexagonal not applicable |
| XI. Pasta .project/ | PASS | Specs in `specs/005-constitution-page/` |
| XII. Documentação e Código | PASS | New route requires doc update — `scripts/generate-docs.sh` and README must stay current |

**Gate result**: PASS — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/005-constitution-page/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
apps/web/
├── src/
│   ├── lib/
│   │   ├── i18n.ts                          # MODIFY — add pathnames config
│   │   └── components/
│   │       ├── ConstitutionHero.svelte      # NEW — hero section
│   │       ├── MandateCard.svelte           # NEW — single mandate card
│   │       ├── MandatesGrid.svelte          # NEW — responsive 12-card grid
│   │       └── TransparencySection.svelte   # NEW — GitHub link block
│   └── routes/
│       └── constitution/
│           ├── +page.svelte                 # NEW — page composition + meta tags
│           └── +page.server.ts              # NEW — waitlist form action
└── messages/
    ├── en.json                              # MODIFY — add constitution_* keys
    ├── pt.json                              # MODIFY — add constitution_* keys
    └── es.json                              # MODIFY — add constitution_* keys
```

**Structure Decision**: Single canonical route at `src/routes/constitution/` with Paraglide `pathnames` handling locale slug translation. New components follow the existing pattern in `src/lib/components/` — page-section components that compose `lib/ui/` primitives.

## Design Decisions

### D1: Paraglide Pathnames for Localized Slugs

Use the `pathnames` option in `createI18n()` to map `/constitution` → `/constituicao` (PT) and `/constitucion` (ES). The existing `reroute` hook handles everything automatically. See [research.md](./research.md#r1-localized-url-slugs-via-paraglide-pathnames).

### D2: Separate Components per Section

Each page section is its own component (`ConstitutionHero`, `MandatesGrid`, `MandateCard`, `TransparencySection`), matching the landing page's composition pattern. `WaitlistCta` and `Footer` are reused directly.

### D3: Replicated Form Action

The Constitution route gets its own `+page.server.ts` with a `waitlist` action wiring the same `$lib/server/` modules. No shared abstraction — 2 routes is not enough to justify extraction. See [research.md](./research.md#r2-waitlist-form-action-on-constitution-route).

### D4: Per-Page Meta Override

The Constitution page uses `<svelte:head>` to override the root layout's title, description, OG, and hreflang tags with constitution-specific i18n messages. See [research.md](./research.md#r3-per-page-meta-tags).

### D5: Footer Link — No Change Needed

The Footer already links to `/constitution`. Paraglide's `ParaglideJS` wrapper auto-translates this to the correct locale slug via the new `pathnames` config. See [research.md](./research.md#r5-footer-constitution-link).

## Complexity Tracking

No violations to justify — all gates pass.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none)    | —          | —                                   |
