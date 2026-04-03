# GitHub Actions Workflow Execution Contract

**Version**: 0.1.0-Phase-A  
**Workflow Name**: `theloop-guard.yml`  
**Target Projects**: Any GitHub project (self-hosted or GH Cloud)

---

## Contract Definition

### Trigger

```yaml
on:
  pull_request:
    branches: [main, master, develop]
    types: [opened, synchronize, reopened]
```

**Expected Behavior**:
- Workflow triggers when PR is opened, updated (new commit), or reopened
- Only triggers for PRs targeting `main`, `master`, or `develop` branches
- Does NOT trigger for draft PRs (GitHub Actions default behavior)

---

### Required Files

The workflow **MUST** find these files in the project before executing:

```
.semgrep/theloop-rules.yml       ← Required (checked at step 3)
.github/workflows/theloop-guard.yml  ← This file
```

**If missing**, workflow:
1. Outputs error message with installation instructions
2. Displays error in PR comment
3. Does NOT fail the job (allows merge; post-commit fix)

---

### Job Configuration

```yaml
jobs:
  semgrep-scan:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read              # Checkout code
      pull-requests: write        # Create/update PR comments
      security-events: write      # Future: SARIF upload
```

**Expected Behavior**:
- Job runs on latest Ubuntu runner
- Total timeout: 10 minutes (job cancelled if exceeded)
- Permissions are minimized to requested operations only
- No access to secrets unless explicitly requested

---

### Step 1: Checkout

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

**Expected Behavior**:
- Clones repository at PR commit
- Full history fetched (allows diff/blame operations if needed)
- Permissions: `contents: read`

---

### Step 2: Install Semgrep

```yaml
- run: pip install semgrep --quiet
```

**Expected Behavior**:
- Installs latest stable Semgrep from PyPI
- Python 3.9+ is pre-installed in GitHub Actions
- Completes in <30 seconds (cached on runner)
- `--quiet` suppresses verbose output

---

### Step 3: Verify Rules File

```yaml
- run: |
    if [ ! -f ".semgrep/theloop-rules.yml" ]; then
      echo "❌ Rules file not found. Install THELOOP.md"
      exit 1
    fi
    semgrep --validate --config .semgrep/theloop-rules.yml
    echo "✅ Rules validated"
```

**Expected Behavior**:
- Checks that `.semgrep/theloop-rules.yml` exists
- If missing: outputs error message, fails job
- If exists: validates YAML syntax and Semgrep pattern correctness
- If invalid YAML: fails job with validation error
- If valid: logs success message and continues

---

### Step 4: Run Semgrep Scan

```yaml
- run: |
    timeout 30 semgrep scan \
      --config .semgrep/theloop-rules.yml \
      --json \
      --output semgrep-results.json \
      --metrics off \
      --quiet
```

**Expected Behavior**:
- Runs Semgrep scan on repository
- Outputs results in JSON format (not table)
- Metrics telemetry disabled (`--metrics off`)
- 30-second timeout wrapper:
  - If scan completes in <10s: normal completion ✅
  - If scan completes in 10-30s: warning logged but results captured ⚠️
  - If scan exceeds 30s: timeout, partial results written, warning in logs ⏱️
- Exit code: 0 (does NOT indicate findings presence; only errors)

---

### Step 5: Analyze Results & Comment PR

**Input**: `semgrep-results.json`

**Processing**:

```javascript
// 1. Parse JSON
const results = JSON.parse(fs.readFileSync('semgrep-results.json', 'utf8')).results || [];

// 2. Classify by severity
const errors = results.filter(r => r.extra.severity === 'ERROR');
const warnings = results.filter(r => r.extra.severity === 'WARNING');

// 3. Format as table (top 50)
const display = results
  .sort((a, b) => (severityRank[b.extra.severity] || 0) - (severityRank[a.extra.severity] || 0))
  .slice(0, 50);

// 4. Generate comment body
let comment = '## 🔁 The Loop — Incident Guard\n\n';
if (results.length === 0) {
  comment += '✅ **No incident patterns detected.** Your code is clean.';
} else {
  comment += `| Severity | Rule | File | Line | Incident |\n`;
  comment += `|:---:|:---|:---|:---:|:---:|\n`;
  for (const r of display) {
    comment += `| ${icon(r.extra.severity)} | ${r.check_id} | ${r.path} | ${r.start.line} | [${r.extra.metadata.incident_id}](${r.extra.metadata.loop_url}) |\n`;
  }
  if (results.length > 50) {
    comment += `\n[View all ${results.length} findings in workflow artifacts](...)\n`;
  }
}

comment += '\n---\n> 🔁 [The Loop](https://loop.oute.pro) | [Report false positive](https://loop.oute.pro/feedback)';

// 5. Find existing comment (authored by github-actions[bot], contains "The Loop")
const existing = comments.find(c => c.body.includes('The Loop — Incident Guard'));

// 6. Post or update
if (existing) {
  github.rest.issues.updateComment({...existing.id, body: comment});
} else {
  github.rest.issues.createComment({...issue.number, body: comment});
}
```

**Expected Behavior**:

| Scenario | Expected Output |
|----------|---|
| 0 findings | "✅ No incident patterns detected." |
| 1-50 findings | Markdown table with severity icon, rule ID, file, line, incident link |
| 50+ findings | Table (top 50) + link to full report |
| Comment exists | UPDATE existing comment (no duplicate) |
| Comment missing | CREATE new comment |
| GitHub API fails | Log error (non-blocking); continue |

---

### Step 6: Set Job Status

```yaml
- name: Fail on errors
  if: steps.semgrep.outputs.errors != '0'
  run: exit 1
```

**Expected Behavior**:

| Condition | Job Status | Merge Impact |
|-----------|-----------|---|
| ERROR findings > 0 | ❌ FAILED | Merge blocked (GitHub branch protection) |
| WARNING findings only | ✅ PASSED | Merge allowed (branch protection not triggered) |
| No findings | ✅ PASSED | Merge allowed |
| Scan timeout (>30s) | ⚠️ WARNING | Merge allowed; warning in logs |
| Rules file missing | ❌ FAILED | Merge blocked |
| Invalid YAML | ❌ FAILED | Merge blocked |

---

## Data Formats

### GitHub API: Create/Update PR Comment

**Endpoint**: `POST /repos/{owner}/{repo}/issues/{issue_number}/comments` (create)  
**Endpoint**: `PATCH /repos/{owner}/{repo}/issues/comments/{comment_id}` (update)

**Request Body**:
```json
{
  "body": "## 🔁 The Loop — Incident Guard\n\n..."
}
```

**Response**: 201 Created / 200 OK

**Error Handling**:
- `403 Forbidden` (rate limit) → log warning, do NOT fail job
- `404 Not Found` (comment deleted) → create new comment
- `422 Unprocessable Entity` (invalid body) → log error, do NOT fail job

---

### Semgrep JSON Output

**File**: `semgrep-results.json`  
**Format**: Semgrep JSON report format (v1)

```json
{
  "version": "1.0",
  "results": [
    {
      "check_id": "theloop.injection-001-sql-string-concat",
      "path": "src/db.py",
      "start": {
        "line": 42,
        "col": 5,
        "offset": 1234
      },
      "end": {
        "line": 42,
        "col": 30,
        "offset": 1259
      },
      "extra": {
        "message": "[The Loop] SQL injection via string concatenation detected...",
        "severity": "ERROR",
        "metadata": {
          "incident_id": "injection-001",
          "category": "injection",
          "loop_url": "https://loop.oute.pro/incidents/injection-001",
          "remediation": "Use parameterized queries..."
        },
        "fingerprint": "abc123def456"
      }
    }
  ],
  "errors": [],
  "stats": {
    "files": {
      "scanned": 42,
      "skipped": 3,
      "error": 0
    },
    "rules": {
      "parsed": 6,
      "run": 6
    }
  }
}
```

---

## Error Scenarios

### Scenario 1: Rules File Missing

**Trigger**: User copies workflow but forgets to copy rules file

**Expected Behavior**:
1. Step 3 detects missing file
2. Outputs: `❌ File .semgrep/theloop-rules.yml not found. Install THELOOP.md`
3. Job fails (step exits with code 1)
4. PR shows red ❌ status
5. Developer reads error, copies rules file, commits
6. Workflow re-runs and succeeds

---

### Scenario 2: Invalid YAML in Rules File

**Trigger**: User manually edits rules file and introduces syntax error

**Expected Behavior**:
1. Step 3 runs `semgrep --validate`
2. Semgrep outputs: `ERROR: Invalid YAML at line 15: ...`
3. Job fails
4. PR shows red ❌ status
5. Developer fixes YAML, commits
6. Workflow re-runs

---

### Scenario 3: GitHub API Rate Limit (429)

**Trigger**: High-frequency PRs or other GitHub API usage consuming rate limit

**Expected Behavior**:
1. Step 5 attempts to post comment
2. GitHub API returns 429 Too Many Requests
3. Error is caught and logged: `[WARN] Failed to post comment: 429 Rate Limited`
4. Job continues (does NOT exit with error)
5. Job completes with status ✅ PASSED
6. PR merge is NOT blocked
7. Results are still visible in workflow logs/artifacts
8. Workflow retries comment on next PR or manual re-run

---

### Scenario 4: Semgrep Scan Exceeds 30 Seconds

**Trigger**: Very large repository (1M+ files) or very slow runner

**Expected Behavior**:
1. Timeout wrapper hits 30-second limit
2. Semgrep process is killed (`timeout 30` sends SIGTERM)
3. Partial results written to `semgrep-results.json` (if possible)
4. Warning logged: `[WARN] Semgrep scan exceeded 30s; partial results reported`
5. Step 5 processes partial results (incomplete but still actionable)
6. Comment shows: `⚠️ Scan exceeded timeout — showing first N findings (partial results)`
7. Job completes with status ✅ PASSED (timeout does NOT fail job)
8. Merge is NOT blocked by timeout

---

## Performance Targets

| Metric | Target | Hard Limit | Notes |
|--------|--------|-----------|-------|
| Scan time | <10s | 30s | Includes checkout, install, validation, scan |
| Comment post | <2s | N/A | GitHub API timeout is 30s |
| Total job time | <15s | 10m | Job-level timeout in workflow config |
| Finding processing | <1s | N/A | JSON parsing + table formatting |
| Memory usage | <500MB | N/A | Semgrep baseline + results |

---

## Backward Compatibility

**Current Version**: 0.1.0-Phase-A (static rules)

**Breaking Changes** (Phase B onwards):
- If workflow is updated with API-driven rule fetching, Phase A projects continue using static rules unless they manually copy new workflow
- No automatic upgrade; opt-in via copy-paste

**Non-Breaking Changes** (allowed in Phase A patch releases):
- Adding new rules (old projects keep 6, new projects get more)
- Updating rule messages (backward compatible)
- Fixing false positives (backward compatible)
- Improving error messages (backward compatible)

---

## Testing & Validation

This contract is validated by:

1. **Unit Tests** (`tests/unit/`):
   - JSON parsing
   - Comment formatting
   - Severity classification
   - Finding sorting

2. **Integration Tests** (`tests/integration/`):
   - Test repository (`the-loop-tester`) PRs
   - Validate all 6 rules fire correctly on `bad/` code
   - Validate zero rules fire on `good/` code
   - Validate comment is updated (not duplicated) on new commits
   - Validate status check blocks/allows merge correctly

3. **Manual Testing** (before release):
   - Run workflow on test repo
   - Verify PR comment format in GitHub UI
   - Verify merge blocking behavior
   - Verify GitHub API error handling

---

## Summary

The workflow is a pure orchestrator: it does NOT implement domain logic, parsing rules, or incident matching. It:
1. Invokes Semgrep (externally)
2. Formats results (parsing Semgrep JSON)
3. Posts to GitHub (GitHub API)
4. Sets status (job exit code)

The rule engine and pattern matching are entirely Semgrep's responsibility.
