# Deployment Checklist: Spec-022 Product Releases Notification

**Status**: Ready for merge to main  
**Automated**: Database migrations (M2) via GitHub Actions  
**Manual**: GitHub token setup (M1) via GCP Console

---

## ✅ M1: GitHub API Token Setup (5 minutes)

### Via GitHub Web Console

1. **Go to GitHub Settings**:
   - Visit: https://github.com/settings/tokens
   - Click: "Generate new token (classic)"

2. **Configure Token**:
   - **Token name**: `GITHUB_TOKEN_THE_LOOP` (or any name)
   - **Expiration**: `No expiration` (recommended) or set a period
   - **Select scopes**: Check **ONLY** `public_repo`
     - This gives read-only access to public repos (exactly what we need)

3. **Generate & Copy**:
   - Click: "Generate token"
   - **Copy immediately** (token starts with `ghp_`)
   - **Save securely** (won't be shown again)

### Via GCP Console Web

4. **Create Secret in GCP**:
   - Go to: https://console.cloud.google.com/security/secret-manager?project=theloopoute
   - Click: "Create Secret"
   - **Name**: `GITHUB_TOKEN` (exact name — used by Cloud Run env vars)
   - **Secret value**: Paste the token from step 3
   - Click: "Create Secret"

5. **Grant Cloud Run Access**:
   - Click on the `GITHUB_TOKEN` secret (from list)
   - Click: "Grant Access"
   - **Select a principal**: `theloop-api@theloopoute.iam.gserviceaccount.com`
   - **Assign role**: `Secret Accessor`
   - Click: "Save"

✅ **M1 COMPLETE** — Token is now accessible to the API

---

## ✅ M2: Database Migration (AUTOMATIC)

**No manual action needed.** The deployment pipeline automatically runs database migrations.

### How It Works

1. **On merge to `main`**: GitHub Actions workflow `deploy.yml` starts
2. **Before Cloud Run deploy**: Migration step runs:
   - Fetches database credentials from Secret Manager
   - Starts Cloud SQL Proxy
   - Runs `alembic upgrade head` (applies all pending migrations, including 023)
   - Deploys updated code to Cloud Run

3. **Result**: Release tables created, API running with new code

### Verification

After deployment, verify migration was applied:

```bash
# SSH into Cloud SQL instance or use psql
psql postgresql://user:pass@host/theloop-db -c \
  "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"

# Should see:
# releases
# release_notification_status
```

---

## 📋 Pre-Merge Checklist

- [ ] PR created from `feat/022-product-releases-notification` to `main`
- [ ] GitHub Actions CI passes:
  - [ ] Lint (ruff + eslint)
  - [ ] Type-check (mypy + TypeScript)
  - [ ] Tests (pytest + vitest)
  - [ ] Build (Docker image)
  - [ ] Trivy security scan
- [ ] Code review approved
- [ ] **M1 complete**: `GITHUB_TOKEN` secret created in GCP
- [ ] Ready to merge

---

## 📋 Post-Merge Checklist

After merge to `main`:

- [ ] Wait for GitHub Actions deployment to complete (~5-10 minutes)
- [ ] Verify Cloud Run deployment succeeded (Cloud Run > theloop-api > Logs)
- [ ] Check database: `releases` and `release_notification_status` tables exist
- [ ] Test API endpoint:
  ```bash
  curl -H "Authorization: Bearer <firebase-token>" \
    https://api.loop.oute.pro/api/v1/releases/unread-count
  # Should return: {"unread_count": 0}
  ```
- [ ] Verify Bell icon appears in production navbar
- [ ] Admin: Sync releases from GitHub:
  ```bash
  curl -X POST \
    -H "Authorization: Bearer <firebase-admin-token>" \
    https://api.loop.oute.pro/api/v1/admin/releases/sync
  # Should return: {"status": "success", "synced_count": N, ...}
  ```

---

## 🔍 Troubleshooting

### Issue: Migration fails during deploy

**Symptoms**: Cloud Run deploy fails, logs show "alembic upgrade" error

**Fix**:
1. Check database is accessible: Cloud SQL instance running?
2. Verify Cloud SQL Proxy started: Check workflow logs
3. Manual migration (if needed):
   ```bash
   cd apps/api
   export DATABASE_URL="postgresql://user:pass@host/db"
   alembic upgrade head
   ```

### Issue: API returns 401 when calling `/releases/`

**Cause**: Missing Firebase token or user not authenticated

**Fix**: Ensure you're passing a valid Firebase JWT in the Authorization header

### Issue: Releases not appearing

**Cause**: GitHub sync hasn't been run

**Fix**: Admin user calls `POST /api/v1/admin/releases/sync` to import releases from GitHub

### Issue: Cloud Run deploy skipped migration

**Cause**: Migration step ran before image was built, or pipeline interrupted

**Fix**: Check workflow logs. If migration was skipped, redeploy or run manually.

---

## 🚀 Environment Variables

After M1 is complete, these env vars will be automatically set by Cloud Run:

| Variable | Source | Used By |
|----------|--------|---------|
| `DATABASE_URL` | Secret Manager `THELOOP_API_DATABASE_URL` | SQLAlchemy connection |
| `GITHUB_TOKEN` | Secret Manager `GITHUB_TOKEN` (M1) | GitHub Releases API client |
| `CORS_ORIGINS` | Hardcoded in deploy.yml | FastAPI CORS middleware |

---

## 📞 Questions?

- **Setup issues?** See `specs/022-product-releases-notification/IMPLEMENTATION_COMPLETE.md` section "Troubleshooting"
- **API details?** See `specs/022-product-releases-notification/contracts/release-api.md`
- **User guide?** See `specs/022-product-releases-notification/quickstart.md`

---

**Status**: ✅ Ready to merge and deploy  
**M1**: Manual (5 min via GCP Console)  
**M2**: Automatic (via GitHub Actions)
