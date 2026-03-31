# Feature Specification: Public Constitution Page

**Feature Branch**: `005-constitution-page`
**Created**: 2026-03-30
**Status**: Draft
**Input**: User description: "Página Pública de Constitution — dedicated i18n page presenting the 12 engineering mandates as public-facing principles"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse Constitution in Preferred Language (Priority: P1)

A visitor arrives at the landing page and clicks "Constitution" in the footer. They land on a dedicated page presenting the 12 engineering mandates in their current language, with the same premium visual style as the rest of the site.

**Why this priority**: This is the core purpose of the feature — converting an internal governance document into a public credibility asset across all 3 supported languages.

**Independent Test**: Navigate to `/en/constitution/`, `/pt/constituicao/`, or `/es/constitucion/` and verify the page renders 12 mandates with correct translations, hero section, transparency section, and consistent visual design.

**Acceptance Scenarios**:

1. **Given** a visitor on the English landing page, **When** they click "Constitution" in the footer, **Then** they are taken to `/en/constitution/` showing all 12 mandates in English with the same header, footer, and visual style as the landing page.
2. **Given** a visitor on the Portuguese landing page, **When** they click "Constituição" in the footer, **Then** they are taken to `/pt/constituicao/` showing all 12 mandates in Portuguese.
3. **Given** a visitor on the Spanish landing page, **When** they click "Constitución" in the footer, **Then** they are taken to `/es/constitucion/` showing all 12 mandates in Spanish.
4. **Given** a visitor on any language version, **When** they switch languages via the language selector, **Then** the Constitution page reloads in the selected language with correct content and URL slug.

---

### User Story 2 - Discover The Loop's Engineering Rigor (Priority: P1)

A developer or engineering manager reads through the 12 mandates to understand the engineering standards behind The Loop. Each mandate is presented as a principle (not as internal repo rules), building trust and credibility.

**Why this priority**: The Constitution page is a content/positioning asset — its value depends on the mandates being presented as compelling engineering principles, not internal governance details.

**Independent Test**: Read through all 12 mandate cards and verify each has a roman numeral, short title, and 1-2 sentence public-facing description with no internal implementation details (no mentions of CODEOWNERS, GitHub Actions, Firestore rules, specific branch protection settings, etc.).

**Acceptance Scenarios**:

1. **Given** a visitor on the Constitution page, **When** they view the mandates grid, **Then** each mandate shows a roman numeral (I through XII) in accent color, a bold title, and a concise public description.
2. **Given** a visitor reading the mandates, **When** they look for implementation details, **Then** none are present — no references to specific tools, configs, or internal processes.
3. **Given** a visitor on mobile (375px), **When** they view the mandates, **Then** they display in a single-column layout with generous spacing. On tablet (768px) they display in 2 columns. On desktop (1280px+) they display in 3 columns.

---

### User Story 3 - Access Full Constitution on GitHub (Priority: P2)

After reading the public summary, a visitor wants to see the full, unabridged Constitution document. A transparency section at the bottom of the page links directly to the CONSTITUTION.md on GitHub.

**Why this priority**: Reinforces transparency and open-source credibility, but secondary to the core page content.

**Independent Test**: Click the GitHub link in the transparency section and verify it opens the CONSTITUTION.md file in a new tab.

**Acceptance Scenarios**:

1. **Given** a visitor on the Constitution page, **When** they scroll to the transparency section, **Then** they see a message explaining the constitution lives in the public repository with a link to GitHub.
2. **Given** a visitor clicking the GitHub link, **When** the link opens, **Then** it navigates to `https://github.com/renatobardi/the-loop/blob/main/CONSTITUTION.md` in a new tab.

---

### User Story 4 - Convert from Constitution Page to Waitlist (Priority: P2)

A visitor impressed by the engineering principles wants to sign up for the waitlist. A CTA section at the bottom of the Constitution page (before the footer) lets them do so without navigating back to the landing page.

**Why this priority**: Maintains conversion consistency — every public page ends with a waitlist CTA — but is secondary to the core content presentation.

**Independent Test**: Submit a valid email in the waitlist form on the Constitution page and verify it processes correctly (success, duplicate, or rate-limited response).

**Acceptance Scenarios**:

1. **Given** a visitor on the Constitution page, **When** they scroll past the transparency section, **Then** they see a waitlist CTA section with the same design as the landing page's bottom CTA.
2. **Given** a visitor submitting an email on the Constitution page, **When** the form is submitted, **Then** the response follows the same state machine (success/duplicate/rate_limited/error) as the landing page form.

---

### Edge Cases

- What happens when a visitor navigates directly to `/en/constitution/` without coming from the landing page? The page must render independently with full header, footer, and meta tags.
- What happens when a visitor accesses the Constitution page URL without the trailing slash (e.g., `/en/constitution`)? The system redirects to the trailing-slash version per the existing `trailingSlash: 'always'` config.
- What happens when a visitor navigates to a non-existent localized slug (e.g., `/en/constituicao/`)? The route returns 404 — each locale has its own slug.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST serve the Constitution page at locale-specific URLs: `/en/constitution/`, `/pt/constituicao/`, `/es/constitucion/`
- **FR-002**: System MUST display a hero section with a headline ("12 Immutable Mandates" or locale equivalent) and a sub-headline describing the engineering principles
- **FR-003**: System MUST display all 12 mandates as individual cards, each with a roman numeral (I–XII), a short title, and a 1-2 sentence public-facing description
- **FR-004**: System MUST present mandate descriptions as engineering principles for external audiences — no internal implementation details
- **FR-005**: System MUST include a transparency section linking to the CONSTITUTION.md on GitHub (`https://github.com/renatobardi/the-loop/blob/main/CONSTITUTION.md`)
- **FR-006**: System MUST include a waitlist CTA section at the bottom of the page, reusing the existing waitlist component with source tracking (e.g., `source="constitution"`)
- **FR-007**: System MUST render the same header (logo, language selector) and footer as the landing page
- **FR-008**: Footer "Constitution" link MUST point to the locale-appropriate Constitution page route instead of the GitHub raw file
- **FR-009**: System MUST include correct `<title>`, `<meta name="description">`, Open Graph (`og:title`, `og:description`, `og:type`, `og:url`, `og:image`), and Twitter Card tags per locale
- **FR-010**: System MUST include `<link rel="alternate" hreflang="...">` tags for all 3 locale versions plus `x-default`
- **FR-011**: Mandate cards MUST use a responsive grid: 1 column on mobile, 2 columns on tablet, 3 columns on desktop
- **FR-012**: All text content MUST be served via the i18n system — no hardcoded strings in components

### Key Entities

- **Mandate**: Represents one of the 12 engineering principles. Attributes: number (I–XII), title (localized), description (localized). Static content defined as i18n message keys.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 3 locale versions of the Constitution page render correctly with 12 mandates each
- **SC-002**: Page is visually consistent with the landing page — same typography, color tokens, spacing, header, and footer
- **SC-003**: Footer Constitution link navigates to the in-app Constitution page (not GitHub) in the correct locale
- **SC-004**: Waitlist form on Constitution page successfully processes signups with `source="constitution"` tracking
- **SC-005**: Page is fully responsive at 375px (mobile), 768px (tablet), and 1280px (desktop) breakpoints
- **SC-006**: Meta tags (title, description, OG, hreflang) are correct and locale-specific on each version
- **SC-007**: Language switching from the Constitution page navigates to the correct localized Constitution URL

## Assumptions

- The 12 mandates are stable and will not change frequently — content is defined as i18n message keys, not fetched from a dynamic source
- The existing waitlist form action pattern will be replicated or shared for the Constitution page route
- The Constitution page slug is different per locale (`constitution`, `constituicao`, `constitucion`) — this requires localized route configuration
- The GitHub link target (`https://github.com/renatobardi/the-loop/blob/main/CONSTITUTION.md`) is a stable URL
- All mandate translations (EN, PT, ES) are provided in the feature description and do not need external translation review
