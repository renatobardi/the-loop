# Quick Start: GitHub + Semgrep Integration — Phase A

**For**: Developers implementing Phase A rules distribution  
**Time**: 15 minutes setup + 30 minutes implementation

---

## Overview

Phase A delivers 3 deliverable files that projects can copy-paste:

1. **`.semgrep/theloop-rules.yml`** — 6 incident-derived Semgrep rules
2. **`.github/workflows/theloop-guard.yml`** — GitHub Actions workflow
3. **`THELOOP.md`** — Installation guide for end users

This quickstart walks you through creating these files, validating them, and testing end-to-end via the test repository.

---

## Prerequisites

- Python 3.9+ with pip
- Semgrep CLI: `pip install semgrep`
- GitHub account with admin access to test repo
- Bash or equivalent shell
- `jq` for JSON parsing (optional, for local testing)

---

## Step 1: Create the Rules File (`.semgrep/theloop-rules.yml`)

### File Location
```
.semgrep/theloop-rules.yml
```

### Content Structure

```yaml
# theloop-rules.yml
# The Loop — Incident Patterns (Phase A)
# Version: 0.1.0 (static, immutable)
# For installation & updates: see THELOOP.md

rules:
  # RULE 1: SQL Injection via String Concatenation
  - id: injection-001-sql-string-concat
    languages: [python, javascript, typescript, java, go, ruby]
    message: |
      [The Loop] SQL injection via string concatenation detected...
    severity: ERROR
    metadata:
      incident_id: "injection-001"
      category: "injection"
      loop_url: "https://loop.oute.pro/incidents/injection-001"
      remediation: "Use parameterized queries..."
    patterns:
      - pattern-either:
          - pattern: $DB.execute("..." + $INPUT)
          - pattern: $DB.execute("...%s" % $INPUT)
          - pattern: $DB.execute(f"...{$INPUT}...")

  # RULE 2: eval() with Dynamic Input
  - id: injection-002-eval-dynamic-input
    # ... (continue for all 6 rules)

  # ... repeat for rules 3–6 (unsafe-api-usage-001, missing-safety-check-001, missing-error-handling-001, unsafe-regex-001)
```

### Key Points

- **Language list**: Semgrep supports multiple languages per rule; use what applies
- **Pattern syntax**: See [Semgrep Pattern Docs](https://semgrep.dev/docs/writing-rules/pattern-syntax/)
- **Metadata**: All 4 required fields (`incident_id`, `category`, `loop_url`, `remediation`)
- **Message**: Should reference incident ID and severity clearly
- **Severity**: Only `ERROR` or `WARNING` (not CRITICAL, INFO, etc.)

### Validation

```bash
# Check YAML syntax
semgrep --validate --config .semgrep/theloop-rules.yml

# Expected output:
# ✅ Config is valid
```

---

## Step 2: Create the Workflow (`.github/workflows/theloop-guard.yml`)

### File Location
```
.github/workflows/theloop-guard.yml
```

### Content Structure

```yaml
name: "🔁 The Loop — Incident Guard"

on:
  pull_request:
    branches: [main, master, develop]
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write
  security-events: write

jobs:
  semgrep-scan:
    name: "Scan — Static Rules"
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      # 1. Checkout
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      # 2. Install Semgrep
      - name: Install Semgrep
        run: |
          pip install semgrep --quiet
          semgrep --version

      # 3. Verify rules file
      - name: Verify rules file
        run: |
          if [ ! -f ".semgrep/theloop-rules.yml" ]; then
            echo "❌ File .semgrep/theloop-rules.yml not found"
            exit 1
          fi
          semgrep --validate --config .semgrep/theloop-rules.yml
          echo "✅ Rules validated"

      # 4. Run scan
      - name: Run Semgrep scan
        id: semgrep
        run: |
          timeout 30 semgrep scan \
            --config .semgrep/theloop-rules.yml \
            --json \
            --output semgrep-results.json \
            --metrics off \
            --quiet || true
          
          # Count findings
          if [ -f semgrep-results.json ]; then
            ERRORS=$(jq '[.results[] | select(.extra.severity == "ERROR")] | length' semgrep-results.json)
            echo "errors=$ERRORS" >> $GITHUB_OUTPUT
          fi

      # 5. Comment PR
      - name: Comment PR with findings
        if: always()
        uses: actions/github-script@v7
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const fs = require('fs');
            
            let body = '## 🔁 The Loop — Incident Guard\n\n';
            
            if (!fs.existsSync('semgrep-results.json')) {
              body += '⚠️ Scan did not produce results.';
            } else {
              const data = JSON.parse(fs.readFileSync('semgrep-results.json', 'utf8'));
              const results = data.results || [];
              
              if (results.length === 0) {
                body += '✅ No incident patterns detected.';
              } else {
                body += '| Severity | Rule | File | Line | Incident |\n';
                body += '|:---:|:---|:---|:---:|:---:|\n';
                
                const errors = results.filter(r => r.extra?.severity === 'ERROR');
                const warnings = results.filter(r => r.extra?.severity === 'WARNING');
                
                for (const r of results.slice(0, 50)) {
                  const sev = r.extra?.severity === 'ERROR' ? '🔴 ERROR' : '🟡 WARN';
                  const rule = r.check_id.split('.').pop();
                  const meta = r.extra?.metadata || {};
                  body += `| ${sev} | \`${rule}\` | \`${r.path}\` | ${r.start?.line || '?'} | [${meta.incident_id || '?'}](${meta.loop_url || '#'}) |\n`;
                }
                
                if (results.length > 50) {
                  body += `\n[View all ${results.length} findings](...)`;
                }
              }
            }
            
            body += '\n\n---\n> 🔁 [The Loop](https://loop.oute.pro) | [Report false positive](https://loop.oute.pro/feedback)';
            
            // Find existing comment
            const { data: comments } = await github.rest.issues.listComments({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
            });
            
            const existing = comments.find(c => c.body.includes('The Loop — Incident Guard'));
            
            if (existing) {
              await github.rest.issues.updateComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                comment_id: existing.id,
                body,
              });
            } else {
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.issue.number,
                body,
              });
            }

      # 6. Fail if errors
      - name: Fail on errors
        if: steps.semgrep.outputs.errors != '0'
        run: |
          echo "❌ ERROR findings detected — merge blocked"
          exit 1
```

### Key Points

- **Trigger**: `pull_request` on branches `main`, `master`, `develop`
- **Permissions**: Minimize to `contents: read` + `pull-requests: write`
- **Timeout**: 10-minute job timeout (hard limit)
- **Scan timeout**: 30-second wrapper with `timeout 30`
- **Exit behavior**: Fails job only if ERROR findings present
- **Comment**: Finds and updates existing comment (no duplicates)

---

## Step 3: Create Installation Guide (`THELOOP.md`)

### File Location
```
THELOOP.md  (at repo root)
```

### Content Template

```markdown
# The Loop — Incident Guard Installation (5 minutes)

## What is this?

The Loop analyzes your code on every PR and blocks patterns that have already caused production incidents.

## Installation

Copy 2 files to your repository:

1. **`.semgrep/theloop-rules.yml`** — Semgrep rules
2. **`.github/workflows/theloop-guard.yml`** — GitHub Actions workflow

That's it. On the next PR, the workflow runs automatically.

## Active Rules (Phase A: 0.1.0)

| Rule ID | Category | Pattern | Severity |
|---------|----------|---------|----------|
| `injection-001` | Injection | SQL via string concat | ERROR 🔴 |
| `injection-002` | Injection | `eval()` with dynamic input | ERROR 🔴 |
| `unsafe-api-usage-001` | Unsafe API | Shell commands with vars | ERROR 🔴 |
| `missing-safety-check-001` | Safety | Hardcoded secrets | ERROR 🔴 |
| `missing-error-handling-001` | Error Handling | Bare `except` | WARNING 🟡 |
| `unsafe-regex-001` | Regex | ReDoS patterns | WARNING 🟡 |

## How It Works

1. You open/update a PR
2. Workflow scans code with Semgrep
3. Findings appear in PR comment
4. ERROR findings block merge
5. WARNING findings are informational

## Troubleshooting

### Workflow doesn't run
- Check: Is `.github/workflows/theloop-guard.yml` in your repo?
- Check: Is the PR targeting `main`, `master`, or `develop`?

### Comment says "Rules file not found"
- Copy `.semgrep/theloop-rules.yml` to your repo
- Commit and push

### False positive reported
- Click [Report false positive](https://loop.oute.pro/feedback) in the PR comment

## Phase B Roadmap (coming later)

- Dynamic rule downloads via API
- New rules for new incident categories
- Rule refinement based on feedback
- Integration with incident details page

---

[The Loop](https://loop.oute.pro)
```

---

## Step 4: Test Locally

### Test Semgrep Rules

```bash
# Create test file with vulnerable code
cat > test_injection.py << 'EOF'
import sqlite3

def unsafe_query(user_input):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    # Vulnerable: SQL injection
    cursor.execute("SELECT * FROM users WHERE id = '" + user_input + "'")
    return cursor.fetchall()
EOF

# Run Semgrep
semgrep scan --config .semgrep/theloop-rules.yml test_injection.py --json

# Expected: rule injection-001 fires
```

### Test Workflow (Manual)

Push to test branch and open PR:

```bash
git checkout -b test/semgrep
git add .semgrep/theloop-rules.yml .github/workflows/theloop-guard.yml THELOOP.md
git commit -m "test: add semgrep workflow"
git push -u origin test/semgrep
# Open PR in GitHub; workflow runs automatically
```

---

## Step 5: Validate with Test Repository

The separate public test repository (`the-loop-tester`) contains intentionally vulnerable code for validation:

### Test Repo Structure

```
the-loop-tester/
├── bad/
│   ├── injection.py
│   ├── shell.py
│   ├── secrets.py
│   ├── error_handling.py
│   ├── regex_dos.py
│   └── eval_injection.py
├── good/
│   ├── injection_safe.py
│   ├── shell_safe.py
│   ├── secrets_safe.py
│   ├── error_handling_safe.py
│   ├── regex_dos_safe.py
│   └── eval_injection_safe.py
├── .semgrep/theloop-rules.yml
└── .github/workflows/theloop-guard.yml
```

### Validation Steps

1. **PR with vulnerable code** (add `bad/injection.py`):
   - Expected: 6 findings (injection-001, injection-002, etc.)
   - Merge: Blocked (ERROR findings)

2. **PR with fixed code** (add `good/injection_safe.py`):
   - Expected: 0 findings
   - Merge: Allowed

3. **PR update test** (push new commit to same PR):
   - Expected: Comment updated (not duplicated)

---

## Implementation Checklist

- [ ] Created `.semgrep/theloop-rules.yml` with 6 rules
- [ ] Validated rules with `semgrep --validate`
- [ ] Created `.github/workflows/theloop-guard.yml`
- [ ] Created `THELOOP.md` with installation guide
- [ ] Tested locally with vulnerable code sample
- [ ] Tested workflow on feature branch (open PR)
- [ ] Validated comment format and merge blocking behavior
- [ ] Tested comment update on subsequent commits
- [ ] Validated all 6 rules fire on test repository `bad/` code
- [ ] Validated zero rules fire on test repository `good/` code

---

## What's Next?

Once Phase A is validated:

1. **Phase B**: Add API endpoint for dynamic rule distribution
2. **Phase C**: Extend to new incident categories
3. **Phase D**: Integrate with incident detail pages + feedback loop

For now, Phase A rules are immutable and distributed via copy-paste.

---

## References

- [Semgrep Documentation](https://semgrep.dev/docs/)
- [Semgrep Pattern Syntax](https://semgrep.dev/docs/writing-rules/pattern-syntax/)
- [GitHub Actions Scripting](https://github.com/actions/github-script)
- [The Loop](https://loop.oute.pro)
