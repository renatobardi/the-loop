# Feature Specification: Waitlist Source Tracking + Pricing CTAs

**Feature Branch**: `004-waitlist-pricing-ctas`
**Created**: 2026-03-30
**Status**: Draft
**Input**: User description: "Waitlist CTA nos Pricing Cards + Email Funcional nos 2 Pontos"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Differentiated Source Tracking (Priority: P1)

A visitor submits their email via the Hero form. The system records `source: "hero"` in Firestore. Another visitor submits via the bottom waitlist CTA (Section 7). The system records `source: "cta-bottom"`. The product owner can later query Firestore to understand which entry point converts better.

**Why this priority**: Source attribution is the core analytics gap. Without it, there is no way to measure which CTA placement drives conversions, making pricing card CTAs and layout decisions data-blind.

**Independent Test**: Submit emails from each form and verify the correct source value appears in Firestore.

**Acceptance Scenarios**:

1. **Given** a visitor on the landing page, **When** they submit a valid email via the Hero form, **Then** the Firestore document contains `source: "hero"`.
2. **Given** a visitor on the landing page, **When** they submit a valid email via the Section 7 (WaitlistCta) form, **Then** the Firestore document contains `source: "cta-bottom"`.
3. **Given** an email already registered with `source: "hero"`, **When** the same email is submitted via the Section 7 form, **Then** the system shows the "already on the list" message and does not overwrite the original source.

---

### User Story 2 - Pricing Card CTAs Link to Waitlist (Priority: P2)

A visitor reads the pricing cards (Free and Pay-as-you-go) and wants to sign up. Each card has a clear CTA button that scrolls them smoothly to the waitlist signup form at the bottom of the page.

**Why this priority**: Pricing cards without a CTA are a dead-end — the visitor has intent but no path to act. Anchor links to the existing waitlist form avoid duplicating form logic while capturing conversion intent.

**Independent Test**: Click the CTA on each pricing card and verify smooth scroll to the `#waitlist` section.

**Acceptance Scenarios**:

1. **Given** the Free pricing card, **When** a visitor clicks its CTA button, **Then** the page scrolls smoothly to the `#waitlist` section.
2. **Given** the Pay-as-you-go pricing card, **When** a visitor clicks its CTA button, **Then** the page scrolls smoothly to the `#waitlist` section.
3. **Given** the Pay-as-you-go card, **When** a visitor views the pricing section, **Then** the card displays a "Most popular" badge for visual differentiation.
4. **Given** the Enterprise card, **When** a visitor clicks "Contact us", **Then** their email client opens with the contact address pre-filled.

---

### User Story 3 - Accessible Waitlist Forms (Priority: P2)

A visitor using a screen reader navigates to either waitlist form. The email input is properly labeled and announced. Keyboard navigation works for both forms with visible focus states.

**Why this priority**: Accessibility is a P0 concern per the design critique and legally required. Both forms must be usable without a mouse.

**Independent Test**: Use a screen reader to navigate each form and verify the email input label is announced correctly in the current locale.

**Acceptance Scenarios**:

1. **Given** either waitlist form, **When** a screen reader focuses the email input, **Then** it announces the label in the current locale (EN: "Email address", PT: "Endereço de email", ES: "Dirección de email").
2. **Given** either waitlist form, **When** a visitor uses Tab to navigate, **Then** focus states are visible on both the input and the submit button.

---

### User Story 4 - Full i18n Coverage (Priority: P2)

All user-facing strings in the waitlist forms, pricing CTAs, and feedback messages are translated into all three supported locales (EN, PT-BR, ES).

**Why this priority**: The site supports three locales; untranslated strings break the experience for non-English visitors.

**Independent Test**: Switch to each locale and verify all waitlist and pricing strings render in the correct language.

**Acceptance Scenarios**:

1. **Given** the page in `/pt/`, **When** the visitor views the pricing cards, **Then** CTA buttons and badges display in Portuguese.
2. **Given** the page in `/es/`, **When** the visitor submits a duplicate email, **Then** the feedback message displays in Spanish.

---

### Edge Cases

- What happens when a visitor submits the form without JavaScript? Progressive enhancement ensures the form still submits as a standard POST and the server returns the correct status.
- What happens when the `source` hidden field is tampered with? The server validates the source value against an allowlist (`"hero"`, `"cta-bottom"`). Invalid values default to `"unknown"`.
- What if rate limiting triggers across both forms? Rate limiting is per IP, not per form — submitting 5 times across both forms within 60 seconds triggers the limit.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Each waitlist form MUST include a hidden field identifying its source (`"hero"` or `"cta-bottom"`).
- **FR-002**: The server action MUST extract the `source` field from form data, validate it against an allowlist, and pass it to the Firestore write function.
- **FR-003**: The Firestore document MUST store the submitted `source` value instead of the hardcoded `"landing"`.
- **FR-004**: The Free and Pay-as-you-go pricing cards MUST each display a CTA button that links to `#waitlist` with smooth scroll behavior.
- **FR-005**: The Pay-as-you-go card MUST display a "Most popular" badge.
- **FR-006**: The Free card CTA MUST use a secondary (outline) button variant; the Pay-as-you-go card CTA MUST use a primary (filled) button variant.
- **FR-007**: All user-facing strings (CTA labels, badges, form feedback, input labels) MUST be available in EN, PT-BR, and ES via Paraglide message keys.
- **FR-008**: Both waitlist form email inputs MUST have an accessible label (sr-only) that is announced by screen readers in the current locale.
- **FR-009**: Duplicate email submissions MUST show a friendly message without creating a duplicate Firestore document, preserving the original source value.
- **FR-010**: Server-side validation MUST reject invalid source values, defaulting to `"unknown"`.

### Key Entities

- **Waitlist Entry**: Represents a user who signed up for early access. Key attributes: email (unique identifier), locale (detected from route), source (which CTA originated the signup: `"hero"`, `"cta-bottom"`, or `"unknown"`), created_at (server timestamp).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of waitlist submissions record the correct source value (`"hero"` or `"cta-bottom"`) instead of a hardcoded value.
- **SC-002**: All three pricing cards display a CTA — Free and Pay-as-you-go link to the waitlist form, Enterprise opens email.
- **SC-003**: All user-facing strings render correctly in all three locales (EN, PT-BR, ES) with zero untranslated keys.
- **SC-004**: Screen readers announce the email input label correctly in the active locale on both waitlist forms.
- **SC-005**: Clicking a pricing card CTA scrolls the page smoothly to the waitlist section within 1 second.

## Assumptions

- The existing waitlist Firestore write logic (duplicate detection, rate limiting, Zod validation) is correct and only needs the `source` parameter added.
- Pricing cards already exist with the correct visual design; this feature adds CTAs and a badge, not a redesign.
- The `#waitlist` anchor ID is already present on the WaitlistCta section wrapper.
- Smooth scroll behavior can rely on CSS `scroll-behavior: smooth` or the existing browser default — no JavaScript scroll library is needed.
- The Input UI component already supports sr-only labels via its `label` prop.
