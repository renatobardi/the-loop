# Phase B Troubleshooting Guide

**Common issues and solutions for the Phase B Rules API.**

---

## API Errors

### "API fetch failed (timeout/error), using Phase A backup"

**Symptom**: GitHub Actions workflow shows this warning, falls back to Phase A rules

**Root Causes**:
1. API endpoint unreachable (network issue)
2. API response timeout (>5 seconds)
3. Invalid JSON response from API
4. THELOOP_API_TOKEN secret missing/invalid

**Diagnosis**:

```bash
# Check if API is online
curl -s https://api.loop.oute.pro/api/v1/health
# Expected: 200 OK with {"status": "healthy"}

# Check rules endpoint directly
curl -s https://api.loop.oute.pro/api/v1/rules/latest \
  | jq . | head -20

# Check response time
curl -w "Time: %{time_total}s\n" \
  https://api.loop.oute.pro/api/v1/rules/latest \
  -o /dev/null
# Should be <1 second
```

**Solutions**:

| Diagnosis | Fix |
|-----------|-----|
| API responds 200 but slow | API under heavy load; wait or increase timeout from 5s to 10s |
| API responds 500 | Check API logs: `gcloud run logs read theloop-api --limit=50` |
| Connection refused | API may be deploying; fallback handles this ✅ |
| Invalid JSON response | API bug; report at https://loop.oute.pro/feedback |

---

### "Validation error: Missing 'rules' key in JSON input"

**Symptom**: Workflow fails at "Convert JSON to YAML" step

**Root Causes**:
1. API returned non-JSON response (e.g., HTML error page)
2. API response is malformed
3. Fallback `.bak` file is broken/missing

**Diagnosis**:

```bash
# Check what the API returned
curl -s https://api.loop.oute.pro/api/v1/rules/latest \
  -o /tmp/response.json

file /tmp/response.json  # Shows "JSON data" or "HTML document"

cat /tmp/response.json | head -5  # Inspect first 5 lines
```

**Solutions**:

1. **API returned HTML error page**:
   ```bash
   # Check API health
   curl https://api.loop.oute.pro/api/v1/health
   
   # If API is down, fallback should kick in automatically
   # If still failing, ensure .semgrep/theloop-rules.yml.bak exists
   ls -la .semgrep/theloop-rules.yml.bak
   ```

2. **Backup file missing**:
   ```bash
   # Restore from repo
   git checkout HEAD -- .semgrep/theloop-rules.yml.bak
   git push
   ```

3. **Backup file corrupted**:
   ```bash
   # Check backup syntax
   semgrep --validate --config .semgrep/theloop-rules.yml.bak
   
   # If broken, re-create from Phase A rules
   curl -s https://raw.githubusercontent.com/renatobardi/the-loop/main/.semgrep/theloop-rules.yml.bak \
     -o .semgrep/theloop-rules.yml.bak
   git add .semgrep/theloop-rules.yml.bak
   git commit -m "chore: restore Phase A backup rules"
   git push
   ```

---

## Workflow Issues

### Semgrep finds 0 rules in converted YAML

**Symptom**: Workflow runs successfully but finds 0 rules (all tests pass)

**Root Causes**:
1. YAML conversion didn't handle patterns correctly
2. Semgrep YAML syntax issue

**Diagnosis**:

```bash
# Inspect converted YAML
cat .semgrep/theloop-rules.yml | head -50

# Validate YAML syntax
semgrep --validate --config .semgrep/theloop-rules.yml

# Count rules in YAML
grep "^  - id:" .semgrep/theloop-rules.yml | wc -l
# Should be >0
```

**Solutions**:

1. **YAML indentation issue**:
   ```bash
   # Semgrep expects 2-space indentation for nested rules
   # Example (correct):
   # rules:
   #   - id: injection-001          ← 2 spaces
   #     languages: [python]        ← 4 spaces
   
   # Check indentation
   cat .semgrep/theloop-rules.yml | grep "^  - id:" | wc -l
   ```

2. **Patterns not formatted correctly**:
   ```python
   # In json_to_semgrep_yaml.py, ensure patterns are serialized correctly:
   
   # Bad:
   lines.append(f"      - pattern: {pattern['pattern']}")
   
   # Good (handles special chars):
   import shlex
   pattern_str = shlex.quote(pattern['pattern'])
   lines.append(f"      - pattern: {pattern_str}")
   ```

---

## Version Issues

### "Version {version} not found" (404)

**Symptom**: Workflow tries to fetch specific version, gets 404

**Root Causes**:
1. Version doesn't exist in API database
2. THELOOP_RULES_VERSION variable is typo'd
3. Version was deleted (rare)

**Diagnosis**:

```bash
# List all available versions
curl https://api.loop.oute.pro/api/v1/rules/versions \
  | jq '.versions[].version'
# Output should include your target version

# Check your pinned version
echo $THELOOP_RULES_VERSION
```

**Solutions**:

1. **Version typo**:
   ```bash
   # Verify correct version exists
   curl https://api.loop.oute.pro/api/v1/rules/0.1.0
   # Should return 200 OK
   
   # If not found, use /latest
   curl https://api.loop.oute.pro/api/v1/rules/latest
   ```

2. **Fix THELOOP_RULES_VERSION**:
   ```bash
   # In GitHub Settings, update the variable to correct value
   # Or unset it to use "latest" (default)
   ```

3. **Check for deprecated versions**:
   ```bash
   curl https://api.loop.oute.pro/api/v1/rules/deprecated \
     | jq '.versions[].version'
   
   # If your pinned version is deprecated, you may want to upgrade
   ```

---

## Caching Issues

### "GET /latest returns old version"

**Symptom**: Published v0.2.0, but `/latest` still returns v0.1.0

**Root Causes**:
1. Cache not invalidated after publish
2. Cache TTL not expired yet
3. Multiple API instances not coordinated

**Diagnosis**:

```bash
# Check what /latest returns now
curl https://api.loop.oute.pro/api/v1/rules/latest \
  | jq .version

# Check all versions
curl https://api.loop.oute.pro/api/v1/rules/versions \
  | jq '.versions[] | {version, status}'
```

**Solutions**:

1. **Cache TTL not expired**:
   - API has 5-minute cache
   - Wait 5 minutes for natural expiry
   - Or redeploy API to clear cache

2. **Cache invalidation failed during publish**:
   ```bash
   # Manually invalidate by hitting a different version
   # (This forces cache refresh on next /latest call)
   curl https://theloop-api.../api/v1/rules/0.1.0
   
   # Then retry /latest
   curl https://theloop-api.../api/v1/rules/latest
   ```

---

## Database Issues

### "RuleVersionNotFoundError" (404) when version exists

**Symptom**: Version is listed in `/versions` but specific query returns 404

**Root Causes**:
1. Database replication lag (Cloud SQL primary/replica mismatch)
2. Recent migration not applied
3. Transaction isolation issue

**Diagnosis**:

```bash
# Check both endpoints
curl https://theloop-api.../api/v1/rules/versions | jq '.versions[] | select(.version=="0.2.0")'
# Should show v0.2.0

curl https://theloop-api.../api/v1/rules/0.2.0
# If 404 but version shows in list, it's replication lag
```

**Solutions**:

1. **Replication lag** (resolves in <30s):
   - Wait and retry
   - Or fallback to Phase A rules in workflow

2. **Recent migration not applied**:
   ```bash
   # Check Alembic migrations
   gcloud sql connect theloop-db --user=postgres
   
   # In psql:
   SELECT version_num FROM alembic_version;
   # Should show latest migration (e.g., 007)
   
   # If not, re-run:
   alembic upgrade head
   ```

---

## Permission Issues

### "Admin role required" (403)

**Symptom**: Publishing new version returns 403, though user is authenticated

**Root Causes**:
1. User not marked as admin in Firebase
2. Custom claim `is_admin` not set correctly
3. Token doesn't include admin claim

**Diagnosis**:

```bash
# Check your Firebase user
firebase auth:get $USER_EMAIL --project=theloopoute

# Verify custom claims include is_admin
firebase auth:get $USER_EMAIL --project=theloopoute | grep is_admin
```

**Solutions**:

1. **Set admin claim in Firebase**:
   ```bash
   # Via Firebase Console:
   # Authentication → Users → Select user → Custom Claims → Add:
   # {
   #   "is_admin": true
   # }
   ```

2. **Or use firebase CLI**:
   ```bash
   firebase auth:set-custom-claims $USER_EMAIL \
     '{"is_admin": true}' \
     --project=theloopoute
   ```

3. **Verify token includes claim**:
   ```bash
   # Decode JWT (use jwt.io or jq)
   TOKEN=$( < /dev/stdin | cut -d'.' -f2 | base64 -d)
   # Should include "is_admin": true
   ```

---

## Workflow Performance Issues

### Workflow runs take 60+ seconds

**Symptom**: GitHub Actions workflow very slow

**Breakdown** (expected):
```
Checkout:                     5s
Fetch rules:                  2s (or <100ms if API timeout + fallback)
Convert JSON→YAML:            1s
Validate YAML:                1s
Semgrep scan:               30-50s (depends on repo size)
Comment PR:                   2s
────────────────────────────────
Total:                      40-60s ✓ Normal
```

**Diagnosis**:

```bash
# Check Semgrep scan time
# Look at workflow logs for step timings
# If "Semgrep scan" takes >60s, repo may be large
```

**Solutions**:

1. **Reduce scan scope**:
   ```yaml
   semgrep scan \
     --config .semgrep/theloop-rules.yml \
     src/                    # ← Limit to src/ instead of whole repo
     --json
   ```

2. **Parallelize**: Run Semgrep on multiple parts in parallel (GitHub Actions matrix)

3. **Cache Semgrep**: Add `--cache` flag to reuse previous scans

---

## Common Patterns

### Resetting to Phase A Manually

If Phase B has issues and you need to rollback:

```bash
# Remove API fetch step from workflow
# Update workflow to use static backup:

cat << 'EOF' > .semgrep/theloop-rules.yml
# Copy from .bak
$(cat .semgrep/theloop-rules.yml.bak)
EOF

git add .github/workflows/theloop-guard.yml .semgrep/theloop-rules.yml
git commit -m "chore: rollback to Phase A (static rules)"
git push
```

All future PRs use Phase A rules until you re-enable Phase B.

### Debugging Conversion Issues

```bash
# Save API response
curl https://api.loop.oute.pro/api/v1/rules/latest \
  -o /tmp/api-response.json

# Convert locally
python3 scripts/json_to_semgrep_yaml.py \
  --input /tmp/api-response.json \
  --output /tmp/converted.yml

# Inspect output
cat /tmp/converted.yml | head -50

# Validate
semgrep --validate --config /tmp/converted.yml
```

### Test Fallback Logic

```bash
# Simulate API failure (rename backup temporarily)
mv .semgrep/theloop-rules.yml.bak .semgrep/theloop-rules.yml.bak.bak

# Create PR; workflow should fail at fetch and use... oh wait, backup is gone!
# This tests that fallback logic is in place

# Restore
mv .semgrep/theloop-rules.yml.bak.bak .semgrep/theloop-rules.yml.bak
```

---

## Getting Help

- **API Status**: https://api.loop.oute.pro/api/v1/health
- **API Logs**: `gcloud run logs read theloop-api --region=us-central1 --limit=100`
- **Report Issues**: https://loop.oute.pro/feedback
- **API Docs**: [API.md](./API.md)
- **Versioning Guide**: [VERSIONING.md](./VERSIONING.md)
