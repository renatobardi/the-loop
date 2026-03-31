# Quickstart: Public Constitution Page

**Branch**: `005-constitution-page` | **Date**: 2026-03-31

## Prerequisites

- Node 22+
- Repository cloned, on branch `005-constitution-page`

## Setup

```bash
cd apps/web
npm install
npm run dev
```

## Verify

1. Open `http://localhost:5173/en/constitution/` — should render 12 mandates in English
2. Open `http://localhost:5173/pt/constituicao/` — should render in Portuguese
3. Open `http://localhost:5173/es/constitucion/` — should render in Spanish
4. Click footer "Constitution" link — should navigate to locale-correct Constitution page
5. Submit a waitlist email on the Constitution page — check Firestore for `source: "constitution"`

## Files Changed

| File | Change |
|------|--------|
| `src/lib/i18n.ts` | Add `pathnames` config for `/constitution` |
| `src/routes/constitution/+page.svelte` | New — Constitution page component |
| `src/routes/constitution/+page.server.ts` | New — Waitlist form action (reuses server modules) |
| `src/lib/components/ConstitutionHero.svelte` | New — Hero section for Constitution page |
| `src/lib/components/MandateCard.svelte` | New — Single mandate card component |
| `src/lib/components/MandatesGrid.svelte` | New — Responsive 12-card grid |
| `src/lib/components/TransparencySection.svelte` | New — GitHub link section |
| `messages/en.json` | Add `constitution_*` keys |
| `messages/pt.json` | Add `constitution_*` keys |
| `messages/es.json` | Add `constitution_*` keys |

## Run Quality Checks

```bash
npm run lint
npm run check
npm run test -- --run
npm run build
```
