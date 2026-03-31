# Research: Landing Page Design Polish

**Feature**: 002-landing-page-polish
**Date**: 2026-03-30

## R1: Language Selector Doubled Prefix Root Cause

**Decision**: The current `LanguageSelector.svelte` already uses the correct pattern (`href="/"` + `hreflang={locale}`), which relies on Paraglide's `translateHref()` to generate `/{locale}/`. The bug reported in the design critique (doubled prefixes like `/en/en/`) was likely present in a previous version and has been fixed in the `fix/i18n-definitive` branch (commit `a170987`). Verification needed: confirm the fix on the current branch and ensure it works correctly in production.

**Rationale**: Paraglide-SvelteKit's link translation intercepts `<a>` elements with `hreflang` attributes and rewrites the `href` to the target locale path. Using `href="/"` as the base avoids double-prefixing because Paraglide replaces the entire path rather than prepending.

**Alternatives considered**:
- Hardcoded absolute URLs (`href="/en/"`, `href="/pt/"`) — rejected because Paraglide would still translate these, causing double-prefixing.
- Using Paraglide's `i18n.resolveRoute()` API directly — unnecessary complexity when `hreflang` attribute handles it.

## R2: Section Spacing — Root Cause of Excessive Whitespace

**Decision**: The `Section.svelte` component uses `min-h-screen` which forces every section to take at least the full viewport height. Combined with `flex items-center` (vertical centering) and `py-20 lg:py-32` padding, this creates massive empty gaps between content blocks. Fix: remove `min-h-screen` from the default Section component; apply it only to the Hero section via class override.

**Rationale**: The design critique identified ~400px+ gaps between sections. The root cause is `min-h-screen` on every section — short content sections get vertically centered in a full-viewport container, creating the "slide deck" effect. Removing it lets sections size to their content naturally.

**Alternatives considered**:
- Reducing padding only (keeping `min-h-screen`) — still creates gaps for short sections.
- Using a `compact` prop on Section — adds unnecessary API surface when simply removing `min-h-screen` and keeping padding achieves the goal.

## R3: WCAG AA Contrast Compliance

**Decision**: Adjust `--color-text-subtle` from `#71717a` to `#8b8b95` (or similar) to meet 4.5:1 ratio against `#0a0a0b` background. Current `--color-text-muted` (#a1a1aa) already passes at ~7:1.

**Rationale**:
- `#71717a` on `#0a0a0b` = ~4.48:1 — borderline fail for WCAG AA normal text (requires 4.5:1).
- `#71717a` on `#141416` (bg-surface) = ~3.93:1 — fails WCAG AA for normal text.
- Bumping to ~`#8b8b95` achieves ~5.5:1 against `#0a0a0b` and ~4.8:1 against `#141416`, passing both.
- The "by Oute" text uses `text-text-subtle` at `text-sm` size — this must pass 4.5:1 for normal text.

**Alternatives considered**:
- Bumping to `#D1D5DB` as the critique suggested — too close to `text-muted`, collapses the 3-tier text hierarchy.
- Keeping current value and only increasing font size where needed — doesn't fix the underlying token.

## R4: Sticky Navigation with Hamburger Menu

**Decision**: Create a new `Navbar.svelte` UI component with:
- Desktop: fixed bar at top with "The Loop" text (left), 3 anchor links (center/right: Features, Pricing, Waitlist), language selector (far right).
- Mobile (< 768px): "The Loop" text + hamburger icon. Tap expands a dropdown panel with the 3 links + language selector.
- Background: `bg-bg/80 backdrop-blur-md` for translucent dark effect consistent with dark theme.
- Smooth scroll: `scroll-behavior: smooth` on `<html>`, with `@media (prefers-reduced-motion: reduce) { scroll-behavior: auto }`.

**Rationale**: Hamburger menu is the established mobile pattern. Translucent backdrop matches premium dark aesthetic. Three links (Features, Pricing, Waitlist) keep the nav scannable without overwhelming.

**Alternatives considered**:
- Auto-hide on scroll down — more complex interaction, less accessible for users who need persistent navigation.
- Bottom nav bar on mobile — unconventional for landing pages, better suited for apps.

## R5: Product Name Placement

**Decision**: Display "The Loop" as a text wordmark in two locations:
1. **Navbar** (left-aligned): Always visible, serves as brand anchor and home link.
2. **Hero** (above headline): Smaller text-lg or text-xl above the h1, providing context before the value proposition.

The hero `h1` stays as the value proposition headline ("Eliminate production incidents..."). "The Loop" in the hero is presentational context, not the h1 — the h1 remains the SEO-optimized action headline.

**Rationale**: The navbar gives persistent brand visibility. The hero placement ensures first-time visitors see the product name without relying on the nav. Using text (not an image) avoids the need for a designed logo asset.

**Alternatives considered**:
- Making "The Loop" the h1 and demoting the headline to h2 — weakens SEO value of the action-oriented headline.
- Only in navbar, not in hero — first-time visitors may not notice the nav product name if they're focused on the hero content.

## R6: Footer Nav Nesting Fix

**Decision**: Change `LanguageSelector.svelte` to accept a `tag` prop (default `'nav'`). In Footer, pass `tag="div"` with `role="group"` and `aria-label="Language selector"` to avoid the nested `<nav>` > `<nav>` issue. The header instance keeps the default `<nav>` tag.

**Rationale**: Semantic HTML requires that `<nav>` elements represent major navigation blocks. Nesting one nav inside another creates confusing landmark structure for screen readers. Using a `div` with `role="group"` maintains the grouping semantics without the nesting issue.

**Alternatives considered**:
- Moving language selector outside the footer `<nav>` — requires restructuring footer layout.
- Removing `<nav>` from LanguageSelector entirely — loses landmark semantics when used standalone in the header.
