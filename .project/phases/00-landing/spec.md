# Feature Specification: The Loop — Landing Page & Waitlist

**Feature Branch**: `001-landing-page-waitlist`
**Created**: 2026-03-30
**Status**: Draft
**Phase**: 00-landing
**Constitution**: CONSTITUTION.md — 12 mandamentos

## Problem Statement

Production incidents repeat because post-mortem knowledge lives in documents that nobody consults at the moment of writing code. Engineering teams invest significant effort in incident analysis and root-cause documentation, but this knowledge fails to reach developers in their workflow — at the pull request, at the commit, at the IDE. The result is preventable incidents recurring across organizations, costing downtime, revenue, and trust.

The Loop closes this gap by transforming post-mortems into active code guardrails. But before building the product, we need to validate demand and communicate the vision clearly to our target audience: software developers and engineering managers.

**Who experiences this**: Every software team that has experienced the same category of incident more than once. This is nearly universal in teams with 10+ engineers.

**Cost of not solving it**: The Loop cannot acquire its first users without a public presence. Without a landing page, there is no way to communicate the product vision, collect early interest, or validate positioning before investing in product development.

## Goals

1. **Communicate the product vision clearly in under 60 seconds of reading** — a visitor should understand what The Loop does, who it's for, and why it matters without scrolling past the hero section.
2. **Collect 200+ waitlist signups in the first 30 days** — validated early demand from developers and engineering managers. This is the success threshold; 500+ is the stretch target.
3. **Establish premium brand identity from day one** — dark mode, bold typography, electric blue accent, and polished interactions that signal "serious developer tool", not "side project".
4. **Ship production-ready infrastructure** — Cloud Run, CI/CD with all 12 constitutional mandates enforced, Firebase Firestore for waitlist. This infrastructure is the foundation for all future phases.
5. **Support 3 languages (EN, PT-BR, ES) from launch** — reach the global developer market with localized copy via route-based i18n.

## Non-Goals

1. **No product functionality** — no scanning, no rules, no API, no knowledge base. This phase is exclusively the public-facing landing page and waitlist collection. Product development starts in Phase 1.
2. **No user authentication** — no login, no signup, no dashboard. The only user action is submitting an email to the waitlist.
3. **No payment processing** — pricing is communicated on the landing page but no billing integration exists. Enterprise "Contact us" links to email.
4. **No blog or content marketing** — the landing page is a single-page experience. Blog, docs site, and changelog come in later phases.
5. **No analytics beyond waitlist count** — we will track signups in Firestore. Advanced analytics (funnel, attribution, heatmaps) are deferred to avoid scope creep.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Understand The Loop's Value Proposition (Priority: P1)

As a developer who has experienced recurring production incidents, I want to understand what The Loop does in under 60 seconds so that I can decide if it's relevant to my team.

**Why this priority**: Without clear communication of the product vision, no other feature matters. The hero section is the first thing every visitor sees and determines whether they stay or leave.

**Independent Test**: Can be tested by having a developer visit the landing page and asking them to describe what The Loop does after reading the hero section. If they can articulate it in their own words, the test passes.

**Acceptance Scenarios**:

1. **Given** a developer lands on loop.oute.pro, **When** they read the hero section, **Then** they understand: (1) The Loop prevents recurring incidents, (2) it works in their existing CI/CD pipeline, (3) it's based on real post-mortem knowledge.
2. **Given** a developer on a mobile device, **When** they visit the page, **Then** the hero section is fully readable without horizontal scrolling.

---

### User Story 2 - Join the Waitlist (Priority: P1)

As a developer, I want to join the waitlist with my email so that I get notified when The Loop launches.

**Why this priority**: Waitlist collection is the primary conversion goal of the landing page. Without this, the page has no mechanism to capture demand.

**Independent Test**: Can be tested by submitting a valid email and verifying it appears in the waitlist data store. Delivers value immediately as a lead capture mechanism.

**Acceptance Scenarios**:

1. **Given** a developer on the landing page, **When** they enter a valid email and submit the waitlist form, **Then** they see a confirmation message and the email is stored with timestamp and locale.
2. **Given** a developer who enters an invalid email, **When** they submit, **Then** they see a clear validation error without page reload.
3. **Given** a developer who submits an email that already exists in the waitlist, **When** they submit, **Then** they see a friendly message ("You're already on the list!") — no duplicate entry created.
4. **Given** a developer using the form, **When** they submit, **Then** the form is protected by rate limiting (max 5 submissions per IP per minute).

---

### User Story 3 - Explore Detection Layers (Priority: P2)

As a developer, I want to see how the 3 detection layers work so that I can assess the technical depth of the product.

**Why this priority**: Technical depth builds trust with developer audience. This section differentiates The Loop from generic monitoring tools and demonstrates the product has substance.

**Independent Test**: Can be tested by having a developer scan the 3 Layers section and asking them to describe what each layer does. If they can distinguish between blocking, consultive, and progressive behaviors, the test passes.

**Acceptance Scenarios**:

1. **Given** a developer scrolling past the hero, **When** they reach the "3 Layers" section, **Then** each layer (Static Rules, RAG Advisory, Auto Synthesis) is explained with a clear visual distinction between blocking, consultive, and progressive behaviors.
2. **Given** a developer who only reads headlines, **When** they scan the section headers, **Then** they get the gist of each layer without reading body text.

---

### User Story 4 - Read in Preferred Language (Priority: P2)

As a developer, I want to read the page in my preferred language (English, Portuguese, or Spanish) so that I fully understand the product.

**Why this priority**: i18n is important for reaching the global developer market but is not blocking for the core conversion funnel. English-only is viable as MVP.

**Independent Test**: Can be tested by navigating to /pt/ and verifying all visible text is in Portuguese, then sharing the URL and confirming it loads directly in Portuguese.

**Acceptance Scenarios**:

1. **Given** a developer visiting loop.oute.pro, **When** the page loads, **Then** it defaults to English (/en/).
2. **Given** a developer, **When** they select PT-BR or ES from the language selector, **Then** the URL changes to /pt/ or /es/ and all content is displayed in the selected language.
3. **Given** a developer sharing the URL /pt/, **When** another person opens the link, **Then** the page loads directly in Portuguese.

---

### User Story 5 - Evaluate Pricing (Priority: P3)

As an engineering manager, I want to understand the pricing model so that I can evaluate whether The Loop fits my team's budget.

**Why this priority**: Pricing information helps managers qualify the product but is not required for waitlist conversion. It adds credibility and sets expectations.

**Independent Test**: Can be tested by having a manager read the pricing section and asking them to describe the pricing model. They should be able to articulate: free tier, pay-as-you-go, and enterprise options.

**Acceptance Scenarios**:

1. **Given** a manager reading the pricing section, **When** they see the pricing cards, **Then** they understand: (1) Free tier = 100 scans/month, (2) Pay-as-you-go by scan batches above the free tier, (3) Enterprise = custom pricing with "Contact us".
2. **Given** a manager, **When** they click "Contact us" on the Enterprise card, **Then** they are directed to an email to initiate a conversation.

---

### User Story 6 - View Integrations (Priority: P3)

As an engineering manager, I want to see which platforms The Loop integrates with so that I know it works with our existing stack.

**Why this priority**: Integration information helps managers assess fit but is not critical for initial interest capture.

**Independent Test**: Can be tested by having a manager identify the supported platforms from the integrations section.

**Acceptance Scenarios**:

1. **Given** a manager reading the integrations section, **When** they see the integration list, **Then** they understand The Loop works with: GitHub (App), IDEs via MCP (Cursor, VS Code, Windsurf), and GitLab/Bitbucket/Jenkins via REST API.
2. **Given** each integration, **When** displayed, **Then** it shows a recognizable icon/logo and a one-line description of the integration type.

---

### User Story 7 - Fast and Premium Experience (Priority: P2)

As any visitor, I want the page to load fast and look premium so that I trust this is a serious product.

**Why this priority**: Performance and visual quality directly impact credibility and conversion. A slow or amateurish page undermines trust immediately.

**Independent Test**: Can be tested by running a Lighthouse audit and checking that LCP is under 2.5 seconds. Visual quality can be verified by comparing against the design system tokens.

**Acceptance Scenarios**:

1. **Given** a visitor on a standard connection, **When** the page loads, **Then** Largest Contentful Paint (LCP) is under 2.5 seconds.
2. **Given** a visitor, **When** they scroll, **Then** animations are smooth (60fps) and elements appear with subtle fade/slide transitions.
3. **Given** a visitor on mobile, **When** they view the page, **Then** the layout is fully responsive with no broken elements.

---

### Edge Cases

- What happens when a user submits the waitlist form with JavaScript disabled? The form MUST work via server-side action (progressive enhancement).
- What happens when the Firestore service is temporarily unavailable? The user MUST see a friendly error message ("Something went wrong. Please try again.") — no raw error displayed.
- What happens when a user accesses an unsupported locale (e.g., /fr/)? The system MUST redirect to /en/ (default).
- What happens when the rate limit is exceeded? The user MUST see a clear message ("Too many attempts. Please try again in a minute.") — no form submission processed.
- What happens when the page is shared without a locale prefix (e.g., loop.oute.pro)? Root `/` MUST redirect to `/en/`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a landing page with 8 sections in this order: Hero, Problem, 3 Layers, How It Works, Integrations, Pricing, Waitlist CTA, Footer.
- **FR-002**: System MUST render with a dark mode first design using electric blue accent color, bold oversized typography, and generous whitespace.
- **FR-003**: Hero section MUST display a headline, sub-headline, and waitlist email input + submit button visible without scrolling.
- **FR-004**: Waitlist form MUST collect email (required) and locale (auto-detected from route), validate on both client and server side, detect duplicates with a friendly message, and enforce rate limiting (max 5 submissions per IP per minute).
- **FR-005**: System MUST store waitlist entries with fields: email, locale, created_at, source ("landing").
- **FR-006**: System MUST support route-based i18n with routes /en/, /pt/, /es/ and root / redirecting to /en/.
- **FR-007**: All visible text MUST be localized — no hardcoded strings. Meta tags (title, description, og:) MUST be localized per language.
- **FR-008**: System MUST include hreflang tags for SEO.
- **FR-009**: Landing page MUST be responsive: mobile (375px+), tablet (768px+), desktop (1280px+).
- **FR-010**: System MUST serve security headers: CSP, X-Content-Type-Options: nosniff, X-Frame-Options: DENY, Referrer-Policy: strict-origin-when-cross-origin, HSTS with max-age of at least 1 year.
- **FR-011**: System MUST enforce HTTPS only with no wildcard CORS.
- **FR-012**: Design tokens (colors, typography, spacing, border-radius, shadows) MUST be defined in a centralized location and all components MUST use only these tokens.
- **FR-013**: Base components MUST include: Button (primary, secondary, ghost), Input (text, email), Card, Badge, Container, Section.
- **FR-014**: CI/CD pipeline MUST enforce all gates: lint, type-check, test, build, vulnerability scan, docs-check. All gates MUST pass before merge is allowed.
- **FR-015**: Deploy to production MUST be triggered automatically on merge to main.
- **FR-016**: System MUST include CODEOWNERS file with `* @renatobardi`.
- **FR-017**: README.md at repo root MUST include project description, setup instructions, architecture overview, and link to Constitution.
- **FR-018**: CONSTITUTION.md MUST exist at repo root.
- **FR-019**: .project/phases/00-landing/ MUST contain spec, plan, and tasks for this phase.

### Key Entities

- **WaitlistEntry**: Represents a single waitlist signup. Attributes: email (unique identifier), locale (language at time of signup), created_at (timestamp), source (origin of signup — "landing" for this phase).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 200+ waitlist signups collected within 30 days of launch (stretch: 500+).
- **SC-002**: Page loads with Largest Contentful Paint under 2.5 seconds on standard connections (stretch: under 1.5 seconds).
- **SC-003**: 100% of CI pipeline gates pass on the first PR merged to main.
- **SC-004**: All 12 constitutional mandates are verifiably enforced via manual audit.
- **SC-005**: Waitlist growth rate of 30+ signups per week sustained (stretch: 50/week).
- **SC-006**: 2+ enterprise "Contact us" email inquiries within 90 days (stretch: 5+).
- **SC-007**: Visitors can understand the product value proposition within 60 seconds of reading the hero section (qualitative — tested via user feedback).

## Assumptions

- Firebase project already exists: ID `theloopoute`, number `1090621437043`, org `renatobardicabral-org`.
- DNS records for loop.oute.pro and theloop.oute.pro are managed externally and will be pointed to Cloud Run's provided URL.
- The waitlist does not require email verification (no confirmation email in Phase 0).
- Pricing details (exact batch sizes and prices for pay-as-you-go) will be finalized before product launch, not before landing page launch. The landing page can show the model without exact numbers.
- The repo github.com/renatobardi/the-loop already exists and is public.
- Visitors have standard internet connectivity (no offline support needed for Phase 0).
- "by Oute" branding is subtle but present on the hero section.

## Open Questions (Resolved)

| # | Question | Resolution |
|---|----------|------------|
| OQ-001 | Accent color | `#0066FF` — azul puro, vibrante, high-contrast |
| OQ-002 | Font | Geist (by Vercel) — angular/tech, premium |
| OQ-003 | Enterprise contact email | `loop@oute.pro` |
| OQ-004 | Pay-as-you-go pricing details | Genérico por enquanto — landing mostra "Pay per scan batch" sem valores exatos |
| OQ-005 | Firebase project | Já existe — project ID: `theloopoute`, project number: `1090621437043`, org: `renatobardicabral-org` |

## Landing Page Content Structure

### Section 1: Hero

**EN Headline**: "Eliminate production incidents before they happen."
**EN Sub-headline**: "Close the loop between post-mortems and code. The Loop transforms incident knowledge into active guardrails in your CI/CD pipeline."
**EN CTA**: "Join the waitlist" + email input

**PT-BR Headline**: "Elimine incidentes de produção antes que aconteçam."
**PT-BR Sub-headline**: "Feche o ciclo entre post-mortems e código. The Loop transforma conhecimento de incidentes em guardrails ativos no seu pipeline de CI/CD."
**PT-BR CTA**: "Entrar na waitlist" + email input

**ES Headline**: "Elimina incidentes de producción antes de que ocurran."
**ES Sub-headline**: "Cierra el ciclo entre post-mortems y código. The Loop transforma el conocimiento de incidentes en guardrails activos en tu pipeline de CI/CD."
**ES CTA**: "Unirse a la waitlist" + email input

### Section 2: The Problem

**EN Headline**: "Don't let history repeat itself in your code."
**EN Body**: "Your team writes detailed post-mortems after every incident. But that knowledge stays in Notion docs and Confluence pages — never reaching the developer at the moment they're about to introduce the same pattern that caused the last outage. The Loop changes that."

**PT-BR Headline**: "Não deixe a história se repetir no seu código."
**PT-BR Body**: "Sua equipe escreve post-mortems detalhados após cada incidente. Mas esse conhecimento fica em docs do Notion e páginas do Confluence — nunca chega ao desenvolvedor no momento em que ele está prestes a introduzir o mesmo padrão que causou a última queda. The Loop muda isso."

**ES Headline**: "No dejes que la historia se repita en tu código."
**ES Body**: "Tu equipo escribe post-mortems detallados después de cada incidente. Pero ese conocimiento queda en docs de Notion y páginas de Confluence — nunca llega al desarrollador en el momento en que está a punto de introducir el mismo patrón que causó la última caída. The Loop cambia eso."

### Section 3: Three Layers of Detection

**EN Headline**: "Three layers. Zero blind spots."

**Layer 1 — Static Rules (Blocking)**: "Deterministic Semgrep rules derived from real production incidents. Runs in pre-commit and CI. Every finding links to the original incident. No AI hallucinations — pure pattern matching."

**Layer 2 — RAG Advisory (Consultive)**: "AI-powered review that compares your pull request against a knowledge base of past incidents. Posts non-blocking comments with matched incidents, confidence scores, and remediation guidance."

**Layer 3 — Auto Synthesis (Progressive)**: "When the same pattern is flagged across multiple PRs, The Loop automatically generates a new static rule and opens a PR for human approval. The system learns and hardens over time."

**PT-BR Headline**: "Três camadas. Zero pontos cegos."

**Layer 1**: "Regras Semgrep determinísticas derivadas de incidentes reais de produção. Roda no pre-commit e CI. Cada finding é rastreável ao incidente original. Sem alucinações de IA — pattern matching puro."
**Layer 2**: "Revisão com IA que compara seu pull request com uma base de conhecimento de incidentes passados. Posta comentários não-bloqueantes com incidentes encontrados, score de confiança e orientação de remediação."
**Layer 3**: "Quando o mesmo padrão é flaggado em múltiplos PRs, The Loop gera automaticamente uma nova regra estática e abre um PR para aprovação humana. O sistema aprende e se fortalece com o tempo."

**ES Headline**: "Tres capas. Cero puntos ciegos."

**Layer 1**: "Reglas Semgrep determinísticas derivadas de incidentes reales de producción. Se ejecuta en pre-commit y CI. Cada hallazgo se vincula al incidente original. Sin alucinaciones de IA — pattern matching puro."
**Layer 2**: "Revisión con IA que compara tu pull request con una base de conocimiento de incidentes pasados. Publica comentarios no bloqueantes con incidentes encontrados, score de confianza y guía de remediación."
**Layer 3**: "Cuando el mismo patrón se detecta en múltiples PRs, The Loop genera automáticamente una nueva regla estática y abre un PR para aprobación humana. El sistema aprende y se fortalece con el tiempo."

### Section 4: How It Works

**EN Headline**: "The feedback loop that makes your code safer."
**EN Flow**: Incident → Knowledge Base → Rule / Advisory → Code Protected → Loop Closes
**EN Description**: "Every production incident becomes a guardrail. Post-mortems feed the knowledge base. The knowledge base generates rules and advisories. Rules block known anti-patterns. Advisories catch semantic similarities. And when new patterns emerge, they become new rules. The loop never stops."

**PT-BR Headline**: "O ciclo de feedback que torna seu código mais seguro."
**PT-BR Description**: "Cada incidente de produção se torna um guardrail. Post-mortems alimentam a base de conhecimento. A base gera regras e advisories. Regras bloqueiam anti-patterns conhecidos. Advisories capturam similaridades semânticas. E quando novos padrões emergem, se tornam novas regras. O ciclo nunca para."

**ES Headline**: "El ciclo de feedback que hace tu código más seguro."
**ES Description**: "Cada incidente de producción se convierte en un guardrail. Los post-mortems alimentan la base de conocimiento. La base genera reglas y advisories. Las reglas bloquean anti-patterns conocidos. Los advisories capturan similitudes semánticas. Y cuando emergen nuevos patrones, se convierten en nuevas reglas. El ciclo nunca se detiene."

### Section 5: Integrations

**EN Headline**: "Works where you work."

- GitHub — "GitHub App with Check Runs, SARIF reports, and PR review comments."
- IDEs (MCP) — "Cursor, VS Code, Windsurf — scan code and get advisories directly in your editor."
- GitLab / Bitbucket / Jenkins — "REST API with webhook support. SARIF and JSON output."

**PT-BR Headline**: "Funciona onde você trabalha."
**ES Headline**: "Funciona donde trabajas."

### Section 6: Pricing

**EN Headline**: "Start free. Pay as you grow."

| | Free | Pay-as-you-go | Enterprise |
|---|---|---|---|
| **Scans** | 100/month | Buy in batches | Unlimited |
| **Layers** | L1 + L2 + L3 | L1 + L2 + L3 | L1 + L2 + L3 |
| **Support** | Community | Email | Dedicated |
| **SSO/SAML** | — | — | Included |
| **Audit logs** | — | — | Included |
| **Price** | $0 | Pay per scan batch | Contact us |

**PT-BR Headline**: "Comece grátis. Pague conforme cresce."
**ES Headline**: "Empieza gratis. Paga mientras creces."

### Section 7: Waitlist CTA (repeated)

**EN Headline**: "Be the first to close the loop."
**EN Sub**: "Join the waitlist and get early access when we launch."

**PT-BR Headline**: "Seja o primeiro a fechar o ciclo."
**PT-BR Sub**: "Entre na waitlist e tenha acesso antecipado ao lançamento."

**ES Headline**: "Sé el primero en cerrar el ciclo."
**ES Sub**: "Únete a la waitlist y obtén acceso anticipado al lanzamiento."

### Section 8: Footer

- Logo: "The Loop" — by Oute
- Links: GitHub repo, Constitution (link to CONSTITUTION.md on GitHub), Contact (email)
- Legal: © 2026 Oute. All rights reserved.
- Language selector (alternative access point)

## Technical Decisions (Phase 0 specific)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | SvelteKit | SSR for SEO, adapter-node for Cloud Run |
| Styling | Tailwind CSS | Utility-first, pairs with design system tokens, no runtime CSS |
| Waitlist storage | Firebase Firestore | Zero backend needed for Phase 0, free tier covers volume |
| Deployment | GCP Cloud Run | min_instances=0 for cost optimization |
| CI/CD | GitHub Actions | Free unlimited minutes (public repo), enforces all gates |
| i18n | Route-based (/en/, /pt/, /es/) | Better for SEO, shareable URLs per language |
| Animations | CSS only | No external animation libraries, prefers-reduced-motion respected |
| Images/Assets | SVG + CSS gradients | 100% code-generated visuals, no external image files |

## Timeline Considerations

- **No hard deadline** — quality over speed. Each phase is validated before moving forward.
- **Dependency**: GCP project and Firebase must be configured before waitlist implementation.
- **Dependency**: Domain DNS records (loop.oute.pro, theloop.oute.pro) must point to Cloud Run before go-live.
- **Suggested phasing within Phase 0**:
  1. Monorepo scaffolding + CI/CD + constitutional mandates enforced
  2. Design system tokens + base components
  3. Landing page sections (Hero → Footer)
  4. i18n (EN → PT-BR → ES)
  5. Waitlist form + Firebase integration
  6. Cloud Run deployment + domain configuration
  7. Final review: Lighthouse audit, security headers, docs-check
