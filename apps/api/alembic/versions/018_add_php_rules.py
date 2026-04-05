"""Add 10 PHP rules to v0.4.0 (Spec-017 Phase 4)

Revision ID: 018
Revises: 017
Create Date: 2026-04-05

"""

import json
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "018"
down_revision = "017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add 10 PHP rules to v0.4.0, bringing total from 75 to 85 rules."""
    connection = op.get_bind()

    # Idempotency guard: check if migration 018 already ran (v0.4.0 has >= 85 rules)
    existing_check = connection.execute(
        sa.text("SELECT id, rules_json FROM rule_versions WHERE version = :version"),
        {"version": "0.4.0"},
    )
    existing_row = existing_check.first()

    if existing_row:
        existing_rules = (
            json.loads(existing_row[1])
            if isinstance(existing_row[1], str)
            else existing_row[1]
        )

        # Check migration completion state
        rule_count = len(existing_rules) if isinstance(existing_rules, list) else 0

        if rule_count >= 85:
            return  # Already patched — migration 018 completed

        # Valid intermediate states from prior migrations
        if rule_count in (45, 60, 75):
            pass  # Expected; continue to append PHP rules
        else:
            # Unexpected state
            raise RuntimeError(
                f"Version v0.4.0 exists with {rule_count} rules; "
                f"expected 45 (migration 015), 60 (migration 016), 75 (migration 017), or 85+ (migration 018 completed). "
                "Database state is inconsistent. Manual review required."
            )

    # Hardcoded PHP rules (Phase 4)
    PHP_RULES = [
        {
            "id": "php-injection-001",
            "languages": ["php"],
            "message": "[The Loop] SQL injection via string concatenation in mysqli_query",
            "severity": "ERROR",
            "patterns": [{"pattern-either": [
                'mysqli_query($CONN, "..." . $INPUT)',
                '$CONN->query("..." . $INPUT)',
            ]}],
            "metadata": {"category": "injection", "cwe": "CWE-89"},
        },
        {
            "id": "php-injection-002",
            "languages": ["php"],
            "message": "[The Loop] SQL injection via string interpolation in PDO exec",
            "severity": "ERROR",
            "patterns": [{"pattern-either": [
                '$DB->exec("SELECT ... WHERE $INPUT ...")',
                '$DB->query("SELECT ... WHERE $INPUT ...")',
            ]}],
            "metadata": {"category": "injection", "cwe": "CWE-89"},
        },
        {
            "id": "php-injection-003",
            "languages": ["php"],
            "message": "[The Loop] Shell injection via system() with unsanitized input",
            "severity": "ERROR",
            "patterns": [{"pattern-either": [
                "system($CMD)",
                "exec($CMD)",
                "shell_exec($CMD)",
                "passthru($CMD)",
            ]}],
            "metadata": {"category": "injection", "cwe": "CWE-78"},
        },
        {
            "id": "php-crypto-001",
            "languages": ["php"],
            "message": "[The Loop] Weak hash algorithm (MD5 or SHA1) detected",
            "severity": "WARNING",
            "patterns": [{"pattern-either": ["md5(...)", "sha1(...)"]}],
            "metadata": {"category": "crypto", "cwe": "CWE-327"},
        },
        {
            "id": "php-crypto-002",
            "languages": ["php"],
            "message": "[The Loop] Weak random number generator for security-sensitive purpose",
            "severity": "ERROR",
            "patterns": [{"pattern-either": ["rand(...)", "mt_rand(...)"]}],
            "metadata": {"category": "crypto", "cwe": "CWE-338"},
        },
        {
            "id": "php-security-001",
            "languages": ["php"],
            "message": "[The Loop] Hardcoded API key or database credential detected",
            "severity": "ERROR",
            "patterns": [{"pattern-regex": r"\$(?:password|api_key|secret)\s*=\s*['\"](?!\$)[^'\"]+['\"]"}],
            "metadata": {"category": "security", "cwe": "CWE-798"},
        },
        {
            "id": "php-security-002",
            "languages": ["php"],
            "message": "[The Loop] CORS misconfiguration with wildcard origin",
            "severity": "WARNING",
            "patterns": [{"pattern-either": [
                'header("Access-Control-Allow-Origin: *")',
                '$_SERVER[\'HTTP_ORIGIN\'] . "*"',
            ]}],
            "metadata": {"category": "security", "cwe": "CWE-345"},
        },
        {
            "id": "php-security-003",
            "languages": ["php"],
            "message": "[The Loop] Unsafe deserialization with unserialize()",
            "severity": "ERROR",
            "patterns": [{"pattern": "unserialize($INPUT)"}],
            "metadata": {"category": "security", "cwe": "CWE-502"},
        },
        {
            "id": "php-error-001",
            "languages": ["php"],
            "message": "[The Loop] Exception caught and silently discarded",
            "severity": "WARNING",
            "patterns": [{"pattern": "catch ($E) { }"}],
            "metadata": {"category": "error-handling"},
        },
        {
            "id": "php-config-001",
            "languages": ["php"],
            "message": "[The Loop] Direct $_GET/$_POST access without sanitization",
            "severity": "WARNING",
            "patterns": [{"pattern-either": ["$_GET[...]", "$_POST[...]", "$_REQUEST[...]"]}],
            "metadata": {"category": "config"},
        },
    ]

    # Expected count after PHP phase
    FULL_RULES_COUNT = 85  # 75 existing (45 + 15 Java + 15 C#) + 10 PHP
    PHP_RULES_COUNT = len(PHP_RULES)

    if PHP_RULES_COUNT != 10:
        raise RuntimeError(
            f"Expected 10 PHP rules; found {PHP_RULES_COUNT}. "
            "Data integrity check failed."
        )

    # Fetch existing 75 rules and APPEND PHP rules (don't overwrite!)
    existing_result = connection.execute(
        sa.text("SELECT rules_json FROM rule_versions WHERE version = :version"),
        {"version": "0.4.0"},
    )
    existing_data = existing_result.first()
    if not existing_data:
        raise RuntimeError("v0.4.0 does not exist. Run migration 017 first.")

    existing_rules = (
        json.loads(existing_data[0])
        if isinstance(existing_data[0], str)
        else existing_data[0]
    )

    # Merge: existing 75 + new 10 PHP = 85 total
    merged_rules = existing_rules + PHP_RULES

    if len(merged_rules) != FULL_RULES_COUNT:
        raise RuntimeError(
            f"Rule count mismatch: expected {FULL_RULES_COUNT}, got {len(merged_rules)}"
        )

    # UPDATE rule_versions with merged rules
    connection.execute(
        sa.text(
            "UPDATE rule_versions SET rules_json = :json WHERE version = :version"
        ),
        {"json": json.dumps(merged_rules), "version": "0.4.0"},
    )
    connection.commit()


def downgrade() -> None:
    """Downgrade: remove PHP rules from v0.4.0, keeping Java + C# + baseline rules."""
    connection = op.get_bind()

    # Fetch current rules for v0.4.0
    result = connection.execute(
        sa.text("SELECT id, rules_json FROM rule_versions WHERE version = :version"),
        {"version": "0.4.0"},
    )
    existing_row = result.first()

    if existing_row:
        existing_rules = (
            json.loads(existing_row[1])
            if isinstance(existing_row[1], str)
            else existing_row[1]
        )

        # Filter out PHP rules (keep all others = 75 rules)
        filtered_rules = [
            r for r in existing_rules if not r.get("id", "").startswith("php-")
        ]

        # After removing PHP rules, we should have 75 (45 baseline + 15 Java + 15 C#)
        if len(filtered_rules) >= 75:
            connection.execute(
                sa.text(
                    "UPDATE rule_versions SET rules_json = :json WHERE version = :version"
                ),
                {"json": json.dumps(filtered_rules), "version": "0.4.0"},
            )
            connection.commit()
