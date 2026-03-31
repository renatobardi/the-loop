# Data Model: Complete i18n Audit & Fix

**Branch**: `003-i18n-audit-fix` | **Date**: 2026-03-30

## Entities

### Locale File (en.json, pt.json, es.json)

Flat JSON key-value store. Keys use `snake_case`. All three files MUST have identical key sets.

**New keys to add** (all three files):

| Key | EN | PT | ES |
|-----|----|----|-----|
| `meta_title` | `The Loop — Eliminate production incidents before they happen` | `The Loop — Elimine incidentes de produção antes que aconteçam` | `The Loop — Elimina incidentes de producción antes de que ocurran` |
| `meta_description` | `Close the loop between post-mortems and code. Transform incident knowledge into active guardrails in your CI/CD pipeline.` | `Feche o ciclo entre post-mortems e código. Transforme conhecimento de incidentes em guardrails ativos no seu pipeline de CI/CD.` | `Cierra el ciclo entre post-mortems y código. Transforma el conocimiento de incidentes en guardrails activos en tu pipeline de CI/CD.` |
| `footer_language_selector_label` | `Language` | `Idioma` | `Idioma` |

**Existing keys to update** (PT and ES only — EN values are correct):

| Key | PT (current → new) | ES (current → new) |
|-----|---------------------|---------------------|
| `integration_github_desc` | EN text → `GitHub App com Check Runs, relatórios SARIF e comentários de review em PRs.` | EN text → `GitHub App con Check Runs, reportes SARIF y comentarios de review en PRs.` |
| `integration_ide_desc` | EN text → `Cursor, VS Code, Windsurf — escaneie código e receba advisories direto no seu editor.` | EN text → `Cursor, VS Code, Windsurf — escanea código y recibe advisories directo en tu editor.` |
| `integration_rest_desc` | EN text → `REST API com suporte a webhooks. Output em SARIF e JSON.` | EN text → `REST API con soporte de webhooks. Output en SARIF y JSON.` |
| `pricing_free_scans` | `100 scans/month` → `100 scans/mês` | `100 scans/month` → `100 scans/mes` |
| `pricing_payg_price` | `Pay per scan batch` → `Pague por lote de scans` | `Pay per scan batch` → `Paga por lote de scans` |
| `pricing_payg_scans` | `Buy in batches` → `Compre em lotes` | `Buy in batches` → `Compra por lotes` |
| `pricing_enterprise_price` | `Contact us` → `Fale conosco` | `Contact us` → `Contáctanos` |
| `pricing_enterprise_scans` | `Unlimited` → `Ilimitado` | `Unlimited` → `Ilimitado` |
| `pricing_support_community` | `Community` → `Comunidade` | `Community` → `Comunidad` |
| `pricing_support_dedicated` | `Dedicated` → `Dedicado` | `Dedicated` → `Dedicado` |
| `pricing_included` | `Included` → `Incluído` | `Included` → `Incluido` |
| `pricing_contact_cta` | `Contact us` → `Fale conosco` | `Contact us` → `Contáctanos` |
| `footer_copyright` | `© 2026 Oute. All rights reserved.` → `© 2026 Oute. Todos os direitos reservados.` | `© 2026 Oute. All rights reserved.` → `© 2026 Oute. Todos los derechos reservados.` |
| `footer_constitution` | `Constitution` → `Constituição` | `Constitution` → `Constitución` |
| `footer_contact` | `Contact` → `Contato` | `Contact` → `Contacto` |

## Validation Rules

- All three locale files MUST have identical key sets (parity check)
- No key may have an empty string value
- Keys use `snake_case` naming convention
- Brand names and technical terms per FR-010 MUST remain in English across all locales
