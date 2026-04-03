# Implementation Plan: GitHub + Semgrep Integration — Phase A (Static Rules)

**Branch**: `010-github-semgrep-rules` | **Date**: 2026-04-03 | **Spec**: `specs/010-github-semgrep-rules/spec.md`
**Input**: Feature specification from `/specs/010-github-semgrep-rules/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver a reusable GitHub Actions workflow + Semgrep rules distribution system (Phase A MVP) that allows any GitHub project to scan PRs for security patterns derived from incident database. Six rules cover injection, unsafe API usage, hardcoded secrets, missing error handling, and ReDoS. Workflow integrates with GitHub PR system (comments with findings, blocks merge on ERROR-severity issues). Test repository validates rule accuracy end-to-end. No external APIs or Semgrep Cloud required in Phase A.

## Technical Context

**Language/Version**: YAML (Semgrep rules), Bash/JavaScript (GitHub Actions workflow), Python 3.9+ (Semgrep CLI), Markdown (docs)  
**Primary Dependencies**: Semgrep 1.45.0+ (open-source CLI), GitHub Actions (GH scripting), jq (JSON parsing in workflow)  
**Storage**: N/A (rules distributed via repo copy-paste; no centralized DB in Phase A)  
**Testing**: Test repository (`the-loop-tester`) with intentionally vulnerable code in `bad/` directory; pytest for CI validation  
**Target Platform**: GitHub (any project with Python/pip or Docker available; works cross-OS via CI)  
**Project Type**: Static analysis rules distribution + GitHub Actions automation (MVP, no API)  
**Performance Goals**: Scan execution under 10 seconds per PR (target); hard timeout 30 seconds with partial results and warning if exceeded  
**Constraints**: 30-second job timeout; findings capped at 50 in PR comment (link to full report if more); rules must be language-agnostic or multilingual (generic/Python/JS)  
**Scale/Scope**: 6 incident-derived rules; 3 deliverable files (`.semgrep/theloop-rules.yml`, `.github/workflows/theloop-guard.yml`, `THELOOP.md`); 2 test repositories (source + validator)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Mandamento | Status | Notes |
|---|---|---|
| **I. Trunk-Based Development** | ✅ PASS | Feature branch `010-github-semgrep-rules` + PR merge to `main` required; no direct push to main |
| **II. Design System** | ⊘ N/A | Not a UI feature; does not consume design tokens |
| **III. Branch Taxonomy** | ✅ PASS | Branch name `010-github-semgrep-rules` follows spec prefix convention (numeric + kebab-case) |
| **IV. Main Protected** | ✅ PASS | PR + approval + CI status checks + signed commits required before merge |
| **V. Merge by @renatobardi** | ✅ PASS | Only @renatobardi merges PRs to main |
| **VI. Single Production Env** | ✅ PASS | Phase A rules are immutable; projects copy files explicitly; no environment config needed |
| **VII. Strict CI** | ✅ PASS | CI gates: lint (YAML validation), test (pytest on test repo), build (docs generation), security scan (no hardcoded secrets) |
| **VIII. Security Mandatory** | ✅ PASS | No hardcoded secrets; rules publicly distributed; no external API calls (Phase A); GitHub API failures non-blocking |
| **IX. Clean Code** | ✅ PASS | All YAML, Bash, JavaScript, and Markdown follow conventions; no dead code |
| **X. Hexagonal Architecture** | ⊘ N/A | Phase A does not require domain model or ports; static rules only. Hexagonal applies Phase 1+ (API-driven rules download) |
| **XI. .project/ Directory** | ✅ PASS | Spec, plan, tasks stored in `specs/010-github-semgrep-rules/`; archive to `.project/` if obsoleted |
| **XII. Documentation** | ✅ PASS | spec.md, plan.md, THELOOP.md (installation guide) all required; docs-check gate applies |
| **XIII. Dependencies in Plan** | ✅ PASS | All infrastructure dependencies explicit: Semgrep CLI, GitHub Actions, test repository, secrets (none for Phase A), CI jobs |

**Gate Result**: ✅ **PASS** — All mandamentos addressed. Phase A scope is contained, security-compliant, and documentation-complete.

## Project Structure

### Documentation (this feature)

```text
specs/010-github-semgrep-rules/
├── spec.md              # Feature specification (completed, clarified)
├── plan.md              # This file (execution plan)
├── research.md          # Phase 0 output — research on Semgrep patterns, GitHub Actions best practices
├── data-model.md        # Phase 1 output — rule schema, workflow structure, metadata
├── quickstart.md        # Phase 1 output — developer quick-start guide
├── contracts/           # Phase 1 output — GitHub API contract, rule format contract
│   ├── semgrep-rule.json        # Rule schema (JSON Schema)
│   ├── github-api-comment.json  # PR comment format (JSON)
│   └── workflow-contract.md     # Workflow execution contract
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan — use /speckit.tasks)
```

### Source Code (repository root)

```text
.semgrep/
  theloop-rules.yml           # 6 incident-derived Semgrep rules (delivered to projects via copy-paste)

.github/workflows/
  theloop-guard.yml           # GitHub Actions workflow (delivered to projects via copy-paste)

THELOOP.md                    # Installation guide + troubleshooting (distributed with rules)

the-loop-tester/              # Separate public test repository (https://github.com/renatobardi/the-loop-tester)
  .semgrep/
    theloop-rules.yml         # Copy of rules for validation
  .github/workflows/
    theloop-guard.yml         # Copy of workflow
  bad/                        # Intentionally vulnerable code (6 files)
    injection.py
    shell.py
    secrets.py
    error_handling.py
    regex_dos.py
    eval_injection.py
  good/                       # Fixed code (each mirrors bad/ with same name)
    injection_safe.py
    shell_safe.py
    secrets_safe.py
    error_handling_safe.py
    regex_dos_safe.py
    eval_injection_safe.py
  README.md                   # Test repo documentation
```

**Structure Decision**: Phase A is a pure distribution MVP — no backend code, no new infrastructure in The Loop repo itself. All deliverables (`.semgrep/` rules, `.github/workflows/` action, `THELOOP.md` docs) are copied into target projects. Test repository is separate public repo used for validation. No hexagonal architecture needed (no domain model, no ports).

## Complexity Tracking

> Mandamento X (Hexagonal Architecture) does **not** apply to Phase A. Rationale:
> - Phase A delivers static rules only; no domain entities, no service layer, no repository pattern needed
> - Rules are YAML (declarative), not code requiring abstraction
> - GitHub Actions workflow is procedural scripting, not business logic requiring ports
> - Phase B (API-driven rules download) will introduce domain model + ports + adapters; deferred

| Area | Status | Notes |
|---|---|---|
| Domain Model | ⊘ N/A | Rules are declarative (YAML); workflow is procedural. No domain entities in Phase A. |
| Port Pattern | ⊘ N/A | Single GitHub API integration; no multiple adapters. Direct integration acceptable. |
| Test Strategy | ✅ INCLUDE | Test repository (`the-loop-tester`) serves as integration test environment; validates all 6 rules end-to-end |
| CI Gates | ✅ INCLUDE | YAML validation (semgrep --validate), pytest on test repo, docs-check, Trivy scan |

---

## Phase 1 Planning Outputs

### Deliverables Generated

✅ **research.md** — 8 research findings resolved:
- Semgrep rule syntax & multilingual patterns
- GitHub Actions workflow integration patterns
- GitHub API failure handling (non-blocking approach)
- Finding pagination & comment size management (50-cap + link to full report)
- Rule immutability & versioning (Phase A static, Phase B dynamic)
- False positive feedback routing (loop.oute.pro/feedback web form)
- Semgrep scan timeout strategy (10s target, 30s hard limit, warning threshold)
- Rule accuracy validation via test repository (bad/ vs good/ scenarios)

✅ **data-model.md** — Full specification of 4 entities:
1. **Semgrep Rule** — YAML schema with metadata, patterns, validation rules
2. **GitHub Actions Workflow** — Execution flow, data transformation, error scenarios
3. **Semgrep JSON Output** — Result format, transformation for PR comment display
4. **Installation & Configuration** — 3 deliverable files (rules, workflow, docs)

✅ **contracts/** directory:
- `semgrep-rule-schema.json` — JSON Schema for rule validation
- `workflow-execution-contract.md` — Workflow behavior contract with error scenarios, performance targets, backward compatibility
- (GitHub API contract implicit in workflow-execution-contract.md)

✅ **quickstart.md** — Developer implementation guide:
- 6-step walkthrough (create rules, workflow, docs, test locally, validate, test repo)
- Code samples and key points for each file
- Troubleshooting section
- Implementation checklist

### Architecture Decisions Confirmed

| Decision | Rationale |
|----------|-----------|
| **YAML over JSON for rules** | Human-readable, version-control friendly, Semgrep native format |
| **GitHub Actions for workflow** | Built-in, no additional SaaS dependency, `github-script` is standard |
| **Non-blocking API failures** | Resilience; scan results accessible even if comment fails |
| **50-finding cap in comment** | Readability; top 50 is actionable; full report in artifacts |
| **Immutable rules (Phase A)** | Simplicity; predictability; upgrade via copy-paste only |
| **Test repository pattern** | End-to-end validation; regression prevention; CI automation |
| **No hexagonal architecture** | Phase A is static rules; no domain model, no abstraction needed |

---

## Phase 2 Ready

Planning is complete. Next step: `/speckit.tasks` to generate task breakdown and implementation sequence.

**Estimated scope** (from research + design):
- 3 deliverable files (`.semgrep/theloop-rules.yml`, `.github/workflows/theloop-guard.yml`, `THELOOP.md`)
- 6 test code files in test repository (`bad/` and `good/` directories)
- ~50-100 lines YAML rules, ~200-300 lines workflow YAML, ~200 lines markdown docs
- ~20-30 implementation tasks (rule definition, workflow creation, testing, validation, docs)
- ~15-20 test tasks (unit, integration, end-to-end)
- CI gate: YAML validation, pytest on test repo, docs-check

**No infrastructure, database, or API required for Phase A.**
