# The Loop GitHub Actions Workflow

**Workflow**: `.github/workflows/theloop-guard.yml`  
**Version**: Phase B (v0.2.0+)  
**Status**: Production-ready

---

## Overview

The Loop's GitHub Actions workflow (`theloop-guard.yml`) automatically scans every pull request for patterns derived from production incidents. It fetches rules from the API (Phase B), falls back to static Phase A rules if the API is unavailable, converts JSON to Semgrep YAML format, validates the rules, executes the scan, and comments on the PR with findings.

## Workflow Steps

### Step 1: Checkout Code
```yaml
- name: Checkout
  uses: actions/checkout@v4
  with:
    fetch-depth: 1
    token: ${{ secrets.GITHUB_TOKEN }}
```
Checks out the PR code for scanning. `fetch-depth: 1` optimizes for speed.

### Step 2: Fetch Rules from API (with Fallback)
```bash
VERSION="${{ vars.THELOOP_RULES_VERSION || 'latest' }}"
curl -s \
  --max-time 5 \
  --connect-timeout 2 \
  -H "Authorization: Bearer ${{ secrets.THELOOP_API_TOKEN }}" \
  "https://api.loop.oute.pro/api/v1/rules/${VERSION}" \
  -o /tmp/rules.json
```

**Key Features**:
- **API Endpoint**: Fetches latest rules from `/api/v1/rules/latest` or specific version via `THELOOP_RULES_VERSION`
- **Timeout**: Hard limit of 5 seconds (curl `--max-time`), connection timeout of 2 seconds
- **Authentication**: Requires `THELOOP_API_TOKEN` secret (Bearer token for API auth)
- **Fallback**: If fetch fails (timeout, 5xx, connection error), automatically uses Phase A backup

**Fallback Trigger Conditions**:
1. curl exit code non-zero (timeout, DNS failure, connection refused)
2. HTTP 5xx response from API
3. Network error or timeout
4. Invalid response format

**Fallback Behavior**:
```bash
if [ $FETCH_EXIT -ne 0 ]; then
  cp .semgrep/theloop-rules.yml.bak /tmp/rules.json
  echo "fallback=true" >> $GITHUB_OUTPUT
fi
```

### Step 3: Verify Backup File
```yaml
- name: Verify backup rules file
  run: |
    if [ ! -f ".semgrep/theloop-rules.yml.bak" ]; then
      exit 1
    fi
```
Ensures Phase A backup rules exist (non-negotiable).

### Step 4: Convert JSON to YAML
```bash
python3 scripts/json_to_semgrep_yaml.py \
  --input /tmp/rules.json \
  --output .semgrep/theloop-rules.yml
```

Converts API JSON response to Semgrep YAML format. Validates schema:
- `rules` key exists and is non-empty list
- Each rule has: `id`, `languages`, `message`, `severity`, `patterns`
- No duplicate rule IDs
- Metadata preserved (incident_id, category, loop_url, remediation)

**Error Handling**: If conversion fails (schema violation, malformed JSON), workflow logs error and falls back to Phase A rules.

### Step 5: Validate Semgrep Rules
```bash
pip install semgrep --quiet
semgrep --validate --config .semgrep/theloop-rules.yml
```

Validates YAML syntax before scanning. Catches:
- YAML parse errors (indentation, syntax)
- Missing required rule fields
- Invalid pattern syntax

### Step 6: Run Semgrep Scan
```bash
semgrep scan \
  --config .semgrep/theloop-rules.yml \
  --json \
  --output /tmp/semgrep-results.json \
  --metrics off \
  --quiet
```

Executes Semgrep with The Loop rules. Outputs findings to JSON file for PR comment.

### Step 7: Comment PR with Findings
Uses `actions/github-script@v7` to:
1. Parse `/tmp/semgrep-results.json`
2. Render findings as table: Severity | Rule | File | Line | Incident Link
3. Separate ERROR (critical) from WARNING (advisory) findings
4. Update existing comment (avoid spam) or create new one

**Comment Format**:

```
## 🔁 The Loop — Incident Guard

🔴 **2 critical error(s) — merge blocked**

| Severity | Rule | File | Line | Incident |
|:---:|:---|:---|:---:|:---:|
| 🔴 ERROR | injection-001-sql-string-concat | src/api/db.py | 45 | [injection-001](https://...) |
| 🟡 WARN | unsafe-regex-001-redos-pattern | tests/utils.py | 102 | [unsafe-regex-001](https://...) |

---
> [The Loop](https://loop.oute.pro) | Incident Prevention
```

### Step 8: Fail on Critical Findings
```bash
if steps.semgrep.outputs.semgrep_exit != '0' && steps.semgrep.outputs.semgrep_exit != ''
then
  exit 1
fi
```

Blocks merge if ERROR-severity findings detected. WARNING findings are advisory only.

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `THELOOP_RULES_VERSION` | `latest` | Specific rule version to fetch (e.g., `0.1.0` for Phase A, `0.2.0` for Phase B) |
| `THELOOP_API_TOKEN` | (required) | GitHub secret for API authentication |

### GitHub Secrets (Required)

1. **`THELOOP_API_TOKEN`**: Bearer token for API authentication
   - Set in: GitHub repo → Settings → Secrets and variables → Actions
   - Format: Bearer token from The Loop API auth system

### GitHub Variables (Optional)

1. **`THELOOP_RULES_VERSION`**: Pin to specific rule version
   - Set in: GitHub repo → Settings → Secrets and variables → Variables
   - Example: `THELOOP_RULES_VERSION = 0.1.0` (locks to Phase A rules)
   - Omit or leave empty to use `latest` (default behavior)

---

## Troubleshooting

### Fetch Fails with Timeout

**Symptom**: Workflow logs show `curl: (28) Operation timeout. The timeout specified has expired.`

**Root Causes**:
- API endpoint unreachable (network issue)
- API slow (>5s response time)
- Network flakiness

**Diagnosis**:
```bash
# Check if API is online
curl -s https://api.loop.oute.pro/api/v1/health

# Check response time
curl -w "Total time: %{time_total}s\n" \
  https://api.loop.oute.pro/api/v1/rules/latest \
  -o /dev/null
```

**Solutions**:
1. **API is down**: Fallback automatically uses Phase A rules ✓
2. **API is slow**: Increase timeout from 5s to 10s in workflow (if acceptable)
3. **Network flaky**: Retry mechanism (add loop in workflow if needed)
4. **Temporary issue**: Wait and re-run workflow

### Validation Fails (YAML Syntax Error)

**Symptom**: Workflow step "Validate Semgrep rules" fails

**Root Causes**:
- API returned malformed JSON
- Conversion script has bug
- Invalid pattern syntax

**Diagnosis**:
```bash
# Check what API returned
curl https://theloop-api.../api/v1/rules/latest | jq '.rules[0]'

# Check output YAML
semgrep --validate --config .semgrep/theloop-rules.yml
```

**Solutions**:
1. **API returned invalid JSON**: Check API health + logs
2. **Conversion script error**: Check Python traceback in workflow logs
3. **Fallback triggered**: Workflow should have used Phase A `.bak` file automatically

### Duplicate Rule IDs Detected

**Symptom**: Conversion fails with `ValueError: Duplicate rule ID detected`

**Root Causes**:
- New rule ID conflicts with existing rule (same ID defined twice)
- Merge conflict in rules file not resolved properly

**Diagnosis**:
```bash
# Check for duplicate IDs in active rules
grep "^  - id:" .semgrep/theloop-rules.yml | sort | uniq -d
```

**Solutions**:
1. **Rename conflicting rule**: Use unique ID prefixes (e.g., `path-traversal-001` not `injection-001`)
2. **Resolve merge conflict**: Check git status, resolve `.semgrep/theloop-rules.yml` conflict
3. **Re-publish rules**: Delete bad version, publish corrected version

### Semgrep Finds 0 Rules

**Symptom**: Workflow completes but "0 rules loaded" or scan finds nothing

**Root Causes**:
- YAML indentation incorrect (Semgrep expects 2-space)
- Rule ID format invalid
- Pattern syntax invalid

**Diagnosis**:
```bash
# Validate YAML
semgrep --validate --config .semgrep/theloop-rules.yml

# Count rules
grep "^  - id:" .semgrep/theloop-rules.yml | wc -l
# Should be 20 (or 6 if fallback)

# Check indentation
cat .semgrep/theloop-rules.yml | head -20
```

**Solutions**:
1. **Fix indentation**: Semgrep rules use 2-space indent for nested fields
2. **Fix pattern syntax**: Check Semgrep docs for pattern-either, pattern-not, pattern-regex formats
3. **Fallback to Phase A**: If issue persists, manually test with Phase A rules

### Fallback Rules Not Found

**Symptom**: Workflow fails with `.semgrep/theloop-rules.yml.bak` not found

**Root Causes**:
- Backup file accidentally deleted or renamed
- Git ignored the file
- Merge conflict removed it

**Diagnosis**:
```bash
# Check if file exists
ls -la .semgrep/theloop-rules.yml.bak

# Check git history
git log -p --follow .semgrep/theloop-rules.yml.bak | head -50
```

**Solutions**:
1. **Restore from git**: `git checkout HEAD -- .semgrep/theloop-rules.yml.bak`
2. **Re-download from repo**: `curl -s https://raw.githubusercontent.com/.../theloop-rules.yml.bak -o .semgrep/theloop-rules.yml.bak`
3. **Commit immediately**: Never commit without this backup file

### Merge Blocked (False Positive)

**Symptom**: Critical finding detected but code is safe

**Root Causes**:
- Rule too broad (matches safe patterns)
- Poor pattern specificity
- Exception needed for this case

**Solutions**:
1. **Report false positive**: https://loop.oute.pro/feedback
2. **Suppress temporarily**: Add `# nosemgrep: rule-id` comment (not recommended)
3. **Pin to older rules**: Set `THELOOP_RULES_VERSION=0.1.0` temporarily
4. **Fix code**: If rule is valid but code is marginal, refactor to avoid pattern

---

## Performance

### Typical Workflow Duration

```
checkout:                   5s
fetch rules:              <1s (cached) or <100ms (fallback)
convert JSON→YAML:        <100ms
validate YAML:            <500ms
semgrep install:          3-5s
semgrep scan:           10-30s (depends on repo size)
comment PR:              <2s
───────────────────────────
TOTAL:                   20-50s
```

### Optimization Tips

1. **Cache Semgrep installation**: Use `actions/cache@v3` to cache Semgrep
2. **Parallel scanning**: Scan multiple directories in parallel (advanced)
3. **Ignore large files**: Add `--exclude` patterns for generated code
4. **Reduce scope**: Scan only `src/` instead of entire repo if possible

---

## Version Pinning

To stay on a specific rule version (e.g., Phase A), set the GitHub variable:

```
THELOOP_RULES_VERSION = 0.1.0
```

Workflow will always fetch `/api/v1/rules/0.1.0`. Useful for:
- Deferring upgrades to Phase B (14 new rules)
- Testing specific versions
- Rollback if issue found in new version

To revert to latest: Delete the variable (workflow defaults to `latest`).

---

## Integration with Other Workflows

### Combining with Other Checks

The Loop workflow is independent and can run alongside:
- Linting (eslint, ruff)
- Type checking (mypy, tsc)
- Unit tests (pytest, vitest)
- Security scans (Trivy, OWASP)

**No conflicts**: The Loop only affects merge status via critical findings.

### Using Rules Elsewhere

Rules can be reused outside GitHub Actions:
```bash
# Local scanning
semgrep scan --config .semgrep/theloop-rules.yml src/

# CI/CD
docker run returntocorp/semgrep:latest \
  semgrep scan --config .semgrep/theloop-rules.yml
```

---

## Support

- **Workflow Issues**: Check logs in GitHub Actions tab
- **API Status**: https://api.loop.oute.pro/api/v1/health
- **API Logs**: `gcloud run logs read theloop-api --region=us-central1 --limit=100`
- **Report Issues**: https://loop.oute.pro/feedback
- **API Docs**: See `specs/011-phase-b-api-integration/API.md`

