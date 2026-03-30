# Research: Landing Page & Waitlist

**Date**: 2026-03-30
**Feature**: 001-landing-page-waitlist

## i18n Strategy

**Decision**: Paraglide-SvelteKit (by Inlang/Opral)

**Rationale**:
- Official `sv add paraglide` integration — endorsed by Svelte ecosystem
- Compiler-generated typed message functions (`m.hero_headline()`) — compile-time error on wrong keys
- `AsyncLocalStorage`-based SSR isolation — correct for Cloud Run concurrent requests
- Tree-shakable: only messages used on rendered pages are shipped
- `localizeHref()` helper simplifies language selector and internal links

**Alternatives considered**:
- Custom JSON + `[lang]` param: Zero dependencies, full control, but no type safety on keys and all plumbing is hand-written. Strong fallback if Paraglide adds unwanted complexity.
- `svelte-i18n`: Unmaintained (v3.7.0), SSR shared-store race condition on concurrent requests — rejected.
- `sveltekit-i18n`: Moderate maintenance, awkward middle ground between custom and Paraglide — rejected.

**Manual work still required** (regardless of approach):
- Root `/` redirect to `/en/` in `hooks.server.ts`
- Unsupported locale fallback (e.g., `/fr/` → `/en/`)
- hreflang loop in `+layout.svelte` (~5 lines)
- Localized `<title>`, `<meta>`, `<og:*>` tags in `<svelte:head>`
- Language selector component

## Firebase/Firestore Waitlist

**Decision**: Firebase Admin SDK (server-side only) + SvelteKit form actions

**Rationale**:
- Admin SDK bypasses Firestore Security Rules — server controls all writes
- `initializeApp()` with ADC on Cloud Run — zero config in production
- Local dev uses `FIREBASE_SERVICE_ACCOUNT` env var (JSON string)
- Singleton guard with `getApps().length` prevents re-init errors

**Key patterns**:
- Email as Firestore document ID — deduplication is a database invariant
- `FieldValue.serverTimestamp()` for `created_at` — consistent timestamps
- `docRef.get()` before `docRef.set()` for duplicate detection
- Cloud Run SA needs `roles/datastore.user` (minimal write role)

**Firestore Security Rules** (defense against direct client SDK access):
- `allow create` with field validation (email string, locale in [en/pt/es], source == "landing")
- `allow read: if false` — no client reads
- `allow update, delete: if false` — immutable from client

## Rate Limiting

**Decision**: `rate-limiter-flexible` with `RateLimiterMemory` (Phase 0)

**Rationale**:
- Zero infrastructure cost — in-memory, no Redis needed
- 5 requests per IP per 60 seconds
- Module-scope singleton persists across requests
- Limitation: not shared across Cloud Run instances — acceptable for Phase 0 traffic

**Scale path**: Migrate to Upstash Redis (`@upstash/ratelimit`) when multi-instance accuracy is needed.

## Email Validation

**Decision**: Zod with `.trim().toLowerCase().email().max(254)`

**Rationale**:
- `safeParse()` returns structured errors — no exceptions in form actions
- `.trim()` and `.toLowerCase()` are transforms that clean before validation
- Max 254 chars per RFC 5321

## Cloud Run Deployment

**Decision**: Global External Application Load Balancer + Serverless NEG

**Rationale**:
- Cloud Run domain mappings deprecated for new regions (mid-2024)
- LB provides: Google-managed SSL, HTTP→HTTPS redirect, static IP
- `--ingress=internal-and-cloud-load-balancing` prevents direct `*.run.app` access
- HSTS with preload (2yr max-age + includeSubDomains)

**DNS setup**: `loop.oute.pro` → A record → static IP from LB

## Workload Identity Federation (WIF)

**Decision**: OIDC provider scoped to `renatobardi/the-loop` repo

**Rationale**:
- Zero service account keys in repository
- `attribute-condition` restricts to exact repo — prevents fork abuse
- `google-github-actions/auth@v2` handles OIDC exchange
- Dedicated `github-deployer` service account with least-privilege roles

**Required roles for deployer SA**:
- `roles/run.admin` — deploy Cloud Run services
- `roles/artifactregistry.writer` — push Docker images

## Dockerfile

**Decision**: 3-stage build (deps → build → runner) with `node:22-alpine`

**Rationale**:
- Alpine keeps image under 200 MB
- Non-root user (UID 1001) per Constitution Mandamento VIII
- `--omit=dev` prunes dev dependencies before final stage
- `COPY --chown` avoids extra layer

## Security Headers

**Decision**: All headers set in `hooks.server.ts` handle hook

**Headers**:
- `Strict-Transport-Security`: 2yr, includeSubDomains, preload
- `X-Frame-Options`: DENY
- `X-Content-Type-Options`: nosniff
- `Referrer-Policy`: strict-origin-when-cross-origin
- `Permissions-Policy`: disable camera, microphone, geolocation, payment, usb
- `Content-Security-Policy`: self + googleapis.com for Firestore connect-src
- `frame-ancestors 'none'` in CSP (modern replacement for X-Frame-Options)

## SvelteKit Configuration

**Decision**: `adapter-node` with `precompress: false`, `csrf.checkOrigin: true`

**Rationale**:
- `precompress: false` — let Cloud Run LB handle compression
- `csrf.checkOrigin: true` — enforce same-origin on form actions (default, but explicit)
- `envPrefix: ''` — allow reading PORT without prefix

## IP Address Extraction

**Decision**: `event.getClientAddress()` with `ADDRESS_HEADER=x-forwarded-for`, `XFF_DEPTH=2`

**Rationale**:
- Cloud Run sits behind GCP LB — without config, `getClientAddress()` returns LB IP
- `XFF_DEPTH=2` accounts for GCP LB layer
