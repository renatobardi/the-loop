"""Create v0.4.0 rule_versions entry with complete 45-rule set.

Migration 014 seeded v0.3.0 with only 1 placeholder rule.
This migration creates a new version v0.4.0 with the full 45 rules:
  Phase A (6)  — Python: SQL injection, eval, shell, secrets, bare-except, ReDoS
  Phase B (14) — Python/multi-lang: path traversal, XXE, crypto, CORS, N+1, etc.
  Phase C (25) — 15 JS/TS + 10 Go

Migrations 016 and 017 will then build on v0.4.0 by adding Java (15) and C# (15) rules.

Revision ID: 015
Revises: 014
Create Date: 2026-04-05
"""

import json
from typing import Any

import sqlalchemy as sa
from alembic import op

revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None

RULES_VERSION = "0.4.0"  # Create new version for Phase B (Python) + Phase C (JS/TS + Go)
FULL_RULES_COUNT = 45

# All 45 rules in DB JSON format (list[dict] — matches Rule domain model fields).
# patterns follow the converter format (json_to_semgrep_yaml.py):
#   {"pattern": "..."}
#   {"pattern-either": ["pat1", "pat2"]}
#   {"pattern-not": ["pat1"]}
#   {"pattern-regex": "..."}
V030_FULL_RULES: list[dict[str, Any]] = [
    # ── PHASE A (6) ────────────────────────────────��─────────────────────────

    {
        "id": "injection-001-sql-string-concat",
        "languages": ["python", "javascript", "typescript", "java", "go", "ruby"],
        "message": "[The Loop] SQL injection via string concatenation",
        "severity": "ERROR",
        "metadata": {"category": "injection", "cwe": "CWE-89"},
        "patterns": [{"pattern-either": [
            '$DB.execute("..." + $INPUT)',
            '$DB.execute(f"...{$INPUT}...")',
        ]}],
    },
    {
        "id": "injection-002-eval-dynamic-input",
        "languages": ["python", "javascript", "typescript", "ruby"],
        "message": "[The Loop] eval() with dynamic input",
        "severity": "ERROR",
        "metadata": {"category": "injection", "cwe": "CWE-94"},
        "patterns": [{"pattern-either": ["eval($INPUT)", "exec($INPUT)"]}],
    },
    {
        "id": "unsafe-api-usage-001-shell-injection",
        "languages": ["python"],
        "message": "[The Loop] Shell execution with variable",
        "severity": "ERROR",
        "metadata": {"category": "unsafe-api-usage", "cwe": "CWE-78"},
        "patterns": [{"pattern-either": [
            "os.system($CMD)",
            "subprocess.call($CMD, ..., shell=True)",
        ]}],
    },
    {
        "id": "missing-safety-check-001-hardcoded-secret",
        "languages": ["generic"],
        "message": "[The Loop] Hardcoded credential detected",
        "severity": "ERROR",
        "metadata": {"category": "missing-safety-check"},
        "patterns": [{"pattern-regex": r'(?i)(password|secret|api_key)\s*[=:]\s*["\'][A-Za-z0-9]{8,}["\']'}],  # noqa: E501
    },
    {
        "id": "missing-error-handling-001-bare-except",
        "languages": ["python"],
        "message": "[The Loop] Bare except clause catches all exceptions silently",
        "severity": "WARNING",
        "metadata": {"category": "missing-error-handling"},
        "patterns": [{"pattern-regex": r"except\s*:"}],
    },
    {
        "id": "unsafe-regex-001-redos-pattern",
        "languages": ["python", "javascript", "typescript", "java"],
        "message": "[The Loop] ReDoS pattern detected",
        "severity": "WARNING",
        "metadata": {"category": "unsafe-regex"},
        "patterns": [{"pattern-regex": r"\((\.\.\+|\.\*)[+*]"}],
    },

    # ── PHASE B (14) ─────────────────────────────────────────────────────────

    {
        "id": "path-traversal-001",
        "languages": ["python", "javascript", "java"],
        "message": "[The Loop] Path traversal vulnerability",
        "severity": "ERROR",
        "metadata": {"category": "injection", "cwe": "CWE-22"},
        "patterns": [{"pattern-either": ["open($INPUT, ...)", "Path($INPUT).open(...)"]}],
    },
    {
        "id": "xxe-001",
        "languages": ["python", "java", "javascript"],
        "message": "[The Loop] XML External Entity (XXE) injection risk",
        "severity": "ERROR",
        "metadata": {"category": "injection", "cwe": "CWE-611"},
        "patterns": [{"pattern-either": ["ElementTree.parse($URL)", "ET.parse($URL)"]}],
    },
    {
        "id": "deserialization-001",
        "languages": ["python", "javascript", "java"],
        "message": "[The Loop] Unsafe deserialization",
        "severity": "ERROR",
        "metadata": {"category": "injection", "cwe": "CWE-502"},
        "patterns": [{"pattern-either": ["pickle.loads($DATA)", "yaml.load($DATA)"]}],
    },
    {
        "id": "crypto-weak-md5-001",
        "languages": ["python", "javascript", "java"],
        "message": "[The Loop] MD5 used for hashing",
        "severity": "WARNING",
        "metadata": {"category": "crypto", "cwe": "CWE-327"},
        "patterns": [{"pattern-either": [
            "hashlib.md5($DATA)",
            'crypto.createHash("md5")',
        ]}],
    },
    {
        "id": "crypto-weak-random-001",
        "languages": ["python", "javascript", "java"],
        "message": "[The Loop] Weak random number generation",
        "severity": "WARNING",
        "metadata": {"category": "crypto", "cwe": "CWE-338"},
        "patterns": [{"pattern-either": ["random.random()", "Math.random()"]}],
    },
    {
        "id": "tls-verify-false-001",
        "languages": ["python", "javascript", "java"],
        "message": "[The Loop] TLS certificate verification disabled",
        "severity": "ERROR",
        "metadata": {"category": "security", "cwe": "CWE-295"},
        "patterns": [{"pattern-either": [
            "requests.get(..., verify=False)",
            "ssl._create_unverified_context()",
        ]}],
    },
    {
        "id": "jwt-hardcoded-001",
        "languages": ["python", "javascript", "java"],
        "message": "[The Loop] Hardcoded JWT secret",
        "severity": "ERROR",
        "metadata": {"category": "security", "cwe": "CWE-798"},
        "patterns": [{"pattern-regex": r'(?i)jwt_secret\s*[=:]\s*["\'][\w\-.]{20,}["\']'}],
    },
    {
        "id": "cors-wildcard-001",
        "languages": ["python", "javascript"],
        "message": "[The Loop] CORS with wildcard origin",
        "severity": "WARNING",
        "metadata": {"category": "security", "cwe": "CWE-345"},
        "patterns": [{"pattern-regex": r"Access-Control-Allow-Origin.*\*"}],
    },
    {
        "id": "sql-timeout-001",
        "languages": ["python", "javascript", "java"],
        "message": "[The Loop] SQL query without timeout",
        "severity": "WARNING",
        "metadata": {"category": "performance"},
        "patterns": [
            {"pattern": "cursor.execute($QUERY)"},
            {"pattern-not": ["cursor.execute($QUERY, timeout=$TIMEOUT)"]},
        ],
    },
    {
        "id": "n-plus-one-001",
        "languages": ["python", "javascript"],
        "message": "[The Loop] N+1 query pattern — database call inside loop",
        "severity": "WARNING",
        "metadata": {"category": "performance"},
        "patterns": [{"pattern-regex": r"for\s+\w+\s+in\s+.+:[\s\S]*?\.(query|execute)\("}],
    },
    {
        "id": "docker-root-001",
        "languages": ["generic"],
        "message": "[The Loop] Docker container runs as root",
        "severity": "WARNING",
        "metadata": {"category": "infrastructure"},
        "patterns": [{"pattern-regex": r"USER\s+root"}],
    },
    {
        "id": "hardcoded-url-001",
        "languages": ["python", "javascript", "go"],
        "message": "[The Loop] Hardcoded API URL in code",
        "severity": "WARNING",
        "metadata": {"category": "config"},
        "patterns": [{"pattern-regex": r'(api_url|endpoint)\s*[=:]\s*["\']https?://[^"\']+'}],
    },
    {
        "id": "debug-enabled-prod-001",
        "languages": ["python", "javascript"],
        "message": "[The Loop] Debug mode enabled in production",
        "severity": "WARNING",
        "metadata": {"category": "config"},
        "patterns": [{"pattern-either": ["DEBUG = True", "app.run(debug=True)"]}],
    },
    {
        "id": "dependency-vulnerable-001",
        "languages": ["generic"],
        "message": "[The Loop] Known vulnerable dependency",
        "severity": "WARNING",
        "metadata": {"category": "dependencies", "cwe": "CWE-1104"},
        "patterns": [{"pattern-regex": r"lodash.*<.*4\.17\.15"}],
    },

    # ── PHASE C — JS/TS INJECTION (4) ────────────────────────────────────────

    {
        "id": "js-injection-001",
        "languages": ["javascript", "typescript"],
        "message": "[The Loop] SQL injection via string concatenation (JS/TS)",
        "severity": "ERROR",
        "metadata": {"category": "injection", "cwe": "CWE-89"},
        "patterns": [{"pattern-either": [
            "$DB.raw($X + $Y)",
            "$CLIENT.query($X + $Y)",
            "knex.raw($X + $Y)",
        ]}],
    },
    {
        "id": "js-injection-002",
        "languages": ["javascript", "typescript"],
        "message": "[The Loop] Dynamic code execution via Function constructor or eval",
        "severity": "ERROR",
        "metadata": {"category": "injection", "cwe": "CWE-94"},
        "patterns": [{"pattern-either": ["new Function($INPUT)", "eval($INPUT)"]}],
    },
    {
        "id": "js-injection-003",
        "languages": ["javascript", "typescript"],
        "message": "[The Loop] XSS via innerHTML assignment with dynamic value",
        "severity": "ERROR",
        "metadata": {"category": "injection", "cwe": "CWE-79"},
        "patterns": [{"pattern": "$EL.innerHTML = $INPUT"}],
    },
    {
        "id": "js-injection-004",
        "languages": ["javascript", "typescript"],
        "message": "[The Loop] Shell injection via child_process with dynamic command",
        "severity": "ERROR",
        "metadata": {"category": "injection", "cwe": "CWE-78"},
        "patterns": [{"pattern-either": [
            "exec($CMD, ...)",
            "execSync($CMD, ...)",
            'spawn("sh", ["-c", $CMD], ...)',
        ]}],
    },

    # ── PHASE C — JS/TS CRYPTO (2) ───────────────────────────────────────────

    {
        "id": "js-crypto-001",
        "languages": ["javascript", "typescript"],
        "message": "[The Loop] Weak cryptographic hash MD5 or SHA1",
        "severity": "WARNING",
        "metadata": {"category": "crypto", "cwe": "CWE-327"},
        "patterns": [{"pattern-either": [
            'crypto.createHash("md5")',
            'crypto.createHash("sha1")',
        ]}],
    },
    {
        "id": "js-crypto-002",
        "languages": ["javascript", "typescript"],
        "message": "[The Loop] Math.random() is not cryptographically secure",
        "severity": "ERROR",
        "metadata": {"category": "crypto", "cwe": "CWE-338"},
        "patterns": [{"pattern": "Math.random()"}],
    },

    # ── PHASE C — JS/TS SECURITY (4) ─────────────────────────────────────────

    {
        "id": "js-security-001",
        "languages": ["javascript", "typescript"],
        "message": "[The Loop] JWT signed with hardcoded string secret",
        "severity": "ERROR",
        "metadata": {"category": "security", "cwe": "CWE-798"},
        "patterns": [{"pattern-either": [
            'jwt.sign($PAYLOAD, "...")',
            'sign($PAYLOAD, "...")',
        ]}],
    },
    {
        "id": "js-security-002",
        "languages": ["javascript", "typescript"],
        "message": "[The Loop] CORS configured with wildcard origin",
        "severity": "WARNING",
        "metadata": {"category": "security", "cwe": "CWE-345"},
        "patterns": [{"pattern-either": [
            'cors({origin: "*"})',
            'cors({..., origin: "*", ...})',
        ]}],
    },
    {
        "id": "js-security-003",
        "languages": ["javascript", "typescript"],
        "message": "[The Loop] TLS validation disabled via NODE_TLS_REJECT_UNAUTHORIZED",
        "severity": "ERROR",
        "metadata": {"category": "security", "cwe": "CWE-295"},
        "patterns": [{"pattern": 'process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0"'}],
    },
    {
        "id": "js-security-004",
        "languages": ["javascript", "typescript"],
        "message": "[The Loop] Prototype pollution risk via Object.assign with external input",
        "severity": "WARNING",
        "metadata": {"category": "security", "cwe": "CWE-1321"},
        "patterns": [{"pattern": "Object.assign({}, $INPUT)"}],
    },

    # ── PHASE C — JS/TS PERFORMANCE (1) ──────────────────────────────────────

    {
        "id": "js-perf-001",
        "languages": ["javascript", "typescript"],
        "message": "[The Loop] await inside loop causes sequential execution (N+1 async)",
        "severity": "WARNING",
        "metadata": {"category": "performance"},
        "patterns": [{"pattern": "for (const $ITEM of $COLLECTION) { ... await $X ... }"}],
    },

    # ── PHASE C — JS/TS CONFIG (2) ────────────────────────────────────────────

    {
        "id": "js-config-001",
        "languages": ["javascript", "typescript"],
        "message": "[The Loop] Sensitive field exposed via console.log",
        "severity": "WARNING",
        "metadata": {"category": "config"},
        "patterns": [{"pattern-either": [
            "console.log(..., $X.password, ...)",
            "console.log(..., $X.token, ...)",
            "console.log(..., $X.secret, ...)",
            "console.log(..., $X.apiKey, ...)",
        ]}],
    },
    {
        "id": "js-config-002",
        "languages": ["javascript", "typescript"],
        "message": "[The Loop] Hardcoded production/staging URL in source code",
        "severity": "WARNING",
        "metadata": {"category": "config"},
        "patterns": [{"pattern-regex": r"https?://[a-z0-9.-]+(prod|production|live|staging)[a-z0-9.-]*"}],
    },

    # ── PHASE C — TYPESCRIPT-SPECIFIC (2) ────────────────────────────────────

    {
        "id": "ts-security-001",
        "languages": ["typescript"],
        "message": "[The Loop] Parameter typed as 'any' bypasses TypeScript safety checks",
        "severity": "WARNING",
        "metadata": {"category": "security"},
        "patterns": [{"pattern": "function $F($X: any) { ... }"}],
    },
    {
        "id": "ts-security-002",
        "languages": ["typescript"],
        "message": "[The Loop] Forced double type assertion 'as unknown as T' bypasses type safety",
        "severity": "WARNING",
        "metadata": {"category": "security"},
        "patterns": [{"pattern": "($X as unknown as $T)"}],
    },

    # ── PHASE C — GO INJECTION (3) ────────────────────────────────────────────

    {
        "id": "go-injection-001",
        "languages": ["go"],
        "message": "[The Loop] SQL injection via fmt.Sprintf in database query",
        "severity": "ERROR",
        "metadata": {"category": "injection", "cwe": "CWE-89"},
        "patterns": [{"pattern-either": [
            "$DB.Query(fmt.Sprintf($QUERY, ...))",
            "$DB.Exec(fmt.Sprintf($QUERY, ...))",
            "$DB.QueryRow(fmt.Sprintf($QUERY, ...))",
        ]}],
    },
    {
        "id": "go-injection-002",
        "languages": ["go"],
        "message": "[The Loop] Shell injection via exec.Command with variable argument",
        "severity": "ERROR",
        "metadata": {"category": "injection", "cwe": "CWE-78"},
        "patterns": [
            {"pattern": "exec.Command($CMD, ...)"},
            {"pattern-not": ['exec.Command("...", ...)']},
        ],
    },
    {
        "id": "go-injection-003",
        "languages": ["go"],
        "message": "[The Loop] Path traversal via filepath.Join with unvalidated input",
        "severity": "ERROR",
        "metadata": {"category": "injection", "cwe": "CWE-22"},
        "patterns": [{"pattern-either": [
            "filepath.Join($ROOT, $INPUT)",
            "path.Join($ROOT, $INPUT)",
        ]}],
    },

    # ── PHASE C — GO CRYPTO (2) ───────────────────────────────────────────────

    {
        "id": "go-crypto-001",
        "languages": ["go"],
        "message": "[The Loop] Weak cryptographic hash MD5 or SHA1",
        "severity": "WARNING",
        "metadata": {"category": "crypto", "cwe": "CWE-327"},
        "patterns": [{"pattern-either": ["md5.New()", "sha1.New()"]}],
    },
    {
        "id": "go-crypto-002",
        "languages": ["go"],
        "message": "[The Loop] math/rand used for security-sensitive value — use crypto/rand",
        "severity": "ERROR",
        "metadata": {"category": "crypto", "cwe": "CWE-338"},
        "patterns": [{"pattern-either": ["rand.Read($BUF)", "rand.Intn($N)", "rand.Int63()"]}],
    },

    # ── PHASE C — GO SECURITY (2) ─────────────────────────────────────────────

    {
        "id": "go-security-001",
        "languages": ["go"],
        "message": "[The Loop] TLS certificate verification disabled via InsecureSkipVerify",
        "severity": "ERROR",
        "metadata": {"category": "security", "cwe": "CWE-295"},
        "patterns": [{"pattern": "&tls.Config{..., InsecureSkipVerify: true, ...}"}],
    },
    {
        "id": "go-security-002",
        "languages": ["go"],
        "message": "[The Loop] JWT signed with hardcoded byte-slice secret",
        "severity": "ERROR",
        "metadata": {"category": "security", "cwe": "CWE-798"},
        "patterns": [{"pattern-either": [
            '$TOKEN.SignedString([]byte("..."))',
            'jwt.NewWithClaims($M, $C).SignedString([]byte("..."))',
        ]}],
    },

    # ── PHASE C — GO ERROR HANDLING (2) ──────────────────────────────────────

    {
        "id": "go-error-001",
        "languages": ["go"],
        "message": "[The Loop] Error silently discarded with _ in critical db or file operation",
        "severity": "WARNING",
        "metadata": {"category": "error-handling"},
        "patterns": [{"pattern-either": [
            "$X, _ = $DB.Query(...)",
            "$X, _ = $DB.Exec(...)",
            "$X, _ = os.Create(...)",
            "$X, _ = os.Open(...)",
        ]}],
    },
    {
        "id": "go-error-002",
        "languages": ["go"],
        "message": "[The Loop] panic() in HTTP handler — return an error response instead",
        "severity": "WARNING",
        "metadata": {"category": "error-handling"},
        "patterns": [
            {"pattern": "func $H(w http.ResponseWriter, r *http.Request) { ... panic(...) ... }"},
        ],
    },

    # ── PHASE C — GO CONFIG (1) ───────────────────────────────────────────────

    {
        "id": "go-config-001",
        "languages": ["go"],
        "message": "[The Loop] http.ListenAndServe without TLS — use ListenAndServeTLS in prod",
        "severity": "WARNING",
        "metadata": {"category": "config"},
        "patterns": [{"pattern": "http.ListenAndServe($ADDR, $HANDLER)"}],
    },
]


def upgrade() -> None:
    """Create v0.4.0 with the complete 45-rule set.

    Migration 014 seeded v0.3.0 with 1 placeholder rule. This migration
    creates a new version v0.4.0 with the full ruleset.

    - Idempotent: returns early if v0.4.0 already exists with ≥ 45 rules
    - Fails fast if v0.4.0 cannot be created or insertion fails
    - Explicitly commits transaction
    """
    assert len(V030_FULL_RULES) == FULL_RULES_COUNT, (
        f"Expected {FULL_RULES_COUNT} rules, got {len(V030_FULL_RULES)}"
    )

    connection = op.get_bind()

    # Check if v0.4.0 already exists
    result = connection.execute(
        sa.text("SELECT rules_json FROM rule_versions WHERE version = :version"),
        {"version": RULES_VERSION},
    )
    row = result.first()

    if row:
        # v0.4.0 exists — check if already patched
        existing_rules: Any = row[0]
        if isinstance(existing_rules, str):
            rules_list: Any = json.loads(existing_rules)
        else:
            rules_list = existing_rules

        if isinstance(rules_list, list) and len(rules_list) >= FULL_RULES_COUNT:
            # Already patched — idempotent success
            return

        # Exists but incomplete — this is unexpected
        raise RuntimeError(
            f"v{RULES_VERSION} exists with {len(rules_list) if isinstance(rules_list, list) else 0} rules; "
            f"expected 0 (not yet created) or {FULL_RULES_COUNT} (already patched)."
        )

    # Validate and serialize the full ruleset
    try:
        rules_json: str = json.dumps(V030_FULL_RULES)
        json.loads(rules_json)  # round-trip validation
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize rules: {e}") from e

    # Create v0.4.0 with the full ruleset
    from uuid import uuid4

    connection.execute(
        sa.text(
            "INSERT INTO rule_versions (id, version, rules_json, status, notes, published_by) "
            "VALUES (:id, :version, :rules_json, :status, :notes, :published_by)"
        ),
        {
            "id": str(uuid4()),
            "version": RULES_VERSION,
            "rules_json": rules_json,
            "status": "active",
            "notes": "Phase B + C: 45 rules (20 Python + 15 JS/TS + 10 Go)",
            "published_by": None,  # System migration, no user attribution
        }
    )

    connection.commit()


def downgrade() -> None:
    """Delete v0.4.0 on downgrade (returns to v0.3.0 from migration 014)."""
    connection = op.get_bind()

    # Delete v0.4.0 if it exists
    result = connection.execute(
        sa.text("DELETE FROM rule_versions WHERE version = :version"),
        {"version": RULES_VERSION}
    )

    if result.rowcount == 0:
        # v0.4.0 doesn't exist — idempotent (downgrade already complete or never ran)
        return

    connection.commit()
