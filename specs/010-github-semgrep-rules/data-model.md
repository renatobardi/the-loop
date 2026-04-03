# Data Model & Contracts: GitHub + Semgrep Integration — Phase A

**Created**: 2026-04-03  
**Feature**: GitHub + Semgrep Integration — Phase A  
**Purpose**: Define rule schema, workflow data structures, and interface contracts

---

## Entity 1: Semgrep Rule

### Definition
A rule is a declarative pattern definition that describes vulnerable code and maps it to an incident context.

### Schema

```yaml
id: string                      # Rule identifier (kebab-case, unique)
languages: [string]             # Target languages (e.g., [python, javascript, typescript])
message: string                 # Human-readable message shown in PR comment
severity: ERROR | WARNING       # Fail merge if ERROR; informational if WARNING
metadata:
  incident_id: string           # Reference to incident in The Loop (e.g., "injection-001")
  category: string              # Incident category (e.g., "injection", "unsafe-api-usage")
  loop_url: string              # URL to incident details (Phase A: placeholder; Phase B: actual link)
  remediation: string           # Step-by-step fix instructions for developer
patterns: [...]                 # Semgrep pattern definitions (pattern, pattern-either, pattern-regex, etc.)
pattern-not: [...]              # Exclusions (optional)
paths:                          # File path filters (optional)
  exclude:
    - "*.test.*"
    - "test_*"
    - "tests/"
    - ".env.example"
    - "*.example"
```

### Examples

#### Example 1: injection-001 (SQL via string concatenation)

```yaml
- id: injection-001-sql-string-concat
  languages: [python, javascript, typescript, java, go, ruby]
  message: |
    [The Loop] SQL injection via string concatenation detected.
    Incident: injection-001 | Severity: CRITICAL
    Remediation: Use prepared statements / parametrized queries.
    More info: https://loop.oute.pro/incidents/injection-001
  severity: ERROR
  metadata:
    incident_id: "injection-001"
    category: "injection"
    loop_url: "https://loop.oute.pro/incidents/injection-001"
    remediation: "Use parameterized queries: cursor.execute(query, (value,)) in Python; prepared statements in other languages."
  patterns:
    - pattern-either:
        - pattern: $DB.execute("..." + $INPUT)
        - pattern: $DB.execute("...%s" % $INPUT)
        - pattern: $DB.execute(f"...{$INPUT}...")
```

#### Example 2: missing-error-handling-001 (Bare except)

```yaml
- id: missing-error-handling-001-bare-except
  languages: [python]
  message: |
    [The Loop] Bare except detected — swallows all errors silently.
    Incident: missing-error-handling-001 | Severity: HIGH
    Remediation: Capture specific exceptions and log or re-raise.
    More info: https://loop.oute.pro/incidents/missing-error-handling-001
  severity: WARNING
  metadata:
    incident_id: "missing-error-handling-001"
    category: "missing-error-handling"
    loop_url: "https://loop.oute.pro/incidents/missing-error-handling-001"
    remediation: "Use 'except SpecificException as e: logger.error(e); raise' instead of 'except: pass'"
  pattern: |
    try:
        ...
    except:
        pass
```

### Validation Rules
- `id` must be globally unique across all rules
- `incident_id` must exist in The Loop incident database
- `languages` must be a non-empty list of Semgrep-supported languages
- `severity` must be exactly ERROR or WARNING (no CRITICAL, INFO, etc.)
- `remediation` must be actionable (not vague; should guide developer toward fix)
- `message` field should not exceed 500 characters for PR comment readability

### Relationships
- Each rule maps to exactly one incident (1:1 mapping via `incident_id`)
- Multiple rules may belong to same category (N:1 relationship to category)
- Rules are immutable within a version; new rules require new file version

---

## Entity 2: GitHub Actions Workflow

### Definition
A workflow is an automated procedure that runs Semgrep on PR code and reports findings to GitHub.

### Schema

```yaml
name: string                    # Workflow display name
on:
  pull_request:
    branches: [string]          # Target branches (main, master, develop)
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write
  security-events: write        # For future SARIF upload

jobs:
  semgrep-scan:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - run: pip install semgrep    # Install Semgrep CLI
      - run: semgrep scan --config .semgrep/theloop-rules.yml --json --output results.json
      - name: Comment PR with findings
        uses: actions/github-script@v7
        with:
          script: |
            # Parse JSON, format table, find/update existing comment
```

### Workflow Execution Flow

```
1. Trigger: PR opened/updated/reopened on target branch
   ↓
2. Checkout code
   ↓
3. Install Semgrep CLI
   ↓
4. Validate rules file exists (.semgrep/theloop-rules.yml)
   ↓
5. Run Semgrep scan
   ├─ Parse JSON output
   ├─ Group by severity (ERROR, WARNING)
   └─ Cap at 50 findings + add link if more exist
   ↓
6. Find existing PR comment (by bot + "The Loop" marker)
   ├─ If exists: UPDATE (no duplicate)
   └─ If not exists: CREATE
   ↓
7. Set workflow status
   ├─ If ERROR findings > 0: FAIL job (blocks merge)
   └─ If only WARNING or no findings: PASS job
   ↓
8. End
```

### Data Structure: PR Comment

```markdown
## 🔁 The Loop — Incident Guard

🔴 **N error(s) critical detected — merge blocked**

| Severity | Rule | File | Line | Incident |
|:---:|:---|:---|:---:|:---:|
| 🔴 ERROR | `injection-001` | `app.py` | 42 | [injection-001](https://loop.oute.pro/incidents/injection-001) |
| 🟡 WARN | `missing-error-handling-001` | `utils.py` | 15 | [missing-error-handling-001](https://loop.oute.pro/incidents/missing-error-handling-001) |

### How to resolve

**injection-001**: Use parameterized queries: cursor.execute(query, (value,)) in Python; prepared statements in other languages.

---
> 🔁 [The Loop](https://loop.oute.pro) | [Report false positive](https://loop.oute.pro/feedback) | Rules version: `0.1.0-static`
```

### Validation Rules
- Workflow only runs on target branches (not PRs from forks by default)
- Permissions are minimized (read-only for contents, write-only for PR comments)
- Timeout is 10 minutes (hard limit prevents hanging)
- Status check name is deterministic (allows GitHub branch protection to reference)

---

## Entity 3: Semgrep JSON Output

### Definition
JSON report generated by Semgrep scan; contains all detected findings.

### Schema

```json
{
  "results": [
    {
      "check_id": "theloop.injection-001-sql-string-concat",
      "path": "app.py",
      "start": { "line": 42, "col": 5 },
      "end": { "line": 42, "col": 30 },
      "message": "[The Loop] SQL injection via string concatenation detected...",
      "extra": {
        "severity": "ERROR",
        "metadata": {
          "incident_id": "injection-001",
          "category": "injection",
          "loop_url": "https://loop.oute.pro/incidents/injection-001",
          "remediation": "Use parameterized queries..."
        }
      }
    }
  ],
  "errors": [],
  "stats": {
    "files": { "scanned": 25, "skipped": 3 },
    "rules": { "parsed": 6, "run": 6 }
  }
}
```

### Transformation (for PR comment)

```javascript
const findings = results.map(r => ({
  rule_id: r.check_id.split('.').pop(),
  severity: r.extra.severity,
  file: r.path,
  line: r.start.line,
  incident_id: r.extra.metadata.incident_id,
  loop_url: r.extra.metadata.loop_url,
  remediation: r.extra.metadata.remediation
}));

// Sort by severity (ERROR first), then by file
findings.sort((a, b) => 
  (severityOrder[b.severity] - severityOrder[a.severity]) ||
  a.file.localeCompare(b.file)
);

// Cap at 50 + add link if more
const display = findings.slice(0, 50);
const hasMore = findings.length > 50;
```

---

## Entity 4: Installation & Configuration

### Definition
Files distributed to target projects for adoption.

### Files

#### File 1: `.semgrep/theloop-rules.yml`

- **Location**: `.semgrep/` directory in target project
- **Content**: 6 rules from Entity 1 above
- **Immutable**: Version embedded in comment; must be replaced entirely for updates
- **Size**: ~3-5 KB (depends on pattern complexity)

#### File 2: `.github/workflows/theloop-guard.yml`

- **Location**: `.github/workflows/` directory in target project
- **Content**: Workflow from Entity 2 above
- **Triggers**: `pull_request` events (opened, synchronize, reopened)
- **Permissions**: contents: read, pull-requests: write

#### File 3: `THELOOP.md`

- **Location**: Root directory of target project
- **Content**: 
  - 1-paragraph overview of The Loop
  - Installation steps (copy 2 files)
  - Active rules list + severity levels
  - Troubleshooting (missing file, YAML errors, GitHub API failures)
  - Phase B roadmap (API-driven updates)
- **Length**: ~2-3 pages (Markdown)

---

## Validation Constraints

| Constraint | Rationale | Test |
|---|---|---|
| Rules must pass `semgrep --validate` | Syntax correctness | CI gate: validation step fails if invalid YAML |
| All 6 rules must fire on `bad/` test code | Detection accuracy | Test repo PR with bad/ → expects 6 findings |
| Zero rules must fire on `good/` test code | False positive rate | Test repo PR with good/ → expects 0 findings |
| Comment must update (not duplicate) | Usability | Test repo: push commit to PR → existing comment modified |
| Findings capped at 50 in comment | Readability | Test repo: 100+ findings PR → shows 50 + link |
| Workflow completes in <10 seconds | User experience | Test on repo with 1000+ files |

---

## State Transitions

### Rule Lifecycle (Phase A → Phase B)

```
IMMUTABLE (Phase A)
  ├─ Copy distributed via GitHub copy-paste
  ├─ No auto-updates
  └─ Version embedded in file
      ↓
DYNAMIC (Phase B)
  ├─ Fetched from API endpoint
  ├─ Versioned in database
  └─ Auto-update via workflow refresh
      ↓
MAINTAINED (Phase C+)
  ├─ Rules refined based on feedback
  ├─ New rules added for new incidents
  └─ Deprecated rules marked for removal
```

### Workflow Execution Lifecycle

```
PENDING (PR opened)
  ↓
RUNNING (Semgrep scan in progress)
  ├─ Timeout warning if >10s
  ├─ Hard timeout at 30s with partial results
  ↓
COMPLETED
  ├─ Results → GitHub JSON
  ├─ Comment created/updated
  ├─ Status check set (PASS/FAIL)
  ↓
PASSED (No ERROR findings | all statuses green)
  ↓
FAILED (ERROR findings > 0 | merge blocked)
```

---

## Summary

Phase A data model is entirely declarative and static:
- **Rules**: 6 YAML definitions, manually versioned
- **Workflow**: 1 GitHub Actions YAML, triggers on PR events
- **Output**: JSON from Semgrep, formatted as Markdown table in PR comment
- **Files**: 3 distributed files (rules, workflow, docs)
- **No database, no API, no state persistence** — single-purpose scanner

Phase B will introduce:
- Database schema for rule versioning and metadata
- API endpoints for rule download and feedback
- Dynamic rule fetching in workflow
- Feedback aggregation and refinement pipeline
