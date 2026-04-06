# Feature Specification: Product Docs

**Feature Branch**: `021-product-wiki`  
**Created**: 2026-04-05  
**Status**: Ready for planning  
**Input**: User description: "documentação de produto em /docs/ com controle de seções por perfil — seções de uso geral para todos os usuários e seções administrativas visíveis somente para administradores"

---

## Overview

A single documentation area at `/docs/` serving all authenticated users. The sidebar and home page adapt based on the user's profile:

- **Regular users** see 7 sections covering product usage: Getting Started, Incidents, Postmortems, Analytics, Semgrep Integration, API Keys, Rules.
- **Admin users** see all 7 user sections plus 3 additional admin-only sections: Administration, Security, API Reference.

Admin-only section pages at `/docs/administration/`, `/docs/security/`, and `/docs/api-reference/` redirect non-admin users to `/docs/` if accessed directly. No separate URL prefix or second Navbar link.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Developer finds integration instructions (Priority: P1)

A developer on a new team needs to integrate The Loop's scanner into their CI pipeline. They navigate to `/docs/`, identify themselves as a Developer, and are directed to the Semgrep integration guide. They follow step-by-step instructions to configure their GitHub Actions workflow, generate an API key, and verify their first scan.

**Why this priority**: The scanner integration workflow (Semgrep + API keys) is the primary onboarding path for technical users and the main driver of platform value.

**Independent Test**: A developer unfamiliar with The Loop can navigate to `/docs/`, select the Developer role, and successfully configure a working CI scan without asking for help.

**Acceptance Scenarios**:

1. **Given** a developer visits `/docs/`, **When** they select the Developer persona, **Then** the Semgrep, API Keys, and Rules sections are visually highlighted as their primary path.
2. **Given** a developer on the Semgrep page, **When** they follow the GitHub Actions snippet, **Then** the snippet is complete, copy-able, and produces a working scan.
3. **Given** a developer on the API Keys page, **When** they follow the creation steps, **Then** they understand the key format, scope, and how to use it in CI headers.

---

### User Story 2 — IT Manager understands analytics value (Priority: P2)

An IT Manager needs to present incident prevention metrics to leadership. They navigate to `/docs/analytics/`, learn what each of the 8 KPI cards means, and understand how to apply filters.

**Why this priority**: Analytics is the primary retention driver for non-technical stakeholders.

**Independent Test**: An IT Manager can open `/docs/analytics/` and answer "what does the MTTR card mean and how do I filter it by team?" without clicking anywhere else.

**Acceptance Scenarios**:

1. **Given** a manager on `/docs/analytics/`, **When** they read the KPI cards section, **Then** all 8 cards are explained in plain language with no technical jargon.
2. **Given** a manager on the home page, **When** they select IT Manager persona, **Then** Getting Started and Analytics sections are highlighted.

---

### User Story 3 — Operator manages incident lifecycle (Priority: P2)

An on-call operator needs to understand incident fields, status transitions, and the postmortem workflow. They navigate to `/docs/incidents/`.

**Why this priority**: Operators are the most frequent users. Unclear incident fields cause data quality issues.

**Independent Test**: An operator can open `/docs/incidents/` and answer "what fields are required to close an incident?" in under 2 minutes.

**Acceptance Scenarios**:

1. **Given** an operator on `/docs/incidents/`, **When** they look for closing requirements, **Then** they find a clear list of required fields before an incident can be closed.
2. **Given** an operator who completed an incident, **When** they navigate to `/docs/postmortems/`, **Then** they understand which template to choose and the consequences of locking a postmortem.

---

### User Story 4 — New user self-onboards (Priority: P1)

A user with a new account needs to understand what to do first. They navigate to `/docs/getting-started/`.

**Why this priority**: First-time user success is the most important metric for adoption.

**Independent Test**: A brand-new user can follow `/docs/getting-started/` top-to-bottom and end up with their first incident created and their team invited.

**Acceptance Scenarios**:

1. **Given** a new user on `/docs/getting-started/`, **When** they read the page sequentially, **Then** they are guided through: account setup → first incident → navigate dashboard → invite team.
2. **Given** any authenticated user anywhere in the app, **When** they click "Docs" in the navigation bar, **Then** they reach `/docs/` in one click.

---

### User Story 5 — Administrator accesses platform config docs (Priority: P2)

A platform administrator navigates to `/docs/` and sees additional sections not visible to regular users: Administration, Security, and API Reference. They access `/docs/administration/` to understand user management and rate limits.

**Why this priority**: Admins have unique operational needs that regular users don't need and shouldn't be distracted by. Profile-based visibility keeps the docs clean for everyone.

**Independent Test**: An admin user opens `/docs/` and sees the Administration, Security, and API Reference sections in the sidebar and home index. A regular user opens `/docs/` and does not see those sections.

**Acceptance Scenarios**:

1. **Given** an admin user views `/docs/`, **When** auth resolves client-side, **Then** the 3 admin section cards appear in the home index and sidebar without animation or loading state (silent addition after initial 7-card SSR render).
2. **Given** a regular user views `/docs/`, **When** the page loads and auth resolves, **Then** the sidebar and home index show only the 7 user sections — no admin sections ever appear.
3. **Given** a regular user navigates directly to `/docs/administration/`, **When** the page loads, **Then** they are redirected to `/docs/` with no admin content rendered.
4. **Given** an admin user views `/docs/administration/`, **When** the page loads, **Then** the full Administration content is rendered.

---

### Edge Cases

- What happens when a regular user navigates directly to `/docs/administration/`, `/docs/security/`, or `/docs/api-reference/`? They must be redirected to `/docs/` with no admin content partially rendered.
- What happens when an **unauthenticated** user navigates directly to an admin section URL? They must be redirected to `/login/` — not to `/docs/`, since they have no product context yet.
- What happens when a user navigates directly to a user-facing doc URL (e.g., `/docs/semgrep/`) without going through the home persona picker? The page must be fully useful standalone.
- What happens on mobile-width viewports? The sidebar must collapse or stack gracefully; content must remain readable.
- What if a doc section references a platform feature not yet released? Content must reflect only what is live in the current production version.
- What happens when an admin loses their admin role while browsing an admin section? The next page navigation to that section must result in a redirect to `/docs/`.

---

## Requirements *(mandatory)*

### Functional Requirements

**Shared docs area (`/docs/`)**

- **FR-001**: The platform MUST provide a single documentation area at `/docs/` covering all sections for all authenticated user profiles.
- **FR-002**: The docs home page MUST present a persona picker for 6 roles: Developer, IT Manager, Operator, Support, QA, Security.
- **FR-003**: Each docs section MUST be independently accessible via a unique, linkable URL under `/docs/`.
- **FR-004**: All user-facing docs pages MUST be accessible without requiring authentication (no login gate on `/docs/*` URLs for the 7 user sections).
- **FR-005**: The authenticated Navbar MUST include a single "Docs" link visible to all logged-in users. The link MUST NOT appear on the public landing page or any unauthenticated route.

**User sections (visible to all)**

- **FR-006**: The following 7 sections MUST be visible and accessible to all users: Getting Started, Incidents, Postmortems, Analytics, Semgrep Integration, API Keys, Rules.

**Admin-only sections (visible and accessible only to admin users)**

- **FR-007**: The following 3 sections MUST be visible and accessible only to users with the admin role: Administration, Security, API Reference.
- **FR-008**: Admin-only sections MUST NOT appear in the sidebar or home index for regular (non-admin) users — they are completely hidden, not locked or greyed out.
- **FR-009**: Any attempt by a non-admin user to access an admin-only section URL directly MUST result in a redirect to `/docs/` — no admin content may be partially rendered or exposed.
- **FR-010**: The admin role is determined using the existing platform admin flag — no new authentication system is required.

**All sections**

- **FR-011**: Every docs page MUST include a page title and description suitable for use in search results and link previews.
- **FR-012**: Every docs page MUST include persistent sidebar navigation showing all sections the current user is allowed to see, with an active section indicator.
- **FR-013**: Every docs page that includes a technical workflow MUST include a copy-able code or configuration example.
- **FR-014**: All docs content MUST reflect the current production state of the platform — no references to unreleased features.
- **FR-015**: All docs pages MUST be visually consistent with the rest of the platform (same design language, fonts, colors).

### Key Entities

- **DocSection**: A named documentation topic with a stable URL, prose content, and optional code examples. Has a `visibility` attribute: `all` (shown to everyone) or `admin` (shown only to admin users).
- **Persona**: A named user role (Developer, IT Manager, Operator, Support, QA, Security) with an associated set of primary doc sections. Used only for visual filtering on the home page.
- **CodeExample**: A copy-able block of code or configuration with an optional language label, embedded within a DocSection.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user unfamiliar with The Loop can navigate from the docs home to the answer for a role-specific question in under 2 minutes.
- **SC-002**: All docs sections relevant to a user's profile are reachable within 2 clicks from anywhere in the authenticated platform.
- **SC-003**: Every docs page meets WCAG 2.1 AA: keyboard-navigable, screen-reader-compatible section headings, and minimum 4.5:1 color contrast ratio for body text.
- **SC-004**: All docs pages load in under 1 second on a standard connection (no blocking API calls at page render time).
- **SC-005**: After the docs launch, the frequency of support questions about documented topics decreases — measured informally by qualitative before/after comparison. No automated page-view tracking required for v1.
- **SC-006**: 100% of copy-able code examples in the docs produce a working result when followed exactly as written.
- **SC-007**: Zero admin-only content is visible or accessible to non-admin users — verified by loading all admin section URLs while authenticated as a regular user.

---

## Clarifications

### Session 2026-04-05

- Q: Should the "Docs" Navbar link be visible to unauthenticated visitors (landing page)? → A: No — the link appears only in the authenticated area. User-facing `/docs/*` URLs remain publicly accessible but are not linked from the public Navbar.
- Q: What WCAG accessibility level must docs pages meet? → A: WCAG 2.1 AA.
- Q: Should doc page views be tracked to measure SC-005? → A: No tracking for v1 — SC-005 measured informally via qualitative before/after comparison.
- Q: Should there be a separate admin docs area at a different URL? → A: No — single `/docs/` area. Admin-only sections are hidden from regular users. No separate URL prefix, no second Navbar link.
- Q: What should the home page show while admin status resolves client-side? → A: Show 7 user section cards initially (SSR). Admin section cards appear silently after auth resolves — no skeleton, no loading state, no animation.
- Q: Where should an unauthenticated user be redirected when accessing an admin section URL directly? → A: Redirect to `/login/` (not `/docs/`) — user has no product context without authentication.

---

## Assumptions

- All docs content will be written in English, consistent with the rest of the platform.
- The docs cover only features that are live in the current production environment.
- No search functionality is required for v1.
- Mobile responsiveness is required (sidebar must adapt to small viewports).
- The docs do not require versioning (no multi-version support).
- All docs content is maintained manually alongside code changes (Mandamento XII).
- The persona picker is a visual navigation aid only — it does not persist the user's selected role across pages or sessions.
- Admin role is determined by the existing platform admin flag — no new backend role system is required.
- Currently 1 admin user exists. Any user with the admin flag automatically gains access to admin-only sections.
- Admin-only sections are completely hidden from non-admin users (not locked or visible with a restriction message).
- No new external services, databases, or infrastructure are required.
