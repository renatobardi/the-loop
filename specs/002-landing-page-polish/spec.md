# Feature Specification: Landing Page Design Polish

**Feature Branch**: `002-landing-page-polish`
**Created**: 2026-03-30
**Status**: Draft
**Input**: Design critique of The Loop landing page (EN) identifying 12 priority improvements across usability, visual hierarchy, consistency, and accessibility.

## Clarifications

### Session 2026-03-30

- Q: How should the sticky nav behave on mobile? → A: Hamburger menu — product name + burger icon always visible, links expand on tap.
- Q: Which sections should the sticky nav link to? → A: 3 links — Features (scrolls to Three Layers section), Pricing, Waitlist.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visitor Identifies the Product (Priority: P1)

A first-time visitor lands on the page and immediately sees the product name "The Loop" prominently displayed, understands what it does, and knows who makes it. Currently, the product name is absent from the hero — visitors only discover it in the footer.

**Why this priority**: Brand recognition is foundational. A visitor who can't name your product can't recommend it, search for it, or remember it.

**Independent Test**: Load the page and verify "The Loop" is visible without scrolling, positioned near the hero headline.

**Acceptance Scenarios**:

1. **Given** a first-time visitor lands on `/en/`, **When** the page loads, **Then** the product name "The Loop" is visible above the fold without scrolling.
2. **Given** a visitor on any locale (`/en/`, `/pt/`, `/es/`), **When** the page loads, **Then** the product name appears consistently in the same position.
3. **Given** a visitor on mobile (viewport < 768px), **When** the page loads, **Then** the product name is still visible and legible above the fold.

---

### User Story 2 - Visitor Switches Language Successfully (Priority: P1)

A visitor clicks a language option (EN, PT, or ES) in either the header or footer language selector and is taken to the correct locale version of the page. Currently, clicking language links produces doubled prefixes (`/en/en/`, `/pt/pt/`) causing broken navigation.

**Why this priority**: This is a functional bug that breaks a core feature. International visitors cannot switch languages.

**Independent Test**: Click each language option in both header and footer selectors; verify correct navigation to `/{locale}/` without doubled prefixes.

**Acceptance Scenarios**:

1. **Given** a visitor on `/en/`, **When** they click "PT" in the header language selector, **Then** they are navigated to `/pt/` (not `/en/pt/` or `/pt/pt/`).
2. **Given** a visitor on `/pt/`, **When** they click "ES" in the footer language selector, **Then** they are navigated to `/es/`.
3. **Given** a visitor on any locale, **When** they click the language option for their current locale, **Then** the page remains on the same locale without URL corruption.

---

### User Story 3 - Screen Reader User Completes Waitlist Signup (Priority: P1)

A visitor using a screen reader navigates to the waitlist form, hears a proper label for the email input, enters their email, and submits. Currently, the email inputs lack associated `<label>` elements — screen readers only announce the placeholder text, which disappears on focus.

**Why this priority**: Accessibility is both a legal obligation and an ethical baseline. Missing form labels block assistive technology users from the primary conversion action.

**Independent Test**: Navigate the form using a screen reader (VoiceOver/NVDA); verify the email input is announced with a descriptive label.

**Acceptance Scenarios**:

1. **Given** a screen reader user navigates to the hero waitlist form, **When** the email input receives focus, **Then** the screen reader announces "Email address" (or equivalent localized label).
2. **Given** a screen reader user navigates to the bottom waitlist CTA form, **When** the email input receives focus, **Then** the screen reader announces the same descriptive label.
3. **Given** a keyboard-only user, **When** they press Tab from the top of the page, **Then** a "Skip to main content" link is the first focusable element.

---

### User Story 4 - Visitor Scrolls Through a Cohesive Narrative (Priority: P2)

A visitor scrolls from the hero through all sections and experiences a continuous narrative flow — not a disconnected "slide deck." Currently, excessive vertical whitespace (~400px+) between sections creates gaps that may make visitors think the page has ended.

**Why this priority**: Narrative flow directly impacts scroll depth and conversion. Visitors who think the page ended at the Problem section never see pricing or the waitlist CTA.

**Independent Test**: Scroll through the page on desktop and mobile; verify no section gap is large enough to fill the viewport with empty space.

**Acceptance Scenarios**:

1. **Given** a visitor on desktop (1440px viewport), **When** they scroll past any section, **Then** the next section heading is partially visible before the previous section fully exits the viewport.
2. **Given** a visitor on mobile, **When** they scroll past the hero, **Then** a scroll-down indicator (chevron or similar) hints that more content exists below.
3. **Given** a visitor viewing the hero, **When** they look at the full viewport, **Then** the top of the next section is at least partially visible or a visual cue indicates more content below.

---

### User Story 5 - Visitor Evaluates Pricing and Takes Action (Priority: P2)

A visitor scrolls to the pricing section, compares tiers, identifies the recommended option, and clicks a CTA to join the waitlist. Currently, only the Enterprise card has a CTA button, and all three cards look visually identical with no "recommended" indicator.

**Why this priority**: Pricing is the decision point. Missing CTAs on two of three cards and no visual hierarchy between tiers leaves visitors without a clear next step.

**Independent Test**: Scroll to pricing; verify each card has a CTA button and the middle tier is visually distinguished.

**Acceptance Scenarios**:

1. **Given** a visitor views the pricing section, **When** they see the Free tier card, **Then** a "Join the waitlist" button is visible on the card.
2. **Given** a visitor views the pricing section, **When** they see the Pay-as-you-go card, **Then** it is visually elevated (distinct border, badge, or scale) compared to the other two cards.
3. **Given** a visitor clicks "Join the waitlist" on a pricing card, **When** the action triggers, **Then** the page scrolls smoothly to the nearest waitlist form.
4. **Given** a visitor views the Enterprise card, **When** they see the "Contact us" button, **Then** it triggers a mailto link to the contact email.

---

### User Story 6 - Visitor Navigates Long Page Efficiently (Priority: P2)

A visitor uses a sticky navigation bar to jump directly to sections of interest (Features, Pricing, Waitlist) without scrolling through the entire page. Currently, no navigation or anchor links exist.

**Why this priority**: On a single-page landing with 8+ sections, orientation and quick access significantly improve user experience, especially on mobile.

**Independent Test**: Click each nav link; verify smooth scroll to the correct section. Verify the nav remains visible while scrolling.

**Acceptance Scenarios**:

1. **Given** a visitor is anywhere on the page, **When** they look at the top of the viewport, **Then** a sticky navigation bar is visible with the product name and three section links: Features, Pricing, Waitlist.
2. **Given** a visitor clicks "Features" in the nav, **When** the click registers, **Then** the page scrolls smoothly to the Three Layers section.
3. **Given** a visitor clicks "Pricing" in the nav, **When** the click registers, **Then** the page scrolls smoothly to the pricing section.
4. **Given** a visitor on mobile, **When** they view the nav bar, **Then** only the product name and a hamburger icon are visible; tapping the icon expands the three nav links.

---

### User Story 7 - Visitor Reads All Content Comfortably (Priority: P3)

A visitor reads body text, sub-headlines, and card details without eye strain. Currently, gray body text on the dark background likely fails WCAG AA contrast requirements (4.5:1 ratio), particularly in the Problem section and pricing card details.

**Why this priority**: Readability directly affects comprehension and trust. Low-contrast text on a dark background signals carelessness to detail-oriented developer audiences.

**Independent Test**: Measure contrast ratios of all body text colors against their backgrounds; verify all meet WCAG AA (4.5:1 for normal text, 3:1 for large text).

**Acceptance Scenarios**:

1. **Given** any body text on the page, **When** its contrast ratio is measured against its background, **Then** it meets or exceeds 4.5:1 (WCAG AA).
2. **Given** the "by Oute" text in the hero, **When** its contrast is measured, **Then** it meets 4.5:1 or the text is removed/restyled.
3. **Given** large text (headings, section titles), **When** contrast is measured, **Then** it meets or exceeds 3:1 (WCAG AA for large text).

---

### User Story 8 - Consistent Visual Language Across Sections (Priority: P3)

A visitor scrolling through the page perceives a unified design — consistent section alignment, card styling, and badge patterns. Currently, section headings alternate between centered and left-aligned, card treatments are ~90% similar (which reads as inconsistent), and badge patterns are applied unevenly.

**Why this priority**: Visual consistency builds trust and professionalism. Subtle inconsistencies accumulate into a perception of unfinished work.

**Independent Test**: Compare all section headings for alignment, all card components for styling uniformity, and badge usage across sections.

**Acceptance Scenarios**:

1. **Given** any section on the page, **When** its heading is rendered, **Then** it uses centered alignment (standardized across all sections).
2. **Given** any card component (Layers, Integrations, Pricing), **When** rendered, **Then** it uses identical border-radius, background color, and padding from the shared Card component.
3. **Given** the footer, **When** the language selector is rendered, **Then** it is not nested inside another `<nav>` element (uses `div` with `role="group"` or equivalent).

---

### Edge Cases

- What happens when a visitor resizes the browser from desktop to mobile while the sticky nav is open?
- How does the sticky nav behave when the page has very little content (e.g., if sections are conditionally hidden)?
- What happens when a pricing card CTA is clicked but the waitlist form is not in the viewport (smooth scroll distance)?
- How do language selector touch targets behave on small mobile screens (< 375px width)?
- What happens to the scroll-down indicator once the user has scrolled past the hero?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Page MUST display the product name "The Loop" prominently above the fold, visible without scrolling on all viewports.
- **FR-002**: Language selector links MUST navigate to the correct locale path (`/{locale}/`) without doubled prefixes on all supported locales (EN, PT, ES).
- **FR-003**: All email input fields MUST have associated visually-hidden `<label>` elements that are announced by screen readers.
- **FR-004**: Page MUST include a "Skip to main content" link as the first focusable element, visually hidden until focused.
- **FR-005**: Section vertical spacing MUST create a continuous narrative scroll where the next section is partially visible or hinted at before the current section exits the viewport.
- **FR-006**: Free and Pay-as-you-go pricing cards MUST each include a CTA button that scrolls to the nearest waitlist form.
- **FR-007**: Pay-as-you-go pricing card MUST be visually distinguished from other tiers (via badge, border treatment, or scale).
- **FR-008**: Page MUST include a sticky navigation bar with the product name and three anchor links: Features (→ Three Layers section), Pricing, and Waitlist. On mobile (< 768px), the nav MUST collapse to a hamburger menu showing only the product name and a menu icon, with links expanding on tap.
- **FR-009**: All body text MUST meet WCAG AA contrast requirements (4.5:1 for normal text, 3:1 for large text) against their backgrounds.
- **FR-010**: All section headings MUST use consistent centered alignment.
- **FR-011**: All card components (Layers, Integrations, Pricing) MUST use unified styling from the shared design system Card component.
- **FR-012**: Footer language selector MUST NOT be nested inside another `<nav>` element.
- **FR-013**: Hero section MUST include a scroll-down indicator (animated chevron or similar) to signal more content below.
- **FR-014**: Language selector touch targets MUST meet minimum 44x44px tap area on mobile devices.
- **FR-015**: Anchor link navigation MUST use smooth scrolling behavior that respects `prefers-reduced-motion`.

### Key Entities

- **Navigation Bar**: Sticky header element containing product name (wordmark), three section anchor links (Features, Pricing, Waitlist), and language selector. On mobile, collapses to hamburger menu.
- **Pricing Card CTA**: Action button on each pricing tier that drives toward waitlist conversion or contact.
- **Skip Link**: Visually hidden, keyboard-focusable link that bypasses navigation to reach main content.
- **Scroll Indicator**: Visual cue in the hero section that signals scrollable content below the fold.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of language selector clicks navigate to the correct locale path without URL corruption (zero doubled-prefix occurrences).
- **SC-002**: Product name "The Loop" is visible above the fold on viewports from 320px to 2560px wide.
- **SC-003**: All text on the page meets WCAG AA contrast ratios (4.5:1 normal, 3:1 large) — zero failures when audited.
- **SC-004**: All interactive elements (links, buttons, inputs) are operable via keyboard alone, with visible focus indicators.
- **SC-005**: Average scroll depth increases (visitors reach pricing section) — measurable via analytics after deployment.
- **SC-006**: Every pricing tier card has a clickable CTA that leads to a conversion action (waitlist form or contact).
- **SC-007**: Page scores 90+ on Lighthouse Accessibility audit (up from current estimated ~60-70).
- **SC-008**: Sticky nav allows visitors to reach any major section in a single click from anywhere on the page.

## Assumptions

- The existing design system (colors, fonts, spacing tokens) will be reused — no brand redesign is in scope.
- "The Loop" wordmark will be text-based (no logo/image asset required for now) — a designed logo is out of scope.
- The language selector bug is a href generation issue in the i18n layer, not a server-side routing problem.
- All i18n message keys for new UI elements (nav labels, CTA text, accessibility labels) will be added to all three locale files (EN, PT, ES).
- The "by Oute" text in the hero may be removed or moved to the footer only — the decision is left to implementation.
- Social proof / waitlist count display is explicitly out of scope for this feature (mentioned as P2 consideration in the critique but deferred).
- Focus state styling and `prefers-reduced-motion` compliance will be verified and fixed where missing, but full animation overhaul is not in scope.
