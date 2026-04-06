# Release API Contract

**Version**: 1.0  
**Base URL**: `https://api.loop.oute.pro/api/v1/releases`  
**Auth**: Firebase JWT (Bearer token)

## Endpoints

### GET /api/v1/releases
Fetch authenticated user's releases with read status.

**Request**:
```http
GET /api/v1/releases
Authorization: Bearer <firebase-jwt>
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "release": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "v1.1.0",
        "version": "1.1.0",
        "published_date": "2026-04-06T12:00:00+00:00",
        "summary": "Bug fixes and improvements",
        "changelog_html": "<h2>Fixes</h2><ul><li>Fixed issue #123</li></ul>",
        "breaking_changes_flag": false,
        "documentation_url": "https://github.com/renatobardi/the-loop/releases/tag/v1.1.0"
      },
      "is_read": false,
      "read_at": null
    }
  ],
  "total": 10
}
```

**Errors**:
- `401 Unauthorized` — Missing/invalid auth token
- `429 Too Many Requests` — Rate limited (60/minute)

---

### GET /api/v1/releases/unread-count
Get count of unread releases for user.

**Request**:
```http
GET /api/v1/releases/unread-count
Authorization: Bearer <firebase-jwt>
```

**Response** (200 OK):
```json
{
  "unread_count": 3
}
```

**Errors**:
- `401 Unauthorized`
- `429 Too Many Requests` (120/minute)

---

### GET /api/v1/releases/{release_id}
Get full details for a specific release.

**Request**:
```http
GET /api/v1/releases/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <firebase-jwt>
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "v1.1.0",
  "version": "1.1.0",
  "published_date": "2026-04-06T12:00:00+00:00",
  "summary": "Bug fixes and improvements",
  "changelog_html": "<h2>Fixes</h2><ul><li>Fixed issue #123</li></ul>",
  "breaking_changes_flag": false,
  "documentation_url": "https://github.com/renatobardi/the-loop/releases/tag/v1.1.0"
}
```

**Errors**:
- `401 Unauthorized`
- `404 Not Found` — Release ID doesn't exist
- `429 Too Many Requests`

---

### PATCH /api/v1/releases/{release_id}/status
Mark release as read for user.

**Request**:
```http
PATCH /api/v1/releases/550e8400-e29b-41d4-a716-446655440000/status
Authorization: Bearer <firebase-jwt>
Content-Type: application/json
```

**Response** (200 OK):
```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "release_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "is_read": true,
  "read_at": "2026-04-06T12:05:00+00:00"
}
```

**Errors**:
- `401 Unauthorized`
- `404 Not Found` — Release ID doesn't exist
- `429 Too Many Requests`

---

## Admin Endpoints

### POST /api/v1/admin/releases/sync
Admin: Manually sync releases from GitHub.

**Request**:
```http
POST /api/v1/admin/releases/sync
Authorization: Bearer <firebase-admin-jwt>
```

**Response** (200 OK):
```json
{
  "status": "success",
  "synced_count": 5,
  "message": "Synced 5 new releases from GitHub"
}
```

**Errors**:
- `401 Unauthorized` — Not authenticated
- `403 Forbidden` — User not admin
- `500 Internal Server Error` — GitHub API failed
- `429 Too Many Requests` (10/minute)

---

## Data Models

### Release
```typescript
{
  id: UUID;
  title: string;
  version: string;
  published_date: ISO8601DateTime;
  summary?: string;
  changelog_html?: string;
  breaking_changes_flag: boolean;
  documentation_url?: string;
}
```

### ReleaseNotificationStatus
```typescript
{
  id: UUID;
  release_id: UUID;
  user_id: UUID;
  is_read: boolean;
  read_at?: ISO8601DateTime;
}
```

## Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| GET /releases | 60 | 1 minute |
| GET /releases/unread-count | 120 | 1 minute |
| GET /releases/{id} | 60 | 1 minute |
| PATCH /releases/{id}/status | 60 | 1 minute |
| POST /admin/releases/sync | 10 | 1 minute |

## Error Responses

All error responses follow standard format:

```json
{
  "detail": "Error message"
}
```

### Status Codes
- `200` — Success
- `400` — Bad request
- `401` — Unauthorized
- `403` — Forbidden
- `404` — Not found
- `429` — Rate limited
- `500` — Server error
