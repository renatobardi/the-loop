# Research Phase 0: GitHub + Semgrep Integration

**Created**: 2026-04-03  
**Feature**: GitHub + Semgrep Integration — Phase A  
**Scope**: Resolve technical ambiguities and validate architecture before Phase 1 design

---

## R1: Semgrep Rule Syntax & Multilingual Patterns

### Decision
Use Semgrep YAML syntax with `pattern-either`, `pattern-regex`, and `pattern-not` for rule definition. Multilingual rules use `languages: [python, javascript, ...]` field.

### Rationale
- Semgrep is the de facto open-source SAST tool (widely adopted, actively maintained)
- YAML syntax is human-readable and version-control friendly
- Pattern matching supports both literal patterns (for language-specific APIs) and regex (for string patterns like secrets)
- Metadata field supports arbitrary key-value pairs (incident_id, loop_url, remediation)

### Validation
- **Rule syntax**: Semgrep CLI validates via `semgrep --validate --config` before scan
- **Pattern accuracy**: Test repository (`bad/` directory) validates that all 6 rules correctly identify vulnerable code
- **False positives**: `pattern-not` clauses and path exclusions reduce noise (e.g., exclude `*.test.*` for secret detection)

### Alternatives Considered
- **AST-based pattern matching** (e.g., tree-sitter) — rejected: requires language-specific rule definitions; YAML + pattern matching is simpler for MVP
- **Regex-only rules** — rejected: insufficient for context-aware checks (e.g., distinguishing `os.system("cmd")` from `os.system(["cmd"])`)
- **Rules from third-party SaaS (Semgrep Cloud)** — rejected: violates Phase A constraint (no external API dependency)

---

## R2: GitHub Actions Workflow Integration

### Decision
Use GitHub Actions `github-script@v7` action with JavaScript to:
1. Parse Semgrep JSON output
2. Format findings into Markdown table
3. Find and update existing PR comment (avoid duplicates)
4. Post comment only if findings exist
5. Set workflow status check based on ERROR count

### Rationale
- `github-script` is the standard GitHub-maintained way to interact with GitHub API (Octokit)
- Avoids additional dependencies (no need for GitHub CLI in workflow)
- Node.js is pre-installed in GitHub Actions runners
- Octokit handles pagination, rate limits, and retries automatically

### Validation
- **Workflow execution**: Runs on `pull_request` events (opened, synchronize, reopened)
- **Comment management**: Tests verify comment is updated (not duplicated) on subsequent commits
- **Status check**: GitHub merges are blocked only if status check fails (ERROR findings present)

### Alternatives Considered
- **GitHub CLI (`gh`) inside workflow** — rejected: requires installation; `github-script` is built-in
- **Posting comment via curl + raw GitHub API calls** — rejected: manual error handling, no built-in retry logic
- **Using third-party Semgrep action (marketplace)** — rejected: reduces control; custom workflow easier to debug and maintain

---

## R3: Handling GitHub API Failures

### Decision
GitHub API failures (posting/updating comment) are **non-blocking**: logged but do not fail the job. Only Semgrep scan failures block the job.

### Rationale
- **Resilience**: Scan results are actionable even if comment post fails (findings are logged to workflow summary)
- **Pragmatism**: Transient API failures (throttling, temporary outages) should not block PR merge indefinitely
- **Degradation**: If comment fails, developer can still see scan results in workflow logs/artifacts
- **Spec alignment**: SC-008 requirement (PR comment displays findings) is best-effort; errors are logged

### Implementation
```javascript
try {
  await github.rest.issues.updateComment(...);
} catch (error) {
  console.log(`[WARN] Failed to update comment: ${error.message}`);
  // Workflow continues; does NOT exit with error
}
```

### Validation
- Unit tests mock GitHub API failures and verify workflow continues
- Integration tests verify comment is created/updated when API succeeds
- Workflow logs document any API failures for troubleshooting

---

## R4: Finding Pagination & Comment Size Management

### Decision
PR comment displays **up to 50 findings** in a Markdown table, with a link to the complete report in the GitHub Actions workflow summary if more findings exist.

### Rationale
- **Comment readability**: GitHub PR comments have practical size limits; 50 findings is actionable without overwhelming
- **Developer experience**: First 50 violations are highest-priority (typically most severe or first encountered)
- **Compliance with SC-008**: "Sufficient for developer to fix 90% of reported issues" — top 50 covers most projects
- **Full visibility**: Complete report remains accessible in workflow artifacts for auditing or CI/CD integration

### Implementation
```javascript
const sortedResults = results.sort((a, b) => 
  (severityLevel[b.extra.severity] || 0) - (severityLevel[a.extra.severity] || 0)
);
const displayResults = sortedResults.slice(0, 50);
if (results.length > 50) {
  comment += `\n[View all ${results.length} findings in workflow summary](${workflowUrl})`;
}
```

### Validation
- Test repository generates PR with 100+ findings; workflow caps comment at 50 + adds link
- PR comment renders correctly in GitHub UI

---

## R5: Rule Immutability & Versioning

### Decision
Rules are **immutable** in Phase A. Projects copy `.semgrep/theloop-rules.yml` explicitly; automatic updates deferred to Phase B.

### Rationale
- **Predictability**: Projects know their rules won't change unless they update the file
- **Traceability**: Each copy of the rules is pinned to a version (included in YAML comment)
- **Simplicity**: MVP avoids complexity of rule versioning, deprecation, and API-driven updates
- **Upgrade path**: Phase B will add API endpoint to fetch latest rules; Phase A projects can opt in

### Implementation
- Rules file includes version comment: `# Versão: 0.1.0 (static — Fase A)`
- `THELOOP.md` documents upgrade process (copy-paste new file)
- No automatic rule fetching in Phase A

### Validation
- Spec clarification Q1 confirmed immutability approach
- No version-checking logic in workflow (Phase A scope)

---

## R6: False Positive Feedback Routing

### Decision
PR comment includes link: **"Report false positive"** → `https://loop.oute.pro/feedback`

### Rationale
- **Centralized feedback**: All false positive reports flow to The Loop team
- **Phase B preparation**: Feedback informs rule refinement and accuracy improvements
- **User empowerment**: Developers can easily report issues without filing GitHub issues
- **Web form backend**: Email-based collection (simple, no additional infrastructure in Phase A)

### Implementation
```markdown
> 🔁 [The Loop](https://loop.oute.pro) | 
> [Reportar falso positivo](https://loop.oute.pro/feedback) | 
> Versão das regras: `0.1.0-static`
```

### Validation
- Spec clarification Q3 confirmed feedback routing
- Link is present in all PR comments
- Form at loop.oute.pro is live (or placeholder for Phase A)

---

## R7: Semgrep Scan Timeout Strategy

### Decision
- **Target**: < 10 seconds per scan (user sees results in one comment cycle)
- **Warning threshold**: If scan exceeds 10 seconds, emit warning to logs
- **Hard timeout**: 30 seconds with partial results reported
- **Rationale**: Large repos may exceed target; hard timeout prevents workflow from hanging indefinitely

### Implementation
```yaml
# Workflow step timeout
timeout-minutes: 10  # GitHub Actions job-level timeout

# Semgrep command with timeout wrapper (bash)
timeout 30 semgrep scan ... || TIMEOUT_EXIT=$?
if [ $TIMEOUT_EXIT -eq 124 ]; then
  echo "[WARN] Semgrep scan exceeded 30s; partial results reported"
fi
```

### Validation
- Spec clarification Q4 confirmed timeout approach
- Test repository validates scan completes within target on representative repo size
- Timeout handling tested in integration environment

---

## R8: Rule Accuracy Validation (Test Repository)

### Decision
Test repository (`the-loop-tester`) contains:
- **`bad/` directory**: 6 Python files with intentional vulnerabilities matching each rule
- **`good/` directory**: 6 corrected versions of each file
- **Workflow**: PR opens against test repo; workflow scans and reports
- **Validation**: 
  - PR with `bad/` code → expects exactly 6 findings (5 ERROR, 1 WARNING bare except, 1 WARNING regex)
  - PR with `good/` code → expects 0 findings
  - Comment updates on subsequent commits (no duplicate comments)

### Rationale
- **End-to-end validation**: Confirms rules work in real GitHub Actions environment
- **Regression prevention**: Test repo catches rule accuracy drift
- **CI integration**: Test PRs are automated; can be re-run on any rule update

### Validation
- Test repository rules match production rules exactly
- Test runs before Phase A release; all scenarios pass

---

## Research Summary

All core technical decisions for Phase A are now resolved:

| Decision | Status | Next Phase |
|----------|--------|-----------|
| Semgrep rule syntax & multilingual patterns | ✅ RESOLVED | Phase 1 design rules schema |
| GitHub Actions workflow architecture | ✅ RESOLVED | Phase 1 design workflow contract |
| GitHub API failure handling (non-blocking) | ✅ RESOLVED | Phase 1 implement error handling |
| Finding pagination & comment size | ✅ RESOLVED | Phase 1 implement comment formatting |
| Rule immutability & versioning | ✅ RESOLVED | Phase 1 document upgrade path |
| False positive feedback routing | ✅ RESOLVED | Phase 1 add feedback link to comments |
| Semgrep scan timeout strategy | ✅ RESOLVED | Phase 1 implement timeout wrapper |
| Rule accuracy validation via test repo | ✅ RESOLVED | Phase 2 tasks create test repo + PRs |

---

## No External Dependencies for Phase A

- ✅ Semgrep CLI (open-source, installed via pip)
- ✅ GitHub Actions (built-in, no subscription required)
- ✅ Node.js + Octokit (pre-installed in GH Actions runners)
- ✅ Python (assumed available in target projects)
- ✅ No external APIs, databases, or SaaS services

Conclusion: Phase A is self-contained and ready for Phase 1 design.
