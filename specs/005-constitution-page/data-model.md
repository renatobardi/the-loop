# Data Model: Public Constitution Page

**Branch**: `005-constitution-page` | **Date**: 2026-03-31

## Entities

### Mandate (Static Content)

No database entity — mandates are static i18n content defined as Paraglide message keys.

| Attribute   | Type   | Source                     | Example                   |
|-------------|--------|----------------------------|---------------------------|
| number      | string | Hardcoded roman numeral    | `"I"`, `"II"`, ... `"XII"` |
| title       | string | i18n message key           | `constitution_mandate_1_title()` |
| description | string | i18n message key           | `constitution_mandate_1_description()` |

**Total**: 12 mandates x 3 locales = 36 title translations + 36 description translations = 72 new i18n message keys + 6 page-level keys (headline, subheadline, transparency text, transparency link label, meta title, meta description) x 3 locales = 90 total new message values.

### i18n Message Key Schema

New keys follow existing `snake_case` convention with `constitution_` prefix:

```
constitution_headline           — "12 Immutable Mandates"
constitution_subheadline        — "The engineering principles that govern..."
constitution_mandate_1_title    — "Trunk-Based Development"
constitution_mandate_1_desc     — "One branch. Always production-ready..."
...
constitution_mandate_12_title   — "Documentation is Code"
constitution_mandate_12_desc    — "Docs are treated with the same rigor..."
constitution_transparency_text  — "This constitution lives in our public repository..."
constitution_transparency_link  — "Read the full document on GitHub."
constitution_meta_title         — "The Loop — 12 Immutable Engineering Mandates"
constitution_meta_description   — "The engineering principles that govern The Loop..."
```

### Waitlist Entry (Existing)

No changes to the existing `waitlist` Firestore collection. The Constitution page reuses the same write path with `source: "constitution"` for tracking.
