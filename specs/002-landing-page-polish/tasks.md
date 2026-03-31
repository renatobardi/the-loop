# Tasks: i18n Audit & Complete Translation Fix

**Input**: Design documents from `/specs/002-landing-page-polish/`
**Prerequisites**: plan.md (required), spec.md (required), research.md
**Branch**: `fix/i18n-missing-translations`

**Tests**: Not explicitly requested — verification via `npm run check`, `npm run build`, and manual locale browsing.

**Organization**: Tasks grouped by translation area. No user stories — this is a single-scope bug fix (missing translations).

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `apps/web/src/` (SvelteKit)
- **i18n**: `apps/web/messages/` (Paraglide JSON)

---

## Phase 1: Locale File Translations

**Purpose**: Translate all untranslated keys in pt.json and es.json, add new key to all 3 files

### Pricing card values (9 keys per locale)

- [ ] T001 [P] Translate pricing keys in `apps/web/messages/pt.json`: `pricing_free_scans` → `100 scans/mês`, `pricing_payg_price` → `Pague por lote de scans`, `pricing_payg_scans` → `Compre em lotes`, `pricing_enterprise_price` → `Fale conosco`, `pricing_enterprise_scans` → `Ilimitado`, `pricing_support_community` → `Comunidade`, `pricing_support_dedicated` → `Dedicado`, `pricing_included` → `Incluído`, `pricing_contact_cta` → `Fale conosco`
- [ ] T002 [P] Translate pricing keys in `apps/web/messages/es.json`: `pricing_free_scans` → `100 scans/mes`, `pricing_payg_price` → `Paga por lote de scans`, `pricing_payg_scans` → `Compra por lotes`, `pricing_enterprise_price` → `Contáctanos`, `pricing_enterprise_scans` → `Ilimitado`, `pricing_support_community` → `Comunidad`, `pricing_support_dedicated` → `Dedicado`, `pricing_included` → `Incluido`, `pricing_contact_cta` → `Contáctanos`

### Footer text (3 keys per locale)

- [ ] T003 [P] Translate footer keys in `apps/web/messages/pt.json`: `footer_copyright` → `© 2026 Oute. Todos os direitos reservados.`, `footer_constitution` → `Constituição`, `footer_contact` → `Contato`
- [ ] T004 [P] Translate footer keys in `apps/web/messages/es.json`: `footer_copyright` → `© 2026 Oute. Todos los derechos reservados.`, `footer_constitution` → `Constitución`, `footer_contact` → `Contacto`

### Integration descriptions (3 keys per locale)

- [ ] T005 [P] Translate integration description keys in `apps/web/messages/pt.json`: `integration_github_desc` → `GitHub App com Check Runs, relatórios SARIF e comentários de review em PRs.`, `integration_ide_desc` → `Cursor, VS Code, Windsurf — escaneie código e receba advisories direto no seu editor.`, `integration_rest_desc` → `REST API com suporte a webhooks. Output em SARIF e JSON.`
- [ ] T006 [P] Translate integration description keys in `apps/web/messages/es.json`: `integration_github_desc` → `GitHub App con Check Runs, reportes SARIF y comentarios de review en PRs.`, `integration_ide_desc` → `Cursor, VS Code, Windsurf — escanea código y recibe advisories directo en tu editor.`, `integration_rest_desc` → `REST API con soporte de webhooks. Output en SARIF y JSON.`

### New key: Language selector aria-label

- [ ] T007 [P] Add `footer_language_selector_label` key to `apps/web/messages/en.json` with value `Language`
- [ ] T008 [P] Add `footer_language_selector_label` key to `apps/web/messages/pt.json` with value `Idioma`
- [ ] T009 [P] Add `footer_language_selector_label` key to `apps/web/messages/es.json` with value `Idioma`

**Checkpoint**: All locale files have complete translations. All 3 files have identical key sets.

---

## Phase 2: Component Updates

**Purpose**: Wire new i18n key into LanguageSelector and add hreflang tags to layout

- [ ] T010 Update `apps/web/src/lib/components/LanguageSelector.svelte` — import `footer_language_selector_label` from `$lib/paraglide/messages.js` and replace both hardcoded `aria-label="Language selector"` strings (line 20 for `<nav>` and line 35 for `<div>`) with `aria-label={footer_language_selector_label()}`
- [ ] T011 Add hreflang `<link>` tags to `apps/web/src/routes/+layout.svelte` — inside `<svelte:head>`, add 4 link elements: `<link rel="alternate" hreflang="en" href="https://loop.oute.pro/en/" />`, `<link rel="alternate" hreflang="pt" href="https://loop.oute.pro/pt/" />`, `<link rel="alternate" hreflang="es" href="https://loop.oute.pro/es/" />`, `<link rel="alternate" hreflang="x-default" href="https://loop.oute.pro/en/" />`

**Checkpoint**: LanguageSelector aria-label is localized; hreflang tags present in `<head>`

---

## Phase 3: Verification & Build

**Purpose**: Ensure all changes compile, pass linting, and render correctly

- [ ] T012 Run `npm run check` in `apps/web/` — verify Paraglide compiles new key and all TypeScript types resolve
- [ ] T013 [P] Run `npm run lint` in `apps/web/` — fix any ESLint/Prettier violations
- [ ] T014 Run `npm run build` in `apps/web/` — verify production build succeeds
- [ ] T015 Run `npm run dev` in `apps/web/` and manually verify: (1) `/pt/` — all pricing, footer, integration text in Portuguese, (2) `/es/` — all pricing, footer, integration text in Spanish, (3) `/en/` — no regressions, (4) language selector works on all 3 locales, (5) view page source — hreflang tags present, (6) LanguageSelector aria-label reads "Idioma" on `/pt/` and `/es/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies — can start immediately. All T001–T009 are independent and parallelizable.
- **Phase 2**: T010 depends on T007–T009 (new key must exist in locale files for Paraglide to generate the import). T011 has no dependencies.
- **Phase 3**: Depends on Phase 1 + Phase 2 completion.

### Parallel Opportunities

```text
# All Phase 1 tasks can run in parallel (different files):
T001, T002, T003, T004, T005, T006, T007, T008, T009

# Phase 2 tasks can run in parallel with each other:
T010, T011

# Phase 3 check/lint can run in parallel:
T012, T013
```

---

## Implementation Strategy

### Single-Pass Delivery

This is a focused translation fix — no incremental delivery needed.

1. Complete Phase 1: All locale file edits (9 parallel tasks)
2. Complete Phase 2: Two component updates (2 parallel tasks)
3. Complete Phase 3: Build verification + manual testing
4. Create PR to `main`

**Estimated scope**: 3 JSON files edited, 2 Svelte components edited. Zero new files. Zero UI restructuring.

---

## Notes

- All [P] tasks in Phase 1 edit different files — maximum parallelism
- Paraglide auto-compiles on Vite dev server start — no manual codegen needed
- Keep `pricing_free_scans` as `100 scans/mês` (not `100/mês`) since the card layout has no separate row labels
- Brand names ("The Loop", "GitHub", "by Oute") stay as-is — identical in all 3 locales by design
- The nested `<nav>` issue in footer is already resolved (`tag="div"` on LanguageSelector)
