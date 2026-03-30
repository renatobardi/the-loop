# The Loop

**Eliminate production incidents before they happen.**

The Loop closes the gap between post-mortems and code by transforming incident knowledge into active guardrails in your CI/CD pipeline.

## Architecture

```
apps/
└── web/          # SvelteKit landing page (adapter-node)
    ├── src/
    │   ├── routes/        # Route-based i18n (/en/, /pt/, /es/)
    │   ├── lib/ui/        # Design system (tokens + components)
    │   ├── lib/components/ # Page sections
    │   └── lib/server/    # Firebase, waitlist, rate limiter
    ├── messages/          # Paraglide i18n translations
    └── Dockerfile         # Multi-stage, non-root (Cloud Run)
```

## Tech Stack

- **Framework**: SvelteKit with adapter-node
- **Styling**: Tailwind CSS 4
- **i18n**: Paraglide-SvelteKit (EN, PT-BR, ES)
- **Waitlist**: Firebase Firestore (project: theloopoute)
- **Deployment**: GCP Cloud Run via GitHub Actions
- **CI/CD**: ESLint, TypeScript strict, vitest, Trivy, docs-check

## Development

```bash
cd apps/web
npm install
npm run dev
```

Open http://localhost:5173/en/

## Quality Checks

```bash
npm run lint       # ESLint + Prettier
npm run check      # TypeScript + svelte-check
npm run test       # vitest
npm run build      # Production build
```

## Deployment

Automatic on merge to `main` via GitHub Actions:
1. CI gates (lint, type-check, test, build, vulnerability scan, docs-check)
2. Docker build → Artifact Registry
3. Cloud Run deploy

## Constitution

This project is governed by 12 mandamentos defined in [CONSTITUTION.md](./CONSTITUTION.md). All contributions must comply.

## Links

- **Landing page**: https://loop.oute.pro
- **Contact**: loop@oute.pro
