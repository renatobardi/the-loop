# The Loop — Installation (5 Minutes)

Convert production incidents into code guardrails. Static rules layer (Phase A).

## What Is This?

GitHub Actions workflow that scans every PR for patterns that previously caused production incidents.

When a PR opens:
1. Checkout code
2. Run Semgrep with The Loop rules
3. Comment on PR with findings
4. Block merge if ERROR-severity findings

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

## FAQ

**Q: Why block on ERROR but not WARNING?**
A: ERROR patterns caused production incidents; WARNING patterns need review but may have context.

**Q: Can I disable a rule?**
A: Edit `.semgrep/theloop-rules.yml` and remove the rule block, then commit locally.

**Q: What if I get a false positive?**
A: Report at https://loop.oute.pro/feedback — helps improve rules.

---

🔁 The Loop — Every incident teaches. Every fix prevents.
