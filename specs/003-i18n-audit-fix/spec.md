# Feature Specification: Complete i18n Audit & Fix (PT-BR and ES)

**Feature Branch**: `003-i18n-audit-fix`  
**Created**: 2026-03-30  
**Status**: Draft  
**Input**: User description: "Auditoria e Correção Completa de i18n (PT-BR e ES)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Portuguese-speaking visitor sees full page in Portuguese (Priority: P1)

A visitor navigates to `/pt/` and sees the entire landing page — every section, label, and footer element — displayed in Portuguese. No English text leaks through in any visible UI element.

**Why this priority**: PT-BR is a primary target market. Untranslated strings break trust and make the product feel incomplete. This covers the majority of missing translations (pricing table, footer, integrations).

**Independent Test**: Navigate to `/pt/` and visually confirm every section (pricing table cells, footer links, integration descriptions, meta tags) is in Portuguese.

**Acceptance Scenarios**:

1. **Given** a visitor on `/pt/`, **When** they scroll through the entire page, **Then** all visible text is in Portuguese — no English strings appear in pricing table values, footer links, footer copyright, or integration descriptions.
2. **Given** a visitor on `/pt/`, **When** they view the page source or inspect `<head>`, **Then** the `<title>` and `<meta name="description">` are in Portuguese.
3. **Given** a visitor on `/pt/`, **When** they view the pricing table, **Then** labels like "Support" show as "Suporte", "Price" shows as "Preco", values like "100/month" show as "100/mes", "Community" as "Comunidade", "Contact us" as "Fale conosco", etc.

---

### User Story 2 - Spanish-speaking visitor sees full page in Spanish (Priority: P1)

A visitor navigates to `/es/` and sees the entire landing page displayed in Spanish, with the same completeness as the Portuguese version.

**Why this priority**: ES is a primary target market with identical translation gaps to PT-BR. Both must be fixed together.

**Independent Test**: Navigate to `/es/` and visually confirm every section is in Spanish.

**Acceptance Scenarios**:

1. **Given** a visitor on `/es/`, **When** they scroll through the entire page, **Then** all visible text is in Spanish — no English strings appear in pricing table, footer, or integration descriptions.
2. **Given** a visitor on `/es/`, **When** they view page source, **Then** meta title and description are in Spanish.

---

### User Story 3 - SEO hreflang tags for search engines (Priority: P2)

Search engines crawling any locale route discover `<link rel="alternate" hreflang="...">` tags in `<head>` pointing to all three language versions plus `x-default`, enabling proper multilingual indexing.

**Why this priority**: Without hreflang tags, search engines may index duplicate content or serve the wrong language version in search results. This is a standard SEO requirement for multilingual sites.

**Independent Test**: View page source on any locale route and confirm four `<link rel="alternate">` tags are present in `<head>`.

**Acceptance Scenarios**:

1. **Given** any page route (`/en/`, `/pt/`, `/es/`), **When** a search engine crawls the page, **Then** the `<head>` contains `<link rel="alternate" hreflang="en">`, `hreflang="pt"`, `hreflang="es"`, and `hreflang="x-default"` tags with correct absolute URLs.

---

### User Story 4 - English visitor sees no regressions (Priority: P2)

A visitor on `/en/` sees the page exactly as it was before — all English text intact, no broken references, no missing strings.

**Why this priority**: Regression check. Adding new i18n keys and refactoring existing ones must not break the primary English version.

**Independent Test**: Navigate to `/en/` and confirm all sections render correctly in English.

**Acceptance Scenarios**:

1. **Given** a visitor on `/en/`, **When** they view the full page, **Then** all content displays correctly in English with no missing or broken text.

---

### User Story 5 - Language selector accessibility in footer (Priority: P3)

The language selector in the footer is accessible and does not create a nested `<nav>` landmark. Screen readers announce it as a grouped control with a localized label.

**Why this priority**: Accessibility compliance. A nested `<nav>` inside the footer `<nav>` would confuse screen reader navigation. The localized aria-label ensures non-English screen reader users understand the control's purpose.

**Independent Test**: Inspect the footer HTML and confirm the language selector uses `<div role="group">` (not `<nav>`) with an i18n aria-label. Verify the label reads "Idioma" on `/pt/` and `/es/`.

**Acceptance Scenarios**:

1. **Given** a screen reader user navigating the footer, **When** they reach the language selector, **Then** it is announced with a localized label ("Language" in EN, "Idioma" in PT/ES) and does not create a nested navigation landmark.

---

### Edge Cases

- What happens if a new locale key is missing from one language file? The i18n system should fall back to the source language (EN) rather than showing a blank string.
- What happens if meta tags use i18n message functions in SSR? They must resolve correctly server-side since meta tags are rendered before hydration.
- How are tier names (Free, Pay-as-you-go, Enterprise) handled? They stay in English across all locales intentionally — these are universal SaaS terms.
- How are technical terms (Scans, Layers, SSO/SAML, Audit logs) handled? They stay in English across all locales intentionally — these are industry-standard terms.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All integration description strings (`integration_github_desc`, `integration_ide_desc`, `integration_rest_desc`) MUST be translated in PT-BR and ES locale files
- **FR-002**: All pricing table value strings MUST be translated in PT-BR and ES: `pricing_free_scans`, `pricing_payg_price`, `pricing_payg_scans`, `pricing_enterprise_price`, `pricing_enterprise_scans`, `pricing_support_community`, `pricing_support_dedicated`, `pricing_included`, `pricing_contact_cta`
- **FR-003**: Footer strings MUST be translated in PT-BR and ES: `footer_copyright`, `footer_constitution`, `footer_contact`
- **FR-004**: ~~DROPPED~~ — Pricing component uses card layout, not comparison table with row headers. No `pricing_label_support` or `pricing_label_price` keys needed. See research.md R2.
- **FR-005**: A `footer_language_selector_label` key MUST be added (EN: "Language", PT: "Idioma", ES: "Idioma") and the LanguageSelector component MUST use it for its aria-label
- **FR-006**: The `<head>` MUST contain `<link rel="alternate" hreflang="...">` tags for `en`, `pt`, `es`, and `x-default` on every page
- **FR-007**: Meta title and description MUST use i18n message functions rather than hardcoded Record objects in the layout, so they participate in the standard i18n workflow
- **FR-008**: Any remaining hardcoded English strings in Svelte components (visible text not sourced from locale files) MUST be replaced with i18n message references
- **FR-009**: The footer language selector MUST NOT create a nested `<nav>` landmark — it MUST use `<div role="group">` with the i18n aria-label from FR-005. *Note: nested nav issue is already resolved (Footer uses `<LanguageSelector tag="div" />`). Only the aria-label i18n remains (covered by FR-005).*
- **FR-010**: Tier names (Free, Pay-as-you-go, Enterprise), technical labels (Scans, Layers, SSO/SAML, Audit logs), and brand names (The Loop, GitHub) MUST remain in English across all locales

### Key Entities

- **Locale files** (`en.json`, `pt.json`, `es.json`): Source of truth for all user-visible strings. Keys use `snake_case`. Must have parity across all three files.
- **Translation key**: A `snake_case` identifier mapping to a localized string value. New keys follow existing naming convention (e.g., `pricing_label_support`, `footer_language_selector_label`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of user-visible strings on `/pt/` are in Portuguese — zero English text leaks (excluding intentionally English terms per FR-010)
- **SC-002**: 100% of user-visible strings on `/es/` are in Spanish — zero English text leaks (excluding intentionally English terms per FR-010)
- **SC-003**: All three locale files have identical key sets — no key present in one file is missing from another
- **SC-004**: Page `<head>` on every locale route contains exactly 4 hreflang `<link>` tags (en, pt, es, x-default)
- **SC-005**: Zero hardcoded English strings found via codebase grep in Svelte components that should come from locale files
- **SC-006**: The English (`/en/`) version shows no regressions — all sections render correctly

## Assumptions

- The existing Paraglide i18n setup and compile-time codegen remain unchanged — only locale JSON files and component references are modified
- Meta tags are rendered server-side via SvelteKit's `<svelte:head>` and will correctly resolve i18n functions during SSR
- The LanguageSelector component already supports a `tag` prop for rendering as `<div>` vs `<nav>` — this existing mechanism is reused
- "GitHub" link text in the footer is intentionally kept in English as a brand name (not translated)
- The hardcoded `Record<string, string>` objects for meta titles/descriptions in `+layout.svelte` will be replaced with proper i18n message keys to keep all translations in the locale JSON files
