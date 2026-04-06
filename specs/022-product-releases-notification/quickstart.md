# Quickstart: Product Releases Notification

**Feature**: Bell icon notifications for GitHub releases  
**Branch**: `feat/022-product-releases-notification`  
**Status**: Ready for testing

## User Flows

### Flow 1: See Unread Badge
1. Log in to The Loop
2. Look at Navbar → Bell icon shows badge with unread count
3. Badge updates every 120 seconds (or on page refresh)

### Flow 2: Open Dropdown & Mark as Read
1. Click bell icon
2. Dropdown opens showing recent releases (unread first)
3. Click "Mark read" button on a release
4. Visual indicator (dot) disappears; count decreases
5. Click outside dropdown to close

### Flow 3: View Full Release Details
1. Click on a release in the dropdown
2. Side panel slides in from right
3. Release automatically marked as read
4. View full changelog, breaking changes, doc link
5. Press Escape or click X to close

### Flow 4: View All Releases
1. In dropdown, click "View All Releases →"
2. Navigate to `/releases/` page
3. See all releases with full details
4. (Requires authentication)

## API Endpoints

### User Endpoints (Authenticated)

**Get releases with read status**
```bash
GET /api/v1/releases
Authorization: Bearer <firebase-token>
# Response:
{
  "items": [
    {
      "release": { "id", "title", "version", "published_date", "summary", ... },
      "is_read": false,
      "read_at": null
    }
  ],
  "total": 10
}
```

**Get unread count**
```bash
GET /api/v1/releases/unread-count
Authorization: Bearer <firebase-token>
# Response: { "unread_count": 3 }
```

**Mark release as read**
```bash
PATCH /api/v1/releases/{release_id}/status
Authorization: Bearer <firebase-token>
# Response:
{
  "id": "uuid",
  "release_id": "uuid",
  "user_id": "uuid",
  "is_read": true,
  "read_at": "2026-04-06T12:00:00Z"
}
```

**Get release detail**
```bash
GET /api/v1/releases/{release_id}
Authorization: Bearer <firebase-token>
# Response: { Release model }
```

### Admin Endpoints

**Sync releases from GitHub**
```bash
POST /api/v1/admin/releases/sync
Authorization: Bearer <firebase-admin-token>
# Response: { "status": "success", "synced_count": 5, "message": "..." }
```

## Testing Scenarios

### Backend (pytest)

```bash
cd apps/api
pytest tests/unit/domain/test_release_notification_service.py -v
pytest tests/api/test_releases_routes.py -v
pytest tests/integration/test_releases_e2e.py -v
```

### Frontend (vitest)

```bash
cd apps/web
npm run test -- tests/unit/components/test_bell_icon.svelte.test.ts -v
npm run test -- tests/unit/components/test_releases_dropdown.svelte.test.ts -v
```

### Manual Testing

1. **Badge visibility**:
   - Log in with test account
   - Verify badge appears with correct count
   - Refresh page → badge persists
   - Mark all releases as read → badge disappears

2. **Dropdown sorting**:
   - Open dropdown
   - Unread releases appear first
   - Releases within each group sorted by date (newest first)

3. **Detail panel**:
   - Click release in dropdown → panel opens from right
   - Release auto-marked as read (badge/count update)
   - Escape key closes panel
   - Click outside (overlay) closes panel

4. **Polling**:
   - Keep page open
   - Wait 120 seconds
   - If new release published, badge updates automatically

## Configuration

### Environment Variables (Backend)

```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxx  # GitHub API token (read public_repo)
DATABASE_URL=postgresql://user:pass@host/db  # Existing
```

### Frontend

- `PUBLIC_API_BASE_URL` — Used in releases service (already set)
- `PUBLIC_FIREBASE_*` — Auth (already set)

## Deployment

1. **Apply database migration**:
   ```bash
   cd apps/api
   alembic upgrade head  # Applies 023_add_release_tables.py
   ```

2. **Set environment variables** in GCP Cloud Run:
   - Add `GITHUB_TOKEN` secret reference to API service

3. **Deploy**:
   - Merge PR to `main`
   - GitHub Actions CI/CD deploys automatically to Cloud Run

4. **Verify**:
   ```bash
   curl https://api.loop.oute.pro/api/v1/releases/unread-count \
     -H "Authorization: Bearer <token>"
   ```

## Known Limitations (v1)

- No real-time updates (polling only, 120s interval)
- No email/Slack notifications
- No user preferences (all authenticated users see badge)
- No release scheduling/drafts (GitHub releases only)
- No offline mode

## Future Enhancements (v2+)

- WebSocket support for real-time updates
- Email digest notifications
- Per-user notification preferences
- Manual release creation in UI
- Release categories/tags
- Search and filtering
