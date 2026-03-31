# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

The Loop — Phase 0 landing page with waitlist. SvelteKit 2 + Svelte 5 (runes), Tailwind CSS 4, Paraglide-SvelteKit i18n (EN/PT/ES), Firebase Firestore, deployed to GCP Cloud Run.

## Commands

All commands run from `apps/web/`:

```bash
npm run dev          # Dev server at localhost:5173 (routes require locale prefix: /en/, /pt/, /es/)
npm run build        # Production build (adapter-node → build/)
npm run check        # svelte-kit sync + svelte-check (TypeScript strict)
npm run lint         # ESLint + Prettier check
npm run format       # Prettier write
npm run test         # vitest watch mode (unit tests in tests/unit/)
npm run test -- --run                         # Single run (CI mode)
npm run test -- --run tests/unit/server.test.ts  # Run a single test file
```

Paraglide codegen runs automatically via Vite plugin. Manual trigger:
```bash
npx paraglide-js compile --project ./project.inlang --outdir ./src/lib/paraglide
```

## Architecture

Monorepo with `apps/web/` as the main SvelteKit app.

- **`specs/`** — Feature specs at repo root. Each numbered directory (e.g., `001-landing-page-waitlist/`) contains `spec.md`, `plan.md`, `tasks.md`, and related artifacts. The numeric prefix maps to branch names (e.g., branch `003-i18n-audit-fix` → `specs/003-i18n-audit-fix/`).
- **`.project/`** — Persistent project history: phase specs, decisions (ADRs), research. Files here are never deleted — obsolete docs go to `.project/archive/`.
- **`src/routes/`** — File-based routing. Trailing slashes enforced (`trailingSlash: 'always'` in `+layout.ts`). All routes served under locale prefix (`/en/`, `/pt/`, `/es/`).
- **`src/lib/ui/`** — Design system components (Button, Input, Card, Badge, Container, Section, Navbar, SkipLink). Barrel-exported via `index.ts`. Consumes design tokens from `app.css`.
- **`src/lib/components/`** — Page section components (Hero, Problem, Layers, HowItWorks, Pricing, Footer, WaitlistForm, etc.).
- **`src/lib/server/`** — Server-only modules: `firebase.ts` (singleton init), `waitlist.ts` (Firestore write, returns `'created' | 'duplicate'`), `schemas.ts` (Zod with email normalization), `rateLimiter.ts` (5 req/60s per IP).
- **`src/lib/paraglide/`** — Auto-generated i18n runtime. **Do not edit or commit.**
- **`messages/`** — i18n source JSON files (`en.json`, `pt.json`, `es.json`). Keys use `snake_case`.
- **`tests/unit/`** — Vitest with jsdom environment and `$lib`/`$app` path aliases.

### Key files

- `src/hooks.ts` — Paraglide i18n reroute handler
- `src/hooks.server.ts` — Security headers (HSTS, CSP, X-Frame-Options, Permissions-Policy)
- `src/routes/+page.server.ts` — Server actions (waitlist form: rate limit → Zod validation → Firestore write)
- `src/app.css` — Tailwind 4 `@theme` block with all design tokens (colors, fonts, spacing, shadows)
- `project.inlang/settings.json` — Paraglide config (source: en, targets: pt, es)
- `src/lib/i18n.ts` — Paraglide setup: `prefixDefaultLanguage: 'always'`, three locales, all LTR

## Svelte 5 Conventions

This project uses Svelte 5 runes exclusively (enforced in `svelte.config.js`):

- **Props**: `let { variant = 'primary', children, ...rest } = $props()` — no `export let`
- **State**: `let value = $state('')` — no `$:` reactive declarations
- **Derived**: `let computedVal = $derived(expression)` — replaces `$: computedVal = ...`
- **Children**: Use `{@render children?.()}` snippet pattern, not `<slot />`

## Design Tokens (Tailwind 4)

`app.css` defines a `@theme` block with custom CSS variables consumed as Tailwind utility classes:

- Colors: `bg-bg`, `bg-bg-surface`, `bg-bg-elevated`, `text-text`, `text-text-muted`, `text-accent`, `bg-accent`
- Glow effect: `shadow-glow` token for accent-colored shadows
- Font: Geist via CDN, with size scale defined as CSS variables (`--font-size-xs` through `--font-size-7xl`)

All visual styling must use these tokens — no ad-hoc color/spacing values.

## i18n (Paraglide-SvelteKit)

- Import messages: `import { hero_headline } from '$lib/paraglide/messages.js'`
- Get current language: `import { languageTag } from '$lib/paraglide/runtime.js'`
- Root layout wraps app with `<ParaglideJS {i18n}>` for link translation
- Use `href="/"` (plain paths) — Paraglide handles locale prefixing automatically
- Never hardcode locale-prefixed URLs in components

## Form Handling Pattern

Server Actions flow: `+page.server.ts` → rate limit check → Zod validation (with email normalization) → Firestore write. Server functions return semantic status codes (`'created'`, `'duplicate'`) rather than throwing. Frontend uses `use:enhance` for progressive enhancement with a state machine (`idle → submitting → success | error | duplicate | rate_limited`).

## Environment

- **Runtime:** `FIREBASE_SERVICE_ACCOUNT` (JSON string via GCP Secret Manager), `PORT=3000`
- **No `.env` in repo** — all secrets via GCP Secret Manager / GitHub Actions secrets
- **Firestore project:** `theloopoute`

## Deployment

GitHub Actions CI gates (lint → type-check → test → build → Trivy scan → docs-check) must all pass before merge. Deploy to Cloud Run via Workload Identity Federation on push to `main`.

## Governance (CONSTITUTION.md)

- Trunk-based development: `main` only via PRs, branch prefixes `feat/`, `fix/`, `hotfix/`, `chore/`. Feature branches for specs use a numeric prefix matching their spec directory (e.g., branch `003-i18n-audit-fix` → `specs/003-i18n-audit-fix/`)
- Design system tokens are centralized in `lib/ui/` — no ad-hoc styling
- `main` = production (no dev environment — single environment)
- All merges controlled by @renatobardi — sole approver
- Hexagonal architecture applies after Phase 1 (not current Phase 0)
- Structural changes (new routes, components, architecture) require doc updates in the same PR — CI runs `scripts/generate-docs.sh` and blocks merge if docs are stale
- Node 22 in CI

## Active Technologies
- TypeScript 5.x, Svelte 5 (runes), SvelteKit 2.50 + @inlang/paraglide-sveltekit 0.16.1, Tailwind CSS 4 (005-constitution-page)
- N/A (static content page; waitlist reuses existing Firestore) (005-constitution-page)

## Recent Changes
- 005-constitution-page: Added TypeScript 5.x, Svelte 5 (runes), SvelteKit 2.50 + @inlang/paraglide-sveltekit 0.16.1, Tailwind CSS 4
