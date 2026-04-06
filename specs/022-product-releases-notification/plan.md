# Implementation Plan: Product Releases Notification

**Branch**: `022-product-releases-notification` | **Date**: 2026-04-06 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/022-product-releases-notification/spec.md`

## Summary

Add a bell icon notification system to the navbar that notifies authenticated users of new product releases via GitHub. Features include:
- **Badge indicator** on bell icon showing unread release count
- **Dropdown panel** with recent releases (unread first, up to ~10 total) + "View All Releases" link
- **Side panel detail view** of full changelog with auto-mark-as-read on open
- **120-second polling** for new releases from GitHub releases feed
- **Per-user read/unread status** persisted to database

**Technical Approach**: 
- Backend: Add Release + ReleaseNotificationStatus entities, GitHub API integration for release import, GET/PATCH endpoints for notifications
- Frontend: Bell icon component with Svelte 5 runes, dropdown + side panel UI, 120s polling service
- Database: Two new tables (releases, release_notification_status) with per-user read tracking
- No new infrastructure or background jobs required (polling is client-side + GitHub sync can be event-driven on publish)

## Technical Context

**Language/Version**: Python 3.12 (FastAPI backend), TypeScript 5+ / Svelte 5 (frontend)  
**Primary Dependencies**: 
- Backend: FastAPI, SQLAlchemy 2.0, Pydantic v2, requests (GitHub API)
- Frontend: SvelteKit 2, Svelte 5 runes, Tailwind CSS 4
- Existing: Firebase (auth), PostgreSQL 16 + pgvector

**Storage**: PostgreSQL 16 (new tables: Release, ReleaseNotificationStatus)  
**Testing**: pytest (backend unit + API), vitest (frontend unit)  
**Target Platform**: Web service (SPA + FastAPI)  
**Project Type**: Web application (monorepo: frontend + backend)  
**Performance Goals**: Dropdown opens <1s, detail panel opens <1s, notifications update within ~2 minutes (120s polling)  
**Constraints**: 
- Badge updates only on page load or every 120 seconds (polling frequency)
- No real-time WebSocket (polling acceptable for low-frequency release events)
- Sidebar panel responsive on mobile (touch-friendly)

**Scale/Scope**: 
- Typical 1–3 releases per week
- All authenticated users receive notifications (no opt-in filtering v1)
- GitHub releases feed used as single source of truth

## Constitution Check

**Mandamento XIII — Dependencias no Plano de Execucao**

✅ **PASS**: All dependencies identified and explicit in this plan:

| Category | Dependency | Status | Notes |
|----------|-----------|--------|-------|
| **Infra** | PostgreSQL 16 | Existing | No new provisioning; add 2 tables via Alembic migration |
| **Infra** | Cloud Run (API) | Existing | No new services; deploy to existing `theloop-api` |
| **Infra** | Cloud Run (Web) | Existing | No new services; deploy to existing `the-loop` |
| **Secrets** | GitHub API token | **TASK T053** | Add `GITHUB_TOKEN` to GCP Secret Manager before deploy; service account needs read access to github.com/renatobardi/the-loop (handled in Phase 7, T053) |
| **APIs** | GitHub Releases REST API | External | No auth required for public repos; rate limit: 60 req/hr unauthenticated, 5k req/hr with token |
| **CI/CD** | Existing workflows | Existing | No new jobs; standard lint/test/build gates apply |
| **Frontend** | Existing Navbar component | Existing | Bell icon added to navbar alongside existing nav items |
| **Backend** | Existing API routes | Existing | New endpoints: `GET /api/v1/releases`, `PATCH /api/v1/releases/{id}/status` |

**Other Mandamentos**: No violations detected.
- ✅ I (Trunk-Based): Branch `022-*` → feature branch → PR → merge to main
- ✅ II (Design System): Uses existing design tokens, Container component, no ad-hoc styling
- ✅ VII (CI Rigoroso): All new code subject to lint/test/type-check gates
- ✅ VIII (Seguranca): GitHub token stored in Secret Manager; CORS enforced on API; Firebase auth required for notifications
- ✅ XIII (Dependencies in Plan): **All dependencies listed above**

## Project Structure

### Documentation (this feature)

```text
specs/022-product-releases-notification/
├── spec.md              # ✅ Feature requirements (COMPLETE)
├── plan.md              # ✅ Implementation strategy (COMPLETE)
├── tasks.md             # ✅ Executable task list with 75 tasks (COMPLETE)
├── checklists/
│   └── requirements.md   # ✅ Specification quality checklist (COMPLETE)
├── research.md          # Skipped — no NEEDS CLARIFICATION markers (Phase 0)
├── data-model.md        # Skipped — entities defined in spec.md + plan.md (Phase 1)
├── quickstart.md        # Will generate during implementation (Phase 1)
└── contracts/           # Will generate during implementation (Phase 1)
    ├── release-api.md
    └── notification-status-api.md
```

### Source Code (existing monorepo structure)

```text
apps/api/
├── src/
│   ├── domain/
│   │   ├── models.py              # Add: Release, ReleaseNotificationStatus Pydantic models
│   │   ├── exceptions.py          # Add: ReleaseNotFoundError, etc.
│   │   └── services.py            # Add: ReleaseNotificationService class
│   ├── adapters/
│   │   ├── postgres/
│   │   │   ├── models.py          # Add: ReleaseRow, ReleaseNotificationStatusRow ORM models
│   │   │   ├── release_repository.py  # NEW: Repository for Release CRUD
│   │   │   └── notification_repository.py  # NEW: Repository for notification status
│   │   └── github/
│   │       └── releases_api.py    # NEW: GitHub Releases API client
│   ├── api/
│   │   ├── routes/
│   │   │   └── releases.py        # NEW: GET /api/v1/releases, PATCH endpoints
│   │   └── deps.py                # Update: Add get_release_service() dependency
│   └── main.py                    # Update: Add startup task for GitHub sync (optional)
│
└── tests/
    ├── unit/
    │   └── domain/
    │       └── test_release_notification.py  # NEW: Unit tests
    └── api/
        └── test_releases_routes.py           # NEW: Route tests

apps/web/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   └── releases/           # NEW: Release notification components
│   │   │       ├── BellIcon.svelte
│   │   │       ├── ReleasesDropdown.svelte
│   │   │       ├── ReleaseDetailPanel.svelte
│   │   │       └── ReleaseNotificationManager.svelte (container)
│   │   ├── services/
│   │   │   └── releases.ts         # NEW: API client for releases endpoints
│   │   └── stores/
│   │       └── releases.ts         # NEW: Svelte store for release notifications state
│   ├── routes/
│   │   └── releases/
│   │       ├── [version]/
│   │       │   └── +page.svelte   # NEW: Public releases archive page
│   │       └── +layout.svelte
│   └── lib/
│       └── components/
│           └── Navbar.svelte       # Update: Add BellIcon component
│
└── tests/
    └── unit/
        ├── lib/
        │   ├── test_releases_service.ts  # NEW: Service tests
        │   └── test_releases_store.ts    # NEW: Store tests
        └── components/
            └── test_release_components.ts # NEW: Component tests

alembic/
└── versions/
    └── 00nn_add_release_tables.py  # NEW: Database migration (Release + NotificationStatus)
```

**Structure Decision**: Existing monorepo structure (frontend + backend) is retained. New code follows established patterns:
- Backend: Domain → Ports → Adapters → API routes (hexagonal architecture)
- Frontend: Components → Services → Stores (Svelte 5 runes pattern)
- Database: Alembic migrations for schema changes
- Tests: Unit (domain/services) + API (routes) + Component (frontend)

## Complexity Tracking

**No Constitution violations requiring justification.** This feature:
- ✅ Uses existing infrastructure (PostgreSQL, Cloud Run, Firebase auth)
- ✅ Requires only one new external dependency (GitHub API token in Secret Manager)
- ✅ Follows existing architectural patterns (hexagonal backend, Svelte 5 frontend)
- ✅ No new services, databases, or CI/CD jobs needed
- ✅ All dependencies explicitly documented in Constitution Check table above
