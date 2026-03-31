# Implementation Plan: Landing Page Design Polish

**Branch**: `002-landing-page-polish` | **Date**: 2026-03-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-landing-page-polish/spec.md`

## Summary

Comprehensive design polish of The Loop landing page addressing 12 items from a design critique: fix language selector routing bug, add product branding to hero, improve accessibility (labels, skip link, contrast, heading hierarchy), reduce section spacing for narrative flow, add pricing card CTAs with visual hierarchy, add sticky navigation with hamburger menu on mobile, and standardize alignment/card styling across sections. All changes are CSS/component-level within the existing SvelteKit + Tailwind + Paraglide stack.

## Technical Context

**Language/Version**: TypeScript 5.x, Svelte 5 (runes), SvelteKit 2.50
**Primary Dependencies**: Tailwind CSS 4, Paraglide-SvelteKit 0.16.1, Svelte 5 snippets/actions
**Storage**: N/A (no data model changes)
**Testing**: vitest (unit), manual Lighthouse audit, manual screen reader testing
**Target Platform**: Web (all modern browsers, responsive 320px–2560px)
**Project Type**: Web application (SvelteKit, SSR + client hydration)
**Performance Goals**: Lighthouse Accessibility 90+, all text WCAG AA compliant
**Constraints**: No new npm dependencies; all changes within existing design system tokens
**Scale/Scope**: Single-page landing, ~8 section components + 4 UI components modified, ~3 new components created

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Mandamento | Status | Notes |
|------------|--------|-------|
| I. Trunk-Based Development | PASS | Working on feature branch `002-landing-page-polish`, will merge via PR |
| II. Design System Imutavel | PASS | All changes use existing tokens from `app.css`; new color token `--color-text-subtle` value adjustment stays within design system. New components (Navbar, SkipLink) follow design system patterns |
| III. Taxonomia de Branches | PASS | Branch follows `feat/` equivalent pattern via speckit numbering |
| IV. Main Protegida | PASS | Will merge via PR with CI gates |
| V. Aprovacao Obrigatoria | PASS | @renatobardi will review and merge |
| VI. Sem Ambiente de Dev | PASS | Changes go to production via main |
| VII. CI Rigoroso | PASS | Must pass lint, type-check, test, build, vuln scan, docs-check |
| VIII. Seguranca Mandatoria | PASS | No new attack surface; CSP headers unchanged; skip link is purely presentational |
| IX. Clean Code | PASS | Small focused components, descriptive names, no dead code |
| X. Arquitetura Hexagonal | N/A | Phase 0 — hexagonal does not apply |
| XI. Pasta .project/ | PASS | Specs tracked in `specs/002-landing-page-polish/` |
| XII. Documentacao e Codigo | PASS | Will update README if structural changes warrant it |

**Gate result**: ALL PASS — proceed to Phase 0.

**Post-Phase 1 re-check**: All gates remain PASS. No new dependencies, no hexagonal violations, design system extended (not bypassed) with new `--color-text-muted` value and Navbar component.

## Project Structure

### Documentation (this feature)

```text
specs/002-landing-page-polish/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (minimal — no data changes)
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A — no external interfaces)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
apps/web/src/
├── lib/
│   ├── ui/
│   │   ├── Section.svelte       # MODIFY: remove min-h-screen, adjust padding
│   │   ├── Input.svelte         # MODIFY: add optional label prop (sr-only)
│   │   ├── Card.svelte          # EXISTING: no changes needed (unified styling already)
│   │   ├── Badge.svelte         # EXISTING: no changes needed
│   │   ├── Button.svelte        # EXISTING: no changes needed
│   │   ├── Container.svelte     # EXISTING: no changes needed
│   │   ├── SkipLink.svelte      # CREATE: skip-to-content accessibility link
│   │   ├── Navbar.svelte        # CREATE: sticky nav with hamburger menu
│   │   └── index.ts             # MODIFY: export new components
│   └── components/
│       ├── Hero.svelte          # MODIFY: add product name, scroll indicator
│       ├── Problem.svelte       # MODIFY: center heading alignment
│       ├── Layers.svelte        # MODIFY: center heading alignment (likely already centered)
│       ├── HowItWorks.svelte    # MODIFY: center heading alignment
│       ├── Integrations.svelte  # EXISTING: verify heading centered
│       ├── Pricing.svelte       # MODIFY: add CTAs, highlight Pay-as-you-go, center heading
│       ├── WaitlistCta.svelte   # MODIFY: verify heading centered
│       ├── WaitlistForm.svelte  # MODIFY: pass label to Input
│       ├── LanguageSelector.svelte  # MODIFY: increase touch targets, change to div for footer
│       └── Footer.svelte        # MODIFY: fix nav nesting
├── routes/
│   ├── +layout.svelte       # MODIFY: add Navbar + SkipLink, remove floating LanguageSelector
│   └── +page.svelte         # MODIFY: add section id anchors if missing
├── app.css                  # MODIFY: adjust text-subtle color for WCAG AA compliance
└── hooks.ts                 # EXISTING: no changes

apps/web/messages/
├── en.json                  # MODIFY: add nav labels, CTA text, accessibility labels
├── pt.json                  # MODIFY: same keys
└── es.json                  # MODIFY: same keys

apps/web/tests/unit/
└── (new test files as needed)
```

**Structure Decision**: All changes are within the existing `apps/web/` SvelteKit app structure. Two new UI components (Navbar, SkipLink) are added to `lib/ui/` following the established pattern. No new directories needed.

## Complexity Tracking

> No constitution violations to justify — all gates pass.
