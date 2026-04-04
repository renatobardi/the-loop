# Phase B API — Rules Versioning (Complete Reference)

**Base URL**: `https://api.loop.oute.pro/api/v1`  
**Version**: 0.2.0 (Phase B production-ready)  
**Rate Limits**: See per-endpoint documentation

---

## Endpoints

### GET /rules/latest

Fetch the latest **active** rule version with automatic caching.

**Parameters**: None  
**Rate Limit**: 60/minute  
**Cache**: 5 minutes (TTL, invalidated on publish/deprecate)  
**Auth**: Public (no authentication required)

**Response (200 OK)**:
```json
{
  "version": "0.2.0",
  "rules_count": 20,
  "created_at": "2026-04-03T22:30:00Z",
  "status": "active",
  "published_by": "550e8400-e29b-41d4-a716-446655440000",
  "notes": "Phase B: 14 new rules added (injection, crypto, security, performance)",
  "deprecated_at": null,
  "rules": [
    {
      "id": "injection-001-sql-string-concat",
      "languages": ["python", "javascript", "typescript", "java", "go", "ruby"],
      "message": "[The Loop] SQL injection via concatenação de string detectado...",
      "severity": "ERROR",
      "metadata": {
        "incident_id": "injection-001",
        "category": "injection",
        "loop_url": "https://loop.oute.pro/incidents/injection-001",
        "remediation": "Use parâmetros bindados..."
      },
      "patterns": [
        {
          "pattern": "$DB.execute(\"...\" + $INPUT)"
        }
      ]
    }
  ]
}
```

**Headers**:
```
Cache-Control: public, max-age=300
Content-Type: application/json
```

**Error Responses**:

| Status | Detail | Cause |
|--------|--------|-------|
| 503 | No active rule version found | No versions published yet, or all versions deprecated |
| 503 | Rules service temporarily unavailable: {error} | Unexpected DB/cache error |

**Example**:
```bash
curl -s https://api.loop.oute.pro/api/v1/rules/latest | jq .version
# Output: "0.2.0"
```

---

### GET /rules/{version}

Fetch a **specific rule version** by semantic version (any status: active, draft, or deprecated).

**Parameters**:

| Name | Type | Example | Required |
|------|------|---------|----------|
| `version` | path | `0.1.0` | Yes (semver X.Y.Z) |

**Rate Limit**: 60/minute  
**Cache**: None (no caching for specific lookups)  
**Auth**: Public

**Response (200 OK)**: Same structure as `/latest`

**Error Responses**:

| Status | Detail | Cause |
|--------|--------|-------|
| 404 | Version {version} not found | Version doesn't exist in database |

**Example**:
```bash
# Fetch v0.1.0
curl -s https://api.loop.oute.pro/api/v1/rules/0.1.0 | jq .status
# Output: "active"

# Fetch deprecated v0.1.0 (still returns 200)
curl -s https://api.loop.oute.pro/api/v1/rules/0.1.0 | jq .deprecated_at
# Output: "2026-04-05T10:00:00Z"
```

---

### GET /rules/versions

List **all rule versions** in reverse creation order (newest first). Includes all statuses: active, draft, deprecated.

**Parameters**: None  
**Rate Limit**: 60/minute  
**Cache**: None  
**Auth**: Public

**Response (200 OK)**:
```json
{
  "versions": [
    {
      "version": "0.2.0",
      "status": "active",
      "created_at": "2026-04-03T22:30:00Z",
      "rules_count": 20,
      "deprecated_at": null
    },
    {
      "version": "0.1.0",
      "status": "deprecated",
      "created_at": "2026-02-01T10:00:00Z",
      "rules_count": 6,
      "deprecated_at": "2026-04-05T10:00:00Z"
    }
  ]
}
```

**Error Responses**:

| Status | Detail | Cause |
|--------|--------|-------|
| 500 | Failed to list versions: {error} | Database connectivity issue |

**Example**:
```bash
curl -s https://api.loop.oute.pro/api/v1/rules/versions | jq '.versions | length'
# Output: 2
```

---

### GET /rules/deprecated

List **only deprecated rule versions** (useful for rollback decisions).

**Parameters**: None  
**Rate Limit**: 60/minute  
**Cache**: None  
**Auth**: Public

**Response (200 OK)**:
```json
{
  "versions": [
    {
      "version": "0.1.0",
      "status": "deprecated",
      "created_at": "2026-02-01T10:00:00Z",
      "rules_count": 6,
      "deprecated_at": "2026-04-05T10:00:00Z"
    }
  ]
}
```

**Error Responses**:

| Status | Detail | Cause |
|--------|--------|-------|
| 500 | Failed to list deprecated versions: {error} | Database error |

**Example**:
```bash
curl -s https://api.loop.oute.pro/api/v1/rules/deprecated | jq '.versions[0].version'
# Output: "0.1.0"
```

---

### POST /rules/publish

Publish a new rule version (admin only). Triggers cache invalidation.

**Parameters**: JSON body

| Field | Type | Example | Required | Validation |
|-------|------|---------|----------|-----------|
| `version` | string | `0.2.0` | Yes | Semver X.Y.Z, must be unique |
| `rules` | array | See below | Yes | Non-empty, each rule has id/languages/message/severity/patterns |
| `notes` | string | `"Phase B: 14 new rules"` | No | Release notes (markdown ok) |

**Rate Limit**: 10/minute  
**Auth**: Requires valid Firebase token with `is_admin=true` claim  
**Cache Effect**: Invalidates `/latest` cache immediately

**Request Body**:
```json
{
  "version": "0.2.0",
  "rules": [
    {
      "id": "injection-001",
      "languages": ["python", "javascript"],
      "message": "[The Loop] SQL injection detected",
      "severity": "ERROR",
      "metadata": {
        "incident_id": "injection-001",
        "category": "injection"
      },
      "patterns": [
        {
          "pattern": "execute(\"...\" + $VAR)"
        }
      ]
    }
  ],
  "notes": "Phase B rules"
}
```

**Response (201 Created)**:
```json
{
  "message": "Published 0.2.0 with 20 rules",
  "version": "0.2.0",
  "created_at": "2026-04-03T22:30:00Z",
  "rules_count": 20
}
```

**Error Responses**:

| Status | Detail | Cause |
|--------|--------|-------|
| 400 | version and rules are required | Missing required fields |
| 400 | Invalid version format: {version} | Version doesn't match X.Y.Z |
| 400 | Invalid version format: {version} | Service validation failed |
| 403 | Admin role required | User not authenticated or not admin |
| 409 | Version conflict: {version} | Version already exists in database |
| 422 | Validation error | Pydantic validation failed (malformed rules array) |
| 500 | Failed to publish version: {error} | Unexpected server error |

**Example**:
```bash
curl -X POST https://theloop-api.../api/v1/rules/publish \
  -H "Authorization: Bearer $FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "0.2.0",
    "rules": [...],
    "notes": "Phase B"
  }'
# Response: 201 {"message": "Published 0.2.0 with 20 rules", ...}
```

---

### POST /rules/deprecate

Mark a specific rule version as deprecated (admin only). Useful for rolling back when issues are discovered.

**Parameters**: JSON body

| Field | Type | Example | Required | Validation |
|-------|------|---------|----------|-----------|
| `version` | string | `0.1.0` | Yes | Semver X.Y.Z, must exist |

**Rate Limit**: 10/minute  
**Auth**: Requires valid Firebase token with `is_admin=true` claim  
**Cache Effect**: Invalidates `/latest` cache immediately

**Request Body**:
```json
{
  "version": "0.1.0"
}
```

**Response (200 OK)**:
```json
{
  "message": "Deprecated version 0.1.0",
  "version": "0.1.0",
  "deprecated_at": "2026-04-05T10:00:00Z"
}
```

**Error Responses**:

| Status | Detail | Cause |
|--------|--------|-------|
| 403 | Admin role required | User not authenticated |
| 404 | Version {version} not found | Version doesn't exist |
| 422 | Validation error | Invalid semver format |
| 500 | Failed to deprecate version: {error} | Unexpected server error |

**Example**:
```bash
# Deprecate v0.1.0 when issues found
curl -X POST https://theloop-api.../api/v1/rules/deprecate \
  -H "Authorization: Bearer $FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"version": "0.1.0"}'
# Response: 200 {"message": "Deprecated version 0.1.0", ...}

# Next /latest request returns v0.2.0 (the new active version)
```

---

## Error Handling

### Common Error Patterns

**4xx Client Errors** (request issue):
- Malformed JSON: 400
- Missing required fields: 400 or 422
- Version not found: 404
- Duplicate version: 409
- Permission denied: 403

**5xx Server Errors** (server issue):
- Database unavailable: 503
- Unexpected exception: 500

### Retry Strategy

**Recommended Client Behavior**:

```python
import asyncio

async def fetch_rules_with_retry(
    url: str,
    max_retries: int = 3,
    backoff_seconds: float = 1.0,
) -> dict:
    """Fetch rules with exponential backoff on transient errors."""
    for attempt in range(max_retries):
        try:
            response = await aiohttp.ClientSession().get(url, timeout=5)
            if response.status == 200:
                return await response.json()
            elif response.status >= 500:
                # Transient: retry
                await asyncio.sleep(backoff_seconds ** attempt)
                continue
            elif response.status >= 400:
                # Client error: don't retry
                raise ValueError(f"Client error: {response.status}")
        except asyncio.TimeoutError:
            # Transient: retry
            await asyncio.sleep(backoff_seconds ** attempt)
            continue
    
    # Fallback to backup rules after retries exhausted
    return load_fallback_rules(".semgrep/theloop-rules.yml.bak")
```

---

## Authentication

### Firebase Admin Check

All `POST` endpoints require Firebase Admin authentication:

```bash
# Get token (in app, Firebase SDK handles this)
TOKEN=$(firebase auth token)

# Use token in Authorization header
curl -H "Authorization: Bearer $TOKEN" https://api.../api/v1/rules/publish
```

**Token Requirements**:
1. Valid Firebase ID token (issued by `firebase-admin` SDK)
2. User must have `is_admin` custom claim in Firebase

**Future Enhancement**: Move `is_admin` check to Firestore custom claims or dedicated database table.

---

## Examples

### Publish New Version

```bash
#!/bin/bash

# Publish v0.2.0 with Phase B rules
curl -X POST https://api.loop.oute.pro/api/v1/rules/publish \
  -H "Authorization: Bearer $FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d @payload.json

# payload.json:
# {
#   "version": "0.2.0",
#   "rules": [...20 rules...],
#   "notes": "Phase B: 14 new rules"
# }
```

### Deprecate Bad Version

```bash
# Discover issue in v0.2.0
curl -X POST https://api.loop.oute.pro/api/v1/rules/deprecate \
  -H "Authorization: Bearer $FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"version": "0.2.0"}'

# Next /latest request will return v0.1.0 (previous active version)
```

### Fetch Latest from Workflow

```yaml
- name: Fetch latest rules
  run: |
    curl -s \
      --max-time 5 \
      --connect-timeout 2 \
      https://api.loop.oute.pro/api/v1/rules/latest \
      -o /tmp/rules.json
    
    # On error, use Phase A backup
    if [ $? -ne 0 ]; then
      cp .semgrep/theloop-rules.yml.bak /tmp/rules.json
      echo "⚠️ API fetch failed, using Phase A backup"
    fi
```

---

## Performance Notes

### Caching

**GET /rules/latest**:
- 5-minute TTL in API process memory
- Invalidated immediately on `POST /publish` or `POST /deprecate`
- Second request within 5 minutes: <10ms (cache hit)
- Expected hit rate: >80% of workflow runs

**GET /rules/{version}** and **GET /rules/versions**:
- No caching (specific queries)
- Expected latency: 50-200ms

### Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| GET /latest | 60/min | Per IP |
| GET /{version} | 60/min | Per IP |
| GET /versions | 60/min | Per IP |
| GET /deprecated | 60/min | Per IP |
| POST /publish | 10/min | Per authenticated user |
| POST /deprecate | 10/min | Per authenticated user |

---

## Support

**API Status**: https://api.loop.oute.pro/api/v1/health  
**Logs**: `gcloud run logs read theloop-api --region=us-central1 --limit=100`  
**Issues**: Report via https://loop.oute.pro/feedback
