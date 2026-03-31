# Implementation Plan: Complete i18n Audit & Fix

**Branch**: `003-i18n-audit-fix` | **Date**: 2026-03-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-i18n-audit-fix/spec.md`

## Summary

Complete the i18n coverage for The Loop landing page by: (1) translating 15 existing English-value keys in PT/ES locale files, (2) adding 3 new i18n keys for meta tags and language selector label, (3) replacing 5 hardcoded strings in 3 Svelte components with i18n references, (4) adding SEO hreflang `<link>` tags to `<head>`, and (5) migrating meta title/description from inline Record objects to the i18n message system.

## Technical Context

**Language/Version**: TypeScript 5.x, Svelte 5 (runes), SvelteKit 2.50  
**Primary Dependencies**: @inlang/paraglide-sveltekit 0.16.1, Tailwind CSS 4  
**Storage**: N/A (locale JSON files only)  
**Testing**: Vitest (unit), manual visual verification per locale  
**Target Platform**: Web (Cloud Run, Node adapter)  
**Project Type**: Web application (SvelteKit)  
**Performance Goals**: N/A (no runtime impact — compile-time i18n)  
**Constraints**: All CI gates must pass (lint, type-check, test, build, Trivy, docs-check)  
**Scale/Scope**: 3 locale files, 4 Svelte files modified, ~18 translation values changed

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Mandamento | Status | Notes |
|------------|--------|-------|
| I. Trunk-Based Development | PASS | Working on feature branch `003-i18n-audit-fix`, will merge via PR |
| II. Design System Imutável | PASS | No visual/token changes — only text content |
| III. Taxonomia de Branches | PASS | Branch follows sequential numbering convention |
| IV. Main Protegida | PASS | Will merge via PR with required approvals |
| V. Merge Controlado | PASS | @renatobardi will merge |
| VI. Sem Ambiente de Dev | PASS | Single production environment, no new envs |
| VII. CI Rigoroso | PASS | All gates will run: lint, type-check, test, build |
| VIII. Segurança Mandatória | PASS | No secrets, no new endpoints, no security surface changes |
| IX. Clean Code | PASS | Removing hardcoded strings improves code quality |
| X. Arquitetura Hexagonal | N/A | Phase 0 — hexagonal not applicable |
| XI. Pasta .project/ | PASS | Specs in `specs/` directory per convention |
| XII. Documentação e Código | PASS | README unaffected; docs-check gate will verify |

**Post-design re-check**: All gates still PASS. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/003-i18n-audit-fix/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (translation key inventory)
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (files to modify)

```text
apps/web/
├── messages/
│   ├── en.json              # +3 new keys
│   ├── pt.json              # +3 new keys, ~15 value updates
│   └── es.json              # +3 new keys, ~15 value updates
└── src/
    ├── routes/
    │   └── +layout.svelte   # Meta tags → i18n, add hreflang <link> tags
    └── lib/
        ├── components/
        │   ├── Footer.svelte              # "The Loop" → hero_product_name()
        │   └── LanguageSelector.svelte    # aria-label → i18n key
        └── ui/
            └── Navbar.svelte              # "The Loop" → hero_product_name()
```

**Structure Decision**: No new files or directories. All changes are edits to existing locale JSON files and Svelte components.

## Complexity Tracking

> No violations to justify. All changes follow existing patterns.
