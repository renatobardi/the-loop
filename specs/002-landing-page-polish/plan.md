# Implementation Plan: i18n Audit & Complete Translation Fix

**Branch**: `fix/i18n-missing-translations` | **Date**: 2026-03-30 | **Spec**: [spec.md](spec.md)
**Input**: User-provided i18n audit spec covering all untranslated strings in PT-BR and ES locales.

## Summary

Complete i18n audit and fix for the landing page. The page uses Paraglide-SvelteKit with flat `snake_case` keys across three locale files (`en.json`, `pt.json`, `es.json`). While headlines and most UI chrome are translated, the **pricing card values**, **footer links/copyright**, **integration descriptions**, and the **LanguageSelector aria-label** remain in English across all locales. Additionally, explicit `<link rel="alternate" hreflang>` tags are missing from `<head>`.

## Technical Context

**Language/Version**: TypeScript 5.x, Svelte 5 (runes), SvelteKit 2.50
**Primary Dependencies**: @inlang/paraglide-sveltekit 0.16.1, Tailwind CSS 4
**Storage**: N/A (i18n is compile-time via Paraglide)
**Testing**: vitest (unit), manual verification across `/en/`, `/pt/`, `/es/`
**Target Platform**: Web (Cloud Run)
**Project Type**: SvelteKit web app (landing page)
**Performance Goals**: N/A (no runtime perf impact — translations are compiled)
**Constraints**: All 3 locale files must stay perfectly synchronized (same keys)
**Scale/Scope**: ~15 keys to translate in pt.json, ~15 keys in es.json, 1 new key across 3 files, 2 component updates

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Mandamento | Status | Notes |
|------------|--------|-------|
| I. Trunk-Based | PASS | New branch `fix/i18n-missing-translations` from `main`, PR to merge |
| II. Design System | PASS | No visual/styling changes — only text content in locale files |
| III. Branch Taxonomy | PASS | `fix/` prefix for bug fix (missing translations) |
| VII. CI Rigoroso | PASS | lint + type-check + test + build gates apply |
| IX. Clean Code | PASS | No dead code added; locale files maintain consistent structure |
| XII. Docs & Code | PASS | No structural changes requiring doc updates |

No violations. No Complexity Tracking entries needed.

## Project Structure

### Documentation (this feature)

```text
specs/002-landing-page-polish/
├── plan.md              # This file
├── research.md          # Phase 0 output (gap analysis)
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

No `data-model.md`, `contracts/`, or `quickstart.md` needed — this is a pure translation fix with no new entities, APIs, or onboarding changes.

### Source Code (files to modify)

```text
apps/web/
├── messages/
│   ├── en.json                    # Add 1 new key (footer_language_selector_label)
│   ├── pt.json                    # Translate ~15 keys + add 1 new key
│   └── es.json                    # Translate ~15 keys + add 1 new key
├── src/
│   ├── routes/+layout.svelte      # Add hreflang <link> tags
│   └── lib/
│       └── components/
│           └── LanguageSelector.svelte  # i18n the aria-label
```

## Gap Analysis (Current State → Desired State)

### Already Correct (no changes needed)

| Area | Status |
|------|--------|
| **Nested `<nav>` in footer** | FIXED — LanguageSelector uses `tag="div"` with `role="group"` |
| **Pricing headline** | Translated in all 3 locales |
| **Integration headline** | Translated in all 3 locales |
| **Meta tags (title, description, og:*)** | Hardcoded per-language in `+layout.svelte` — correct |
| **Hero, Problem, Layers, HowItWorks, Waitlist** | Fully translated |
| **Nav labels, form messages, skip link** | Fully translated |
| **Hardcoded "Join the waitlist"** | Uses `form_submit()` / `pricing_join_waitlist()` ✓ |
| **Hardcoded "your@email.com"** | Uses `hero_email_placeholder()` ✓ |
| **Hardcoded "Skip to main content"** | Uses `skip_to_content()` ✓ |
| **"The Loop" in Navbar/Footer** | Brand name — identical in all 3 locales by design |
| **"GitHub" in Footer** | Brand name — identical in all 3 locales by design |

### Gaps to Fix

#### A. Pricing card values (pt.json + es.json) — 9 keys each

| Key | Current PT/ES | Target PT | Target ES |
|-----|--------------|-----------|-----------|
| `pricing_free_scans` | `100 scans/month` | `100 scans/mês` | `100 scans/mes` |
| `pricing_payg_price` | `Pay per scan batch` | `Pague por lote de scans` | `Paga por lote de scans` |
| `pricing_payg_scans` | `Buy in batches` | `Compre em lotes` | `Compra por lotes` |
| `pricing_enterprise_price` | `Contact us` | `Fale conosco` | `Contáctanos` |
| `pricing_enterprise_scans` | `Unlimited` | `Ilimitado` | `Ilimitado` |
| `pricing_support_community` | `Community` | `Comunidade` | `Comunidad` |
| `pricing_support_dedicated` | `Dedicated` | `Dedicado` | `Dedicado` |
| `pricing_included` | `Included` | `Incluído` | `Incluido` |
| `pricing_contact_cta` | `Contact us` | `Fale conosco` | `Contáctanos` |

**Note on key naming**: The spec uses hierarchical dot-notation keys (e.g., `pricing.value.scans_free`), but the codebase uses flat `snake_case` keys (e.g., `pricing_free_scans`). The translations map to existing flat keys.

**Note on "scans/month"**: The spec suggests `100/mês` (without "scans"), but the current card layout has no separate row labels — the string must be self-contained. Using `100 scans/mês` preserves context.

#### B. Footer text (pt.json + es.json) — 3 keys each

| Key | Current PT/ES | Target PT | Target ES |
|-----|--------------|-----------|-----------|
| `footer_copyright` | `© 2026 Oute. All rights reserved.` | `© 2026 Oute. Todos os direitos reservados.` | `© 2026 Oute. Todos los derechos reservados.` |
| `footer_constitution` | `Constitution` | `Constituição` | `Constitución` |
| `footer_contact` | `Contact` | `Contato` | `Contacto` |

#### C. Integration descriptions (pt.json + es.json) — 3 keys each

| Key | Current PT/ES | Target PT | Target ES |
|-----|--------------|-----------|-----------|
| `integration_github_desc` | (English) | `GitHub App com Check Runs, relatórios SARIF e comentários de review em PRs.` | `GitHub App con Check Runs, reportes SARIF y comentarios de review en PRs.` |
| `integration_ide_desc` | (English) | `Cursor, VS Code, Windsurf — escaneie código e receba advisories direto no seu editor.` | `Cursor, VS Code, Windsurf — escanea código y recibe advisories directo en tu editor.` |
| `integration_rest_desc` | (English) | `REST API com suporte a webhooks. Output em SARIF e JSON.` | `REST API con soporte de webhooks. Output en SARIF y JSON.` |

#### D. New key: Language selector aria-label — all 3 files

| Key | EN | PT | ES |
|-----|-----|-----|-----|
| `footer_language_selector_label` | `Language` | `Idioma` | `Idioma` |

#### E. hreflang `<link>` tags — `+layout.svelte`

Currently missing. Add to `<svelte:head>`:
```html
<link rel="alternate" hreflang="en" href="https://loop.oute.pro/en/" />
<link rel="alternate" hreflang="pt" href="https://loop.oute.pro/pt/" />
<link rel="alternate" hreflang="es" href="https://loop.oute.pro/es/" />
<link rel="alternate" hreflang="x-default" href="https://loop.oute.pro/en/" />
```

#### F. LanguageSelector aria-label i18n — `LanguageSelector.svelte`

Currently hardcoded `aria-label="Language selector"` in both the `<nav>` and `<div>` branches. Replace with imported `footer_language_selector_label()`.

## Implementation Sequence

1. **Locale files** (pt.json, es.json, en.json) — translate all gap keys, add new key
2. **LanguageSelector.svelte** — import and use `footer_language_selector_label()`
3. **+layout.svelte** — add hreflang `<link>` tags
4. **Verify** — `npm run check` + `npm run lint` + `npm run build` from `apps/web/`

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Paraglide codegen fails with new key | Vite plugin auto-compiles; verify with `npm run check` |
| Key typo breaks build | TypeScript strict mode catches missing imports at build time |
| Locale file desync (missing key in one file) | Paraglide compiler warns on missing keys; all 3 files edited together |
