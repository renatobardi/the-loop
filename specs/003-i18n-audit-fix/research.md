# Research: Complete i18n Audit & Fix

**Branch**: `003-i18n-audit-fix` | **Date**: 2026-03-30

## R1: Current state of untranslated strings in PT/ES locale files

**Decision**: Update 13 existing keys in `pt.json` and `es.json` that have English values instead of translations.

**Rationale**: The locale files were populated with English placeholders for many pricing, integration, and footer strings. These keys exist and are imported in components, but their PT/ES values are still English.

**Untranslated keys (same in both PT and ES)**:
- `integration_github_desc`, `integration_ide_desc`, `integration_rest_desc` — integration descriptions
- `pricing_free_scans`, `pricing_payg_price`, `pricing_payg_scans`, `pricing_enterprise_price`, `pricing_enterprise_scans` — pricing values
- `pricing_support_community`, `pricing_support_dedicated`, `pricing_included` — feature values
- `pricing_contact_cta` — CTA text
- `footer_copyright`, `footer_constitution`, `footer_contact` — footer text

**Alternatives considered**: Creating new keys with different names — rejected because the keys already exist and are already imported in components. Only the values need updating.

## R2: Pricing component structure — card layout, not comparison table

**Decision**: The spec's FR-004 (adding `pricing_label_support` and `pricing_label_price` row-header keys) does NOT apply. The Pricing component uses a card-based layout, not a comparison table with row headers.

**Rationale**: Reading `Pricing.svelte` reveals three cards (Free, Pay-as-you-go, Enterprise) each with name, price, scans, and a features bullet list. There are no separate "Support", "Price", "Scans" row labels — each card displays values directly. The labels (Scans, Layers, etc.) are implicit in the card structure.

**Impact on spec**: FR-004 can be dropped. The existing keys already cover all pricing content. Only the locale file values need updating per R1.

## R3: Hardcoded strings found in Svelte components

**Decision**: Fix 3 categories of hardcoded strings (5 instances total).

| String | File | Action |
|--------|------|--------|
| `"The Loop"` | `Footer.svelte:10` | Replace with `hero_product_name()` (key exists) |
| `"The Loop"` | `Navbar.svelte:25` | Replace with `hero_product_name()` (key exists) |
| `"GitHub"` | `Footer.svelte:17` | Keep hardcoded — brand name, intentionally English per FR-010 |
| `"Language selector"` | `LanguageSelector.svelte:20,35` | Replace with new i18n key `footer_language_selector_label` |

**Rationale**: "The Loop" already has a message key (`hero_product_name`). "GitHub" is a brand and stays English. The aria-label needs i18n for accessibility in non-English contexts.

## R4: Meta tags — hardcoded Record vs i18n message keys

**Decision**: Add `meta_title` and `meta_description` keys to all three locale files and replace the hardcoded `Record<string, string>` objects in `+layout.svelte`.

**Rationale**: The current layout has titles and descriptions as inline TypeScript objects. Moving them to the i18n system keeps all translations in one place (locale JSON files) and makes them part of the standard translation workflow. The translations are already correct — they just need to move from the layout to the locale files.

**Alternatives considered**: Keeping the current Record approach — rejected because it creates a maintenance burden with translations split between two systems (locale files vs inline code).

## R5: hreflang `<link>` tags — missing from `<head>`

**Decision**: Add four `<link rel="alternate" hreflang="...">` tags to the `<svelte:head>` block in `+layout.svelte`.

**Rationale**: Currently, `hreflang` only exists as attributes on the LanguageSelector anchor links (for navigation), but the standard SEO `<link>` tags in `<head>` are absent. Search engines rely on these for proper multilingual indexing.

**Implementation**: Static tags with absolute URLs since the site has a single page:
```html
<link rel="alternate" hreflang="en" href="https://loop.oute.pro/en/" />
<link rel="alternate" hreflang="pt" href="https://loop.oute.pro/pt/" />
<link rel="alternate" hreflang="es" href="https://loop.oute.pro/es/" />
<link rel="alternate" hreflang="x-default" href="https://loop.oute.pro/en/" />
```

## R6: LanguageSelector accessibility — nested nav already resolved

**Decision**: The nested `<nav>` issue is already resolved. The LanguageSelector component has a `tag` prop, and Footer uses `<LanguageSelector tag="div" />` which renders `<div role="group">`.

**Remaining work**: Only the aria-label needs i18n (currently hardcoded as "Language selector").

## R7: Unused locale key — `pricing_included`

**Decision**: Keep and translate the key even though it's not currently used in the Pricing component.

**Rationale**: The key exists in all three locale files. It represents "Included" for the SSO/SAML feature in Enterprise tier. Although the current card layout shows SSO/SAML as a bullet without an "Included" label, the key may be needed if the layout changes. Translating it costs nothing and maintains locale file parity.
