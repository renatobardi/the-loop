# The Loop — Installation & Usage

Convert production incidents into code guardrails. Rules layer provides static pattern detection.

## What Is This?

GitHub Actions workflow that scans every PR for patterns that previously caused production incidents. Rules are distributed via:
- **Phase A (Static)**: Immutable rule file (`.semgrep/theloop-rules.yml`)
- **Phase B (API)**: Versioned rules API with live updates (Phase B deployment)

When a PR opens:
1. Checkout code
2. Fetch latest rules (Phase B: from API; Phase A: static file)
3. Run Semgrep with The Loop rules
4. Comment on PR with findings
5. Block merge if ERROR-severity findings

## Install in Your Project

```bash
# 1. Copy rules to your repo
cp .semgrep/theloop-rules.yml YOUR_PROJECT/.semgrep/theloop-rules.yml

# 2. Copy workflow to your repo
cp .github/workflows/theloop-guard.yml YOUR_PROJECT/.github/workflows/theloop-guard.yml

# 3. Commit & push
git add .semgrep .github
git commit -m "chore: add The Loop incident guard"
git push origin feature-branch

# 4. Open PR — workflow runs automatically!
```

## Rules (6 Static Rules)

| Rule | Pattern | Severity | Language |
|------|---------|----------|----------|
| **injection-001** | SQL concatenation (`"SELECT * FROM users WHERE id = '" + user_id + "'"`) | ERROR | All |
| **injection-002** | `eval()` with user input | ERROR | Python, JS, Ruby |
| **unsafe-api-usage-001** | `subprocess.call(shell=True)` with variable | ERROR | Python |
| **missing-safety-check-001** | Hardcoded credentials/passwords | ERROR | All |
| **missing-error-handling-001** | Bare `except:` blocks (swallow errors silently) | WARNING | Python |
| **unsafe-regex-001** | ReDoS patterns (catastrophic backtracking) | WARNING | All |

## Understanding Findings

### 🔴 ERROR Findings → Merge Blocked

These are critical patterns linked to production incidents. Fix before merge:

```
❌ injection-001: SQL concatenation at app.py:42
   Fix: Use parameterized queries — cursor.execute(query, (user_id,))

❌ missing-safety-check-001: Hardcoded API key at config.py:7
   Fix: Use os.environ.get('API_KEY') + secrets manager
```

### 🟡 WARNING Findings → Informational

Review and fix when possible (doesn't block merge):

```
⚠️  missing-error-handling-001: Bare except at utils.py:15
   Review: Specify exception type + add logging

⚠️  unsafe-regex-001: ReDoS pattern at validator.py:8
   Review: Rewrite regex without nested quantifiers
```

## Contact

- **Email**: loop@oute.pro
- **GitHub**: https://github.com/renatobardi/the-loop
- **Feedback**: Report false positives or missing patterns

## Next Steps

1. ✅ Install (copy 2 files, push)
2. 📋 Open PR — workflow scans automatically
3. 🔍 Review findings in PR comment
4. 🔧 Fix or acknowledge (if warning-only)
5. ✅ Merge when ready

## Phase B — Versioned Rules API (Coming Soon)

Phase B enables live rule updates without redeploying dependent projects:

**Benefits**:
- Semantic versioning (v0.1.0, v0.2.0, ...) with rollback support
- Rules update immediately across all projects
- Deprecation lifecycle (draft → active → deprecated)
- Admin control via Firebase authentication

**Workflow Integration (Phase B)**:
```yaml
- name: Fetch latest rules from The Loop API
  run: |
    curl -s https://theloop-api.run.app/api/v1/rules/latest \
      --max-time 5 \
      -o rules.json || {
        echo "API unavailable, using Phase A backup"
        cp .semgrep/theloop-rules.yml.bak rules.json
      }

- name: Run Semgrep scan
  run: semgrep scan --config rules.json --json --output results.json
```

**Fallback**: If API is unavailable (>5s timeout), uses local `.semgrep/theloop-rules.yml.bak` (Phase A backup).

---

## FAQ

**Q: Why block on ERROR but not WARNING?**
A: ERROR patterns caused production incidents; WARNING patterns need review but may have context.

**Q: Can I disable a rule?**
A: Phase A: Edit `.semgrep/theloop-rules.yml` and remove the rule block. Phase B: Contact @renatobardi for admin publish control.

**Q: What if I get a false positive?**
A: Report at https://loop.oute.pro/feedback — helps improve rules.

**Q: How often are rules updated?**
A: Phase A: manually (static file). Phase B: real-time via API (with deprecation timeline).

**Q: What's the difference between Phase A and Phase B?**
A: Phase A uses static rules file (stable, immutable). Phase B uses versioned API (live updates, rollback support).

---

🔁 The Loop — Every incident teaches. Every fix prevents.
