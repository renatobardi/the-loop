# Quickstart: Landing Page & Waitlist

**Date**: 2026-03-30
**Feature**: 001-landing-page-waitlist

## Prerequisites

- Node.js 22 LTS
- npm
- Firebase project `theloopoute` access (for local Firestore writes)
- Service account JSON for local development

## Setup

```bash
# Clone and enter the project
git clone git@github.com:renatobardi/the-loop.git
cd the-loop/apps/web

# Install dependencies
npm install

# Configure local Firebase credentials
# Create .env.local (gitignored) with your service account JSON:
echo 'FIREBASE_SERVICE_ACCOUNT={"type":"service_account","project_id":"theloopoute",...}' > .env.local
```

## Development

```bash
# Start dev server
npm run dev

# Open in browser
open http://localhost:5173/en/
```

Available routes:
- `http://localhost:5173/` → redirects to `/en/`
- `http://localhost:5173/en/` — English
- `http://localhost:5173/pt/` — Portuguese
- `http://localhost:5173/es/` — Spanish

## Quality Checks

```bash
# Lint (ESLint + Prettier)
npm run lint

# Type check (TypeScript strict + svelte-check)
npm run check

# Unit tests
npm run test

# All checks (as CI runs them)
npm run lint && npm run check && npm run test && npm run build
```

## Build & Docker

```bash
# Production build
npm run build

# Run production build locally
node build/index.js

# Docker build
docker build -t the-loop .

# Docker run
docker run -p 3000:3000 \
  -e NODE_ENV=production \
  -e FIREBASE_SERVICE_ACCOUNT='...' \
  the-loop
```

## Waitlist Testing

1. Open `http://localhost:5173/en/`
2. Scroll to waitlist form (hero or bottom CTA)
3. Enter a valid email and submit
4. Verify confirmation message appears
5. Submit same email again — verify "already on the list" message
6. Submit 6 times rapidly — verify rate limit message on 6th attempt
7. Submit with invalid email — verify validation error

## Project Structure

```
apps/web/
├── src/
│   ├── routes/[lang]/     # Locale-parameterized pages
│   ├── lib/ui/            # Design system tokens + components
│   ├── lib/server/        # Firebase, waitlist, rate limiter, schemas
│   ├── lib/components/    # Page sections (Hero, Pricing, etc.)
│   └── lib/i18n/          # Paraglide translation messages
├── Dockerfile
├── svelte.config.js
└── tailwind.config.ts
```

## Deployment

Deployment is automatic on merge to `main` via GitHub Actions:
1. CI runs all quality gates (lint, type-check, test, build, vuln scan, docs-check)
2. Docker image is built and pushed to Artifact Registry
3. Cloud Run service is updated with new image
4. Custom domain loop.oute.pro serves the new version

No manual deployment steps required.
