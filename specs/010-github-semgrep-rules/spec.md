# Feature Specification: GitHub + Semgrep Integration — Fase A (Static Rules)

**Feature Branch**: `010-github-semgrep-rules`  
**Created**: 2026-04-03  
**Status**: Draft  
**Phase**: A — Static Rules (MVP, pre-API)

---

## User Scenarios & Testing

### User Story 1 - Security Team Distributes Incident-Derived Rules (Priority: P1)

A security team at The Loop wants to package static analysis rules derived from their incident database into a reusable GitHub Actions workflow. These rules should be easy to copy into any project, immediately preventing the same security patterns that caused past incidents.

**Why this priority**: This is the core use case — converting hard-learned lessons from production incidents into preventive code guardrails. Every organization needs this.

**Independent Test**: Can be fully tested by setting up the rules file and workflow in a test repository, opening a PR with vulnerable code, and confirming the workflow blocks the PR with detailed findings about which incident patterns were detected.

**Acceptance Scenarios**:

1. **Given** a project has no Semgrep rules configured, **When** a developer copies `.semgrep/theloop-rules.yml` and `.github/workflows/theloop-guard.yml` to their repo, **Then** the first PR automatically runs the guard workflow and comments with findings
2. **Given** a PR contains code matching an incident pattern, **When** the workflow scans, **Then** the PR comment displays a table showing severity, rule ID, file, line, and links to incident details
3. **Given** a PR contains multiple vulnerabilities, **When** the workflow reports findings, **Then** ERROR-severity issues block merge while WARNING-severity issues only inform

---

### User Story 2 - Developer Fixes Security Issues Guided by Incident Context (Priority: P1)

A developer receives feedback on their PR that they've introduced a pattern from a documented incident. They click a link to the incident in The Loop, understand why it's dangerous, read the remediation steps, and fix the code.

**Why this priority**: The entire value prop depends on developers being able to act on the feedback. Without clear remediation context, the tool becomes noise.

**Independent Test**: Can be fully tested by verifying that each finding in the PR comment includes incident ID, severity level, remediation instructions, and a working link to incident details (even if link is placeholder for Phase A).

**Acceptance Scenarios**:

1. **Given** a PR finding with incident ID `injection-001`, **When** the developer reads the PR comment, **Then** they see the message "[incident-id]: [remediation instructions]"
2. **Given** a developer searches for remediation info, **When** they click the incident link, **Then** they navigate to incident details (Phase A: link is placeholder to loop.oute.pro)
3. **Given** a developer has fixed the issue, **When** they push new commits, **Then** the PR comment updates (not duplicated) with new scan results

---

### User Story 3 - Project Lead Prevents Regressions at Scale (Priority: P2)

A project lead enables The Loop guard on their team's main repository. They can now be confident that entire categories of incidents cannot be reintroduced — the rules catch them before merge, consistently, without human review overhead.

**Why this priority**: Once deployed, this scales enforcement without additional effort. It's force-multiplier for security.

**Independent Test**: Can be fully tested by running the workflow on multiple scenarios (PR with vulnerabilities, PR clean, PR with warnings) and confirming blocking/commenting behavior is consistent.

**Acceptance Scenarios**:

1. **Given** a workflow runs on a PR with 3 ERROR-severity findings, **When** the merge button is clicked, **Then** GitHub blocks the merge due to failed status check
2. **Given** a workflow runs on a PR with only WARNING findings, **When** the merge button is available, **Then** the developer can merge without fixing (unless branch protection requires status check pass)
3. **Given** repeated PRs, **When** no vulnerable code patterns exist, **Then** the workflow passes cleanly with a green checkmark and one-line confirmation

---

### User Story 4 - Test Repository Validates All Rules End-to-End (Priority: P2)

A test repository (`the-loop-tester`) contains intentionally vulnerable code (`bad/` directory) and fixed code (`good/` directory). When PRs are opened against this repo, they verify that:
- All 6 rules fire on vulnerable code
- No rules fire on fixed code
- The workflow integrates correctly with GitHub's PR system

**Why this priority**: Without validation infrastructure, we can't be confident that deployed rules actually work in the field.

**Independent Test**: Can be fully tested by running the workflow against both `bad/` and `good/` directories and confirming rule matches are accurate.

**Acceptance Scenarios**:

1. **Given** a PR adding files to `bad/` directory, **When** workflow scans, **Then** exactly 6 findings are reported (5 ERROR, 1 WARNING for bare except, 1 WARNING for regex)
2. **Given** a PR with only `good/` directory code, **When** workflow completes, **Then** zero findings reported and PR comment shows ✅ clean status
3. **Given** the workflow comments on test PRs, **When** the same PR is updated, **Then** the existing comment is updated (not duplicated)

---

### Edge Cases

- What happens when a user has `.semgrep/theloop-rules.yml` but it's malformed YAML? → Workflow should fail with validation error message
- What happens if a rule matches legitimate code that's not actually vulnerable? → Developer sees "Report false positive" link in comment pointing to `https://loop.oute.pro/feedback` web form; feedback is centrally collected and reviewed by The Loop team for Phase B rule refinement
- What happens if the test repo's `bad/` code evolves but rules aren't updated? → Rules file becomes stale; Phase B will automate updates via API
- What happens if Semgrep scan exceeds 10 seconds? → Workflow continues with warning in log and partial results reported; hard timeout at 30 seconds ensures scan doesn't block indefinitely on large repos
- What happens if Semgrep finds 100+ violations? → PR comment displays top 50 findings with link to complete report in workflow summary; prevents overwhelming developers while maintaining access to full results

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a Semgrep rules file (`.semgrep/theloop-rules.yml`) containing exactly 6 rules derived from incident patterns
  - `injection-001`: SQL injection via string concatenation
  - `injection-002`: `eval()` with dynamic input
  - `unsafe-api-usage-001`: Shell commands with variables
  - `missing-safety-check-001`: Hardcoded secrets/credentials
  - `missing-error-handling-001`: Bare `except` without logging
  - `unsafe-regex-001`: ReDoS-vulnerable regex patterns

- **FR-002**: Each rule MUST include metadata with `incident_id`, `category`, `loop_url`, and `remediation_instructions` for display in PR comments

- **FR-003**: System MUST provide a GitHub Actions workflow (`.github/workflows/theloop-guard.yml`) that automatically runs on pull requests to `main`/`master`/`develop` branches

- **FR-004**: The workflow MUST execute Semgrep scan against the rules file and collect results in JSON format; scan MUST timeout after 30 seconds with partial results reported; workflow MUST emit warning if scan exceeds 10 seconds

- **FR-005**: The workflow MUST comment on the PR with a formatted table showing severity, rule ID, file path, line number, and incident ID with link; findings MUST be capped at 50 in the comment, with a link to the complete report in the workflow summary if more findings exist; if GitHub API call fails, the failure MUST be logged but MUST NOT block the job

- **FR-006**: The workflow MUST fail the job (block merge) if any ERROR-severity findings exist; WARNING findings do not block merge

- **FR-007**: If the workflow previously commented on a PR, it MUST update the existing comment rather than creating duplicates when the PR is updated or commits are pushed; comment update failures MUST be logged but MUST NOT block the job

- **FR-008**: The workflow MUST validate that `.semgrep/theloop-rules.yml` exists before scanning; if missing, it MUST display an error message with installation instructions

- **FR-009**: System MUST provide a test repository (`the-loop-tester`) with `bad/` and `good/` directories containing vulnerable and corrected code respectively

- **FR-010**: System MUST provide installation documentation (`THELOOP.md`) explaining installation steps, rule severity levels, active rules, and Phase B roadmap

- **FR-011**: Rules MUST exclude files matching patterns (tests, examples, `.env.example`) from certain checks (e.g., secret detection)

- **FR-012**: System MUST NOT depend on external services (Semgrep Cloud, third-party APIs) for Phase A

- **FR-013**: Each PR comment MUST include a "Report false positive" link pointing to `https://loop.oute.pro/feedback` web form; feedback is centrally collected and reviewed by The Loop team for Phase B rule refinement

---

### Key Entities

- **Semgrep Rule**: A pattern matcher derived from an incident category, with metadata linking to incident details, severity level, and remediation instructions
- **GitHub Actions Workflow**: Automated execution that runs Semgrep on PR code and reports findings as PR comment with status check integration
- **Test Repository**: Mirror of integration points with intentionally vulnerable and corrected code to validate rule accuracy and workflow behavior
- **Incident Context**: Reference to original incident (category, ID, remediation) embedded in rule metadata to guide developer fixes

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: All 6 rules correctly identify vulnerable code patterns in the `bad/` test directory (100% detection rate on target patterns)

- **SC-002**: No rules fire on corrected code in the `good/` test directory (0% false positive rate on safe patterns)

- **SC-003**: Rules MUST NOT fire on intentional examples in documentation files (`.env.example`, `*.test.*`, `test_*` directories excluded)

- **SC-004**: Workflow execution targets under 10 seconds per PR scan (user sees feedback within one comment cycle); hard timeout at 30 seconds with partial results and warning if exceeded

- **SC-005**: GitHub Actions status check integration works correctly: ERROR findings block merge, WARNING findings only inform

- **SC-006**: PR comment updates occur on subsequent commits without duplication (existing comment is modified, not new comment added)

- **SC-007**: Installation is completable in under 5 minutes by copying 2 files to 2 paths

- **SC-008**: Remediation instructions provided in PR comment are sufficient for developer to fix 90% of reported issues without external resources

- **SC-009**: End-to-end workflow validation in test repository passes (test PRs with `bad/` code fail with 6 findings, test PRs with `good/` code pass cleanly)

---

## Assumptions

- **Scope**: Phase A delivers static rules only; dynamic rule download from API is Phase B
- **Semgrep CLI**: Projects must have Python/pip available to install `semgrep` package; no Docker requirement for MVP
- **GitHub Ecosystem**: Target projects use GitHub Actions (not GitLab CI, Jenkins, etc.) for CI/CD
- **Incident Data**: 6 selected incident categories cover the most universal and multilanguage security patterns; framework-specific rules are out of scope for Phase A
- **Rule Accuracy**: Rules are tuned for precision over recall; some edge cases may require future refinement based on false positive feedback
- **Incident Links**: In Phase A, incident links point to placeholder URLs; Phase B will link to actual incident details UI
- **No API Dependency**: Workflow is fully self-contained; no authentication or API calls required for Phase A
- **Deployment Target**: Reusable files are distributed via GitHub copy-paste; no package registry in Phase A
- **Testing Environment**: Test repository (`the-loop-tester`) is a separate public GitHub repo used for validation
- **Rule Immutability**: Rules are immutable once delivered in Phase A; projects update by copying an entirely new version of `.semgrep/theloop-rules.yml` from The Loop, ensuring predictable behavior and avoiding breaking changes mid-release

---

## Clarifications

### Session 2026-04-03

- Q1: Should rules in Phase A be immutable or auto-updateable? → A: Rules are immutable; projects copy new versions explicitly. Defers upgrade complexity to Phase B.
- Q2: How should the workflow handle GitHub API failures when posting/updating comments? → A: GitHub API failures are logged but non-blocking; only Semgrep scan failures block the job. Ensures scan always runs and catches vulns, while API transients don't permanently block PRs.
- Q3: Where should false positive feedback be collected and reviewed? → A: Web form at loop.oute.pro (email-based backend). Centralizes feedback with The Loop team where incident database lives; deferred feedback informs Phase B rule improvements.
- Q4: How should the workflow handle scans that exceed 10-second target? → A: 30-second hard timeout with warning if >10 seconds. Partial results reported if timeout reached. Pragmatic for MVP; respects large repos; clear growth path for Phase B optimization.
- Q5: How should the workflow handle PRs with many findings (50+)? → A: Cap findings at 50 in PR comment with link to complete report in workflow summary. Prevents comment bloat; ensures actionable feedback (top 50 violations); satisfies SC-008 intent; full visibility available if needed.
