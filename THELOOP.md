# The Loop — Incident Guard Installation (5 minutes)

## What is this?

The Loop analyzes your code on every PR and **blocks patterns that have already caused production incidents**. This is Phase A: static analysis rules delivered via GitHub Actions.

## Installation (Copy 2 Files)

### Step 1: Copy rules file
```bash
mkdir -p .semgrep
curl -o .semgrep/theloop-rules.yml https://raw.githubusercontent.com/renatobardi/the-loop/main/.semgrep/theloop-rules.yml
```

Or manually copy from [.semgrep/theloop-rules.yml](https://github.com/renatobardi/the-loop/blob/main/.semgrep/theloop-rules.yml)

### Step 2: Copy workflow
```bash
mkdir -p .github/workflows
curl -o .github/workflows/theloop-guard.yml https://raw.githubusercontent.com/renatobardi/the-loop/main/.github/workflows/theloop-guard.yml
```

Or manually copy from [.github/workflows/theloop-guard.yml](https://github.com/renatobardi/the-loop/blob/main/.github/workflows/theloop-guard.yml)

### Step 3: Commit & Push
```bash
git add .semgrep/theloop-rules.yml .github/workflows/theloop-guard.yml
git commit -m "security: add The Loop incident guard"
git push
```

### Step 4: Open a PR
The workflow will run automatically on your next PR.

---

## What Gets Scanned?

| Rule ID | Category | Pattern Detected | Severity |
|---------|----------|------------------|----------|
| `injection-001` | Injection | SQL concatenation | 🔴 ERROR |
| `injection-002` | Injection | `eval()` with user input | 🔴 ERROR |
| `unsafe-api-usage-001` | Unsafe API | `os.system()` / `subprocess shell=True` | 🔴 ERROR |
| `missing-safety-check-001` | Safety | Hardcoded credentials | 🔴 ERROR |
| `missing-error-handling-001` | Error Handling | Bare `except:` blocks | 🟡 WARNING |
| `unsafe-regex-001` | Regex | ReDoS patterns (backtracking) | 🟡 WARNING |

---

## What Happens When Scan Finds Issues?

### 🔴 ERROR Findings (5 rules)
- PR comment shows **which** rules were violated
- Each finding includes:
  - **Incident ID** (e.g., `injection-001`)
  - **Remediation instructions** (how to fix)
  - **Link to incident** (why it matters)
- **Merge is BLOCKED** until all ERROR findings are fixed

### 🟡 WARNING Findings (1 rule)
- PR comment shows findings
- **Merge is ALLOWED** (informational only)
- Developer can choose to fix or merge

### ✅ Clean PRs
- Workflow shows: `✅ No incident patterns detected`
- Merge is allowed

---

## Troubleshooting

### Workflow doesn't run
**Check**: Is the PR targeting `main`, `master`, or `develop` branch?
**Check**: Are both `.semgrep/theloop-rules.yml` and `.github/workflows/theloop-guard.yml` in your repo?

### Error: "Rules file not found"
**Fix**: Copy `.semgrep/theloop-rules.yml` to your repository and push.

### Error: "Invalid YAML in rules"
**Check**: The rules file is malformed. Download a fresh copy from The Loop.

### GitHub API failure (comment didn't post)
**Don't worry**: The scan still ran. Results are in the workflow summary.
**Retry**: Push a new commit to re-run the workflow.

### False positive (rule fires on safe code)
**Report it**: [Feedback form](https://loop.oute.pro/feedback)
**Exclude it**: Add patterns to `.semgrep/theloop-rules.yml` paths → exclude section

---

## Performance

- **Typical scan time**: < 10 seconds
- **Hard timeout**: 30 seconds (for very large repos)
- **Finding cap**: Top 50 shown in comment, full report in workflow artifacts

---

## Phase B Roadmap (Coming Later)

- **API endpoint**: Automatic rule updates
- **Feedback loop**: Rules refined based on false positive reports
- **Dashboard**: View all incidents detected across your org
- **Incident linking**: PR comments link directly to incident details

---

## References

- [The Loop](https://loop.oute.pro) — Incident database
- [Semgrep](https://semgrep.dev) — Pattern matching engine
- [GitHub Actions](https://github.com/features/actions) — CI/CD
- [Report false positive](https://loop.oute.pro/feedback) — Feedback form

---

**Questions?** Open an issue: [renatobardi/the-loop/issues](https://github.com/renatobardi/the-loop/issues)
