# Quickstart: Landing Page Design Polish

**Feature**: 002-landing-page-polish
**Date**: 2026-03-30

## Prerequisites

- Node.js 22 LTS
- `npm install` in `apps/web/`

## Development

```bash
cd apps/web
npm run dev
```

Visit `http://localhost:5173/en/` (all routes require locale prefix).

## Key Files to Modify

### New Components
1. `src/lib/ui/Navbar.svelte` — Sticky nav with hamburger menu
2. `src/lib/ui/SkipLink.svelte` — Skip-to-content accessibility link

### Modified Components (by priority)
1. `src/lib/components/LanguageSelector.svelte` — Add `tag` prop, increase touch targets
2. `src/lib/components/WaitlistForm.svelte` — Pass label to Input
3. `src/lib/ui/Input.svelte` — Add `label` prop (sr-only)
4. `src/lib/ui/Section.svelte` — Remove `min-h-screen`, keep for Hero only
5. `src/lib/components/Hero.svelte` — Add product name, scroll indicator
6. `src/lib/components/Pricing.svelte` — Add CTAs, highlight PAYG card
7. `src/lib/components/Footer.svelte` — Fix nav nesting
8. `src/lib/components/Problem.svelte` — Center heading
9. `src/lib/components/HowItWorks.svelte` — Center heading
10. `src/routes/+layout.svelte` — Add Navbar + SkipLink, remove floating LanguageSelector
11. `src/app.css` — Adjust `--color-text-subtle` for WCAG AA

### i18n Messages
- `messages/en.json`, `messages/pt.json`, `messages/es.json` — Add ~11 new keys

## Verification

```bash
npm run lint          # ESLint + Prettier
npm run check         # TypeScript strict + svelte-check
npm run test          # vitest
npm run build         # Production build
```

### Manual Testing Checklist
- [ ] Language selector: click EN/PT/ES in header and footer — verify correct URL
- [ ] Scroll: verify continuous narrative flow, no full-viewport gaps between sections
- [ ] Navbar: verify sticky behavior, anchor links smooth-scroll to correct sections
- [ ] Navbar mobile: verify hamburger menu opens/closes, links work
- [ ] Pricing CTAs: verify Free and PAYG cards have "Join the waitlist" buttons
- [ ] Pricing highlight: verify PAYG card is visually distinguished
- [ ] Screen reader: verify email inputs announced with "Email address" label
- [ ] Keyboard: verify Tab goes to skip link first, then through all interactive elements
- [ ] Contrast: run Lighthouse accessibility audit, verify 90+ score
- [ ] `prefers-reduced-motion`: verify smooth scroll disabled, section reveals instant
