# Quickstart: Complete i18n Audit & Fix

**Branch**: `003-i18n-audit-fix` | **Date**: 2026-03-30

## What this feature does

Completes the i18n coverage for the landing page by translating all remaining English strings in the PT-BR and ES locale files, replacing hardcoded strings in Svelte components with i18n references, adding SEO hreflang tags, and moving meta tags into the i18n system.

## Files to modify

### Locale files (translation updates)
- `apps/web/messages/en.json` — add 3 new keys (`meta_title`, `meta_description`, `footer_language_selector_label`)
- `apps/web/messages/pt.json` — add 3 new keys + update 15 existing values
- `apps/web/messages/es.json` — add 3 new keys + update 15 existing values

### Components (hardcoded string removal)
- `apps/web/src/lib/components/Footer.svelte` — replace hardcoded "The Loop" with `hero_product_name()`
- `apps/web/src/lib/ui/Navbar.svelte` — replace hardcoded "The Loop" with `hero_product_name()`
- `apps/web/src/lib/components/LanguageSelector.svelte` — replace hardcoded "Language selector" aria-label with `footer_language_selector_label()`

### Layout (meta tags + hreflang)
- `apps/web/src/routes/+layout.svelte` — replace hardcoded Record objects with i18n message calls, add hreflang `<link>` tags

## How to verify

```bash
cd apps/web
npm run dev
# Visit /en/, /pt/, /es/ and check every section
# View source to verify meta tags and hreflang links
npm run check    # TypeScript / svelte-check
npm run lint     # ESLint + Prettier
npm run test -- --run  # Run tests
```

## Key decisions

- **FR-004 dropped**: Pricing uses card layout, not comparison table — no row-label keys needed
- **"GitHub" stays hardcoded**: Brand name, intentionally English per FR-010
- **`pricing_included` translated but unused**: Key exists in locale files, translated for parity
