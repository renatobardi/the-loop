# Implementation Plan: Landing Page & Waitlist

**Branch**: `001-landing-page-waitlist` | **Date**: 2026-03-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-landing-page-waitlist/spec.md`

## Summary

Build a production-ready landing page for The Loop — a dark-mode, trilingual (EN/PT-BR/ES) single-page marketing site with waitlist collection via Firebase Firestore. Deploy to GCP Cloud Run with full CI/CD pipeline enforcing all 12 constitutional mandates. SvelteKit + Tailwind CSS + Paraglide i18n.

## Technical Context

**Language/Version**: TypeScript 5.x, Node.js 22 LTS
**Primary Dependencies**: SvelteKit (adapter-node), Tailwind CSS 4, Paraglide-SvelteKit (i18n), firebase-admin (Firestore), Zod (validation), rate-limiter-flexible (rate limiting)
**Storage**: Firebase Firestore (project: `theloopoute`)
**Testing**: vitest (unit), playwright (e2e when applicable)
**Target Platform**: GCP Cloud Run (Docker, node:22-alpine)
**Project Type**: Web application (SSR landing page)
**Performance Goals**: LCP < 2.5s (stretch: < 1.5s), 60fps scroll animations
**Constraints**: Single environment (production), HTTPS only, all 12 constitutional mandates enforced
**Scale/Scope**: Single landing page, 3 locales, ~50 translation keys, waitlist form with Firestore backend

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Mandamento | Status | Notes |
|---|-----------|--------|-------|
| I | Trunk-Based Development | PASS | `feat/001-landing-page-waitlist` branch, PRs to `main` |
| II | Design System Imutavel | PASS | Tokens in `apps/web/src/lib/ui/`, all components use tokens |
| III | Taxonomia de Branches | PASS | `feat/` prefix, kebab-case, English |
| IV | Main Protegida | PASS | Branch protection, CODEOWNERS, signed commits |
| V | Aprovacao Obrigatoria | PASS | @renatobardi approves all PRs |
| VI | Sem Ambiente de Dev | PASS | Single env: production. `main` = prod |
| VII | CI Rigoroso | PASS | ESLint+Prettier, TS strict, vitest, Docker build, trivy, docs-check |
| VIII | Seguranca Mandatoria | PASS | CSP, HSTS, rate limiting, Firestore rules, WIF, non-root Docker |
| IX | Clean Code | PASS | SRP, descriptive names, no dead code, Zod validation |
| X | Arquitetura Hexagonal | N/A | Phase 0 — constitution explicitly exempts: "Clean Code e suficiente" |
| XI | Pasta .project/ | PASS | `.project/phases/00-landing/` with spec, plan, tasks |
| XII | Documentacao e Codigo | PASS | README.md, CONSTITUTION.md, docs-check CI gate |

**Gate result**: PASS — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/001-landing-page-waitlist/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── waitlist-api.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
apps/
└── web/                          # SvelteKit landing page
    ├── src/
    │   ├── hooks.server.ts        # Security headers, locale redirect
    │   ├── routes/
    │   │   ├── +layout.svelte    # Root layout (hreflang, meta)
    │   │   ├── +layout.server.ts # Root layout data
    │   │   ├── +page.server.ts   # Root redirect / → /en/
    │   │   └── [lang]/           # Locale-parameterized routes
    │   │       ├── +layout.svelte
    │   │       ├── +layout.server.ts
    │   │       ├── +page.svelte  # Landing page (all 8 sections)
    │   │       └── +page.server.ts # Waitlist form action
    │   ├── lib/
    │   │   ├── ui/               # Design system (tokens + components)
    │   │   │   ├── tokens/       # CSS variables / Tailwind config
    │   │   │   ├── Button.svelte
    │   │   │   ├── Input.svelte
    │   │   │   ├── Card.svelte
    │   │   │   ├── Badge.svelte
    │   │   │   ├── Container.svelte
    │   │   │   ├── Section.svelte
    │   │   │   └── index.ts      # Barrel export
    │   │   ├── server/           # Server-only modules
    │   │   │   ├── firebase.ts   # Admin SDK init (singleton)
    │   │   │   ├── waitlist.ts   # Firestore waitlist operations
    │   │   │   ├── rateLimiter.ts
    │   │   │   └── schemas.ts    # Zod validation schemas
    │   │   ├── components/       # Page-specific components
    │   │   │   ├── Hero.svelte
    │   │   │   ├── Problem.svelte
    │   │   │   ├── Layers.svelte
    │   │   │   ├── HowItWorks.svelte
    │   │   │   ├── Integrations.svelte
    │   │   │   ├── Pricing.svelte
    │   │   │   ├── WaitlistCta.svelte
    │   │   │   ├── Footer.svelte
    │   │   │   ├── WaitlistForm.svelte
    │   │   │   └── LanguageSelector.svelte
    │   │   └── i18n/             # Paraglide messages
    │   │       └── messages/
    │   │           ├── en.json
    │   │           ├── pt.json
    │   │           └── es.json
    │   ├── app.html
    │   ├── app.css               # Tailwind directives + global styles
    │   └── params/
    │       └── lang.ts           # Locale param matcher
    ├── static/
    │   └── fonts/                # Geist font files
    ├── tests/
    │   ├── unit/                 # vitest
    │   └── e2e/                  # playwright (when applicable)
    ├── svelte.config.js
    ├── vite.config.ts
    ├── tailwind.config.ts
    ├── tsconfig.json
    ├── package.json
    └── Dockerfile

# Root-level files
├── .github/
│   ├── workflows/
│   │   ├── ci.yml               # Lint, type-check, test, build, vuln scan, docs-check
│   │   └── deploy.yml           # Cloud Run deploy on merge to main
│   └── CODEOWNERS               # * @renatobardi
├── .project/
│   └── phases/
│       └── 00-landing/
│           ├── spec.md          # Copy of feature spec
│           ├── plan.md          # Copy of this plan
│           └── decisions/       # ADRs
├── scripts/
│   └── generate-docs.sh         # docs-check script
├── firestore.rules              # Firestore security rules
├── CONSTITUTION.md              # Root-level constitution
└── README.md
```

**Structure Decision**: Single SvelteKit app in `apps/web/` — prepares for future monorepo growth (e.g., `apps/api/`, `packages/ui/`) without over-engineering Phase 0. Design system lives in `apps/web/src/lib/ui/` and migrates to `packages/ui/` when needed (per Constitution Mandamento II).

## Complexity Tracking

> No violations to justify — all 12 mandamentos pass.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | — | — |
