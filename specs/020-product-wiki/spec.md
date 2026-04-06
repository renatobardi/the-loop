# Spec-020: Product Wiki

**Status**: Ready for implementation  
**Branch**: `feat/020-product-wiki`  
**Created**: 2026-04-05  
**Author**: @renatobardi

---

## Overview

Create a public, in-product documentation wiki at `/docs/` that serves as the single reference for every persona interacting with The Loop. Each section is written for a specific audience and links to related sections.

The wiki is fully static (no backend changes), served from SvelteKit, public (no auth required), and uses the existing design system.

---

## Problem

There is no structured documentation for The Loop. Users in different roles — developers configuring CI, IT managers reviewing analytics, security teams auditing rules — have no guidance beyond the UI itself. This creates friction for adoption and increases support load.

---

## Goals

1. One URL per topic, shareable and linkable.
2. Persona-filtered home page: pick your role → see curated path.
3. Full coverage of every major platform capability.
4. Zero new backend dependencies.

---

## Out of Scope

- Search functionality (no backend for full-text search).
- Versioned docs (no multi-version support).
- Localization (English only, same as product).
- MDsveX or any new markdown pipeline.

---

## Personas & Primary Needs

| Persona | Primary Questions | Key Sections |
|---------|-------------------|--------------|
| **Developer** | How do I integrate the scanner? What are API keys? | Semgrep, API Keys, API Reference, Rules |
| **IT Manager** | How do I onboard my team? What do the analytics mean? | Getting Started, Analytics, Administration |
| **Operator** | How do I manage incidents? What's the postmortem flow? | Incidents, Postmortems |
| **Support** | How do I triage an incident? Where are postmortems? | Incidents, Postmortems |
| **QA** | How do I test rules? How do I read scan history? | Semgrep, Rules |
| **Security** | What's the auth model? How do API keys scope access? | Security, API Keys, Rules, Administration |

---

## Information Architecture

```
/docs/                        — Home: persona picker + feature index
/docs/getting-started/        — Onboarding (account setup, first incident)
/docs/incidents/              — Incident lifecycle (create → manage → close)
/docs/postmortems/            — Postmortem capture, templates, locking
/docs/analytics/              — Dashboard guide (KPIs, filters, drill-down)
/docs/semgrep/                — Scanner setup, CI/CD workflow, fallback
/docs/api-keys/               — Create, rotate, scope, revoke API keys
/docs/rules/                  — Browse rules, understand findings, whitelisting
/docs/administration/         — Team management, configuration, rate limits
/docs/security/               — Auth model, data isolation, compliance
/docs/api-reference/          — Endpoint index, auth headers, response formats
```

---

## Acceptance Criteria

- [ ] `/docs/` renders a persona picker with 6 roles; selecting a role highlights curated links.
- [ ] All 10 section pages exist and render without errors.
- [ ] Every page has a `<title>`, `<meta name="description">`, and canonical URL.
- [ ] Navbar includes a "Docs" link visible on all pages.
- [ ] All pages load without auth (public, SSR enabled).
- [ ] No ad-hoc styling — design tokens only.
- [ ] `npm run check` and `npm run lint` pass.
- [ ] `npm run build` passes.

---

## Non-Goals / Constraints

- Do not introduce MDsveX or any new frontend dependency.
- Do not add backend routes or DB changes.
- Do not require auth to view any doc page.
