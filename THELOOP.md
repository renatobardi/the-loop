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

## Rules (20 Total: Phase A Base + Phase B Extended)

### Phase A — 6 Base Rules (v0.1.0)

| Rule | Pattern | Severity | Language |
|------|---------|----------|----------|
| **injection-001** | SQL concatenation (`"SELECT * FROM users WHERE id = '" + user_id + "'"`) | ERROR | All |
| **injection-002** | `eval()` with user input | ERROR | Python, JS, Ruby |
| **unsafe-api-usage-001** | `subprocess.call(shell=True)` with variable | ERROR | Python |
| **missing-safety-check-001** | Hardcoded credentials/passwords | ERROR | All |
| **missing-error-handling-001** | Bare `except:` blocks (swallow errors silently) | WARNING | Python |
| **unsafe-regex-001** | ReDoS patterns (catastrophic backtracking) | WARNING | All |

### Phase B — 14 New Rules (v0.2.0)

| Category | Rules | Severity |
|----------|-------|----------|
| **Injection** | path-traversal, XXE, unsafe deserialization | ERROR ×3 |
| **Crypto** | weak MD5, weak random | WARNING ×2 |
| **Security** | TLS verify disabled, hardcoded JWT secret, CORS wildcard | ERROR ×2, WARNING ×1 |
| **Performance** | SQL without timeout, N+1 queries | WARNING ×2 |
| **Infrastructure** | Docker runs as root | WARNING ×1 |
| **Config** | Hardcoded URLs, DEBUG enabled | WARNING ×2 |
| **Dependencies** | Known vulnerable dependency | WARNING ×1 |

**Total**: 20 rules (8 ERROR, 12 WARNING) covering 11 categories

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

## Phase B — Versioned Rules API (Live)

Phase B enables live rule updates without redeploying dependent projects:

**Features** (All Live):
- ✅ Semantic versioning (v0.1.0, v0.2.0) with rollback support
- ✅ 14 new rules (Phase B) across 7 categories
- ✅ Deprecation lifecycle (draft → active → deprecated)
- ✅ Automatic fallback to Phase A if API unavailable
- ✅ Version pinning via environment variable

**How It Works**:

The workflow fetches rules from the API with intelligent fallback:

```bash
# Fetch latest or pinned version (5s timeout)
curl -s --max-time 5 \
  -H "Authorization: Bearer $THELOOP_API_TOKEN" \
  "https://theloop-api-1090621437043.us-central1.run.app/api/v1/rules/${VERSION}" \
  -o /tmp/rules.json

# On timeout/error: fallback to Phase A backup (guaranteed safety)
if [ $? -ne 0 ]; then
  cp .semgrep/theloop-rules.yml.bak /tmp/rules.json
fi

# Convert JSON → YAML and run Semgrep
python3 scripts/json_to_semgrep_yaml.py --input /tmp/rules.json --output .semgrep/theloop-rules.yml
semgrep scan --config .semgrep/theloop-rules.yml --json --output results.json
```

**Version Pinning**:
```bash
# Use specific version instead of latest
export THELOOP_RULES_VERSION=0.1.0    # Phase A only
export THELOOP_RULES_VERSION=0.2.0    # Phase B (14 new rules)
```

**Rollback (If Needed)**:
If a new version has issues:
1. API marks version as deprecated: `POST /api/v1/rules/deprecate?version=0.2.0`
2. Workflow automatically fallbacks to Phase A (v0.1.0)
3. No code changes or redeploy needed — automatic on next PR

---

## Troubleshooting

**🔴 Workflow fails at "Fetch rules from API"**
- Error: Timeout or 401 Unauthorized
- Fix: Check `THELOOP_API_TOKEN` secret is set in GitHub Actions settings
- Fallback: Workflow automatically uses Phase A backup rules (`.semgrep/theloop-rules.yml.bak`)

**🔴 Workflow fails at "Convert JSON to YAML"**
- Error: Script not found or permission denied
- Fix: Ensure `scripts/json_to_semgrep_yaml.py` is in your repo root
- Check: `git ls-files scripts/json_to_semgrep_yaml.py` returns the file path

**🟡 Semgrep finds false positives on safe code**
- Example: WARNING on `cursor.execute(query, timeout=30)` but has timeout
- Reason: Some rules may flag patterns without checking all variations
- Fix: Add `# nosemgrep` comment above line (not recommended) or report at https://loop.oute.pro/feedback
- Better: Update rule via API (Phase B) to exclude safe patterns

**🟡 "Critical findings detected" but code looks safe**
- Review the rule metadata in PR comment (click incident link)
- Check if there's actual vulnerability or false positive
- Report at https://loop.oute.pro/feedback with code example

**❓ How to temporarily skip the scan?**
- Add to commit message: `[skip ci]` — skips entire workflow
- Add to code: `# nosemgrep` above line — skips single rule on that line
- Neither recommended — better to fix the underlying issue

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
