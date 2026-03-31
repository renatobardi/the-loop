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
npm run test         # vitest (unit tests in tests/unit/)
npm run test -- --run  # Single run (used in CI)
```

Paraglide codegen (runs automatically via Vite plugin, but can be triggered manually):
```bash
npx paraglide-js compile --project ./project.inlang --outdir ./src/lib/paraglide
```

## Architecture

Monorepo with `apps/web/` as the main SvelteKit app.

- **`src/routes/`** — File-based routing with trailing slashes enforced. All routes served under locale prefix (`/en/`, `/pt/`, `/es/`).
- **`src/lib/ui/`** — Design system components (Button, Input, Card, Badge, Container, Section). Exported via `index.ts`. Uses design tokens from `app.css`.
- **`src/lib/components/`** — Page section components (Hero, Problem, Layers, HowItWorks, Pricing, Footer, etc.).
- **`src/lib/server/`** — Server-only code: Firebase init, Firestore operations, Zod schemas, rate limiter.
- **`src/lib/paraglide/`** — Auto-generated i18n runtime. **Do not edit or commit.**
- **`messages/`** — i18n source JSON files (`en.json`, `pt.json`, `es.json`). Keys use `snake_case`.
- **`tests/unit/`** — Vitest tests with jsdom environment.

### Key files

- `src/hooks.ts` — Paraglide i18n reroute handler
- `src/hooks.server.ts` — Security headers (HSTS, CSP, X-Frame-Options, Permissions-Policy)
- `src/routes/+page.server.ts` — Server actions (waitlist form: Zod validation → rate limit → Firestore write)
- `src/app.css` — Tailwind 4 `@theme` block with all design tokens (colors, fonts, spacing, shadows)
- `project.inlang/settings.json` — Paraglide config (source: en, targets: pt, es)

## i18n (Paraglide-SvelteKit)

- Import messages: `import { hero_headline } from '$lib/paraglide/messages.js'`
- Get current language: `import { languageTag } from '$lib/paraglide/runtime.js'`
- Root layout wraps app with `<ParaglideJS {i18n}>` for link translation
- Use `href="/"` (plain paths) — Paraglide handles locale prefixing automatically
- Never hardcode locale-prefixed URLs in components

## Form Handling Pattern

Server Actions via `+page.server.ts` → Zod validation → rate limiting (per IP) → Firestore write. Frontend uses `use:enhance` for progressive enhancement.

## Environment

- **Runtime:** `FIREBASE_SERVICE_ACCOUNT` (JSON string via GCP Secret Manager), `PORT=3000`
- **No `.env` in repo** — all secrets via GCP Secret Manager / GitHub Actions secrets
- **Firestore project:** `theloopoute`

## Deployment

GitHub Actions CI gates (lint → type-check → test → build → Trivy scan → docs-check) must all pass before merge. Deploy to Cloud Run via Workload Identity Federation on push to `main`.

## Governance (CONSTITUTION.md)

- Trunk-based development: `main` only via PRs, branch prefixes `feat/`, `fix/`, `hotfix/`, `chore/`
- Design system tokens are centralized in `lib/ui/` — no ad-hoc styling
- `main` = production (no dev environment)
- All merges controlled by @renatobardi
- Hexagonal architecture applies after Phase 1 (not current Phase 0)

## Active Technologies
- TypeScript 5.x, Svelte 5 (runes), SvelteKit 2.50 + Tailwind CSS 4, Paraglide-SvelteKit 0.16.1, Svelte 5 snippets/actions (002-landing-page-polish)

## Recent Changes
- 002-landing-page-polish: Design polish — nav, accessibility, spacing, pricing CTAs, contrast fixes
