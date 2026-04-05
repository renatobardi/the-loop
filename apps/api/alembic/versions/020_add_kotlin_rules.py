"""Add 10 Kotlin rules to v0.4.0 (Spec-017 Phase 6)

Revision ID: 020
Revises: 019
Create Date: 2026-04-05

"""

import json
from alembic import op
import sqlalchemy as sa

revision = "020"
down_revision = "019"
branch_labels = None
depends_on = None

def upgrade() -> None:
    connection = op.get_bind()
    existing_check = connection.execute(
        sa.text("SELECT id, rules_json FROM rule_versions WHERE version = :version"),
        {"version": "0.4.0"},
    )
    existing_row = existing_check.first()
    if existing_row:
        existing_rules = json.loads(existing_row[1]) if isinstance(existing_row[1], str) else existing_row[1]
        rule_count = len(existing_rules) if isinstance(existing_rules, list) else 0
        if rule_count >= 105:
            return
        if rule_count not in (45, 60, 75, 85, 95):
            raise RuntimeError(f"Version v0.4.0 exists with {rule_count} rules; expected intermediate state.")

    KOTLIN_RULES = [
        {"id": "kotlin-injection-001", "languages": ["kotlin"], "message": "[The Loop] SQL injection via string concatenation in JDBC", "severity": "ERROR", "patterns": [{"pattern-either": ["connection.createStatement().executeQuery(\"...\" + $INPUT)", "statement.execute(\"...\" + $INPUT)"]}], "metadata": {"category": "injection", "cwe": "CWE-89"}},
        {"id": "kotlin-injection-002", "languages": ["kotlin"], "message": "[The Loop] Runtime.getRuntime().exec() with unvalidated input", "severity": "ERROR", "patterns": [{"pattern": "Runtime.getRuntime().exec($CMD)"}], "metadata": {"category": "injection", "cwe": "CWE-78"}},
        {"id": "kotlin-injection-003", "languages": ["kotlin"], "message": "[The Loop] Unsafe reflection with external input", "severity": "ERROR", "patterns": [{"pattern": "Class.forName($INPUT).newInstance()"}], "metadata": {"category": "injection", "cwe": "CWE-470"}},
        {"id": "kotlin-crypto-001", "languages": ["kotlin"], "message": "[The Loop] Weak hash algorithm (MD5 or SHA1) in MessageDigest", "severity": "WARNING", "patterns": [{"pattern-either": ["MessageDigest.getInstance(\"MD5\")", "MessageDigest.getInstance(\"SHA1\")"]}], "metadata": {"category": "crypto", "cwe": "CWE-327"}},
        {"id": "kotlin-crypto-002", "languages": ["kotlin"], "message": "[The Loop] java.util.Random instead of SecureRandom for secrets", "severity": "ERROR", "patterns": [{"pattern": "Random().nextInt(...)"}], "metadata": {"category": "crypto", "cwe": "CWE-338"}},
        {"id": "kotlin-security-001", "languages": ["kotlin"], "message": "[The Loop] TLS verification disabled", "severity": "ERROR", "patterns": [{"pattern": "setDefaultHostnameVerifier { _, _ -> true }"}], "metadata": {"category": "security", "cwe": "CWE-295"}},
        {"id": "kotlin-security-002", "languages": ["kotlin"], "message": "[The Loop] Hardcoded credential in code", "severity": "ERROR", "patterns": [{"pattern-regex": "val\\s+(password|apiKey|secret)\\s*=\\s*['\"][^'\"]+['\"]"}], "metadata": {"category": "security", "cwe": "CWE-798"}},
        {"id": "kotlin-security-003", "languages": ["kotlin"], "message": "[The Loop] Unsafe deserialization with ObjectInputStream", "severity": "ERROR", "patterns": [{"pattern": "ObjectInputStream($STREAM).readObject()"}], "metadata": {"category": "security", "cwe": "CWE-502"}},
        {"id": "kotlin-error-001", "languages": ["kotlin"], "message": "[The Loop] Coroutine launched without error handling", "severity": "WARNING", "patterns": [{"pattern": "GlobalScope.launch { ... }"}], "metadata": {"category": "error-handling"}},
        {"id": "kotlin-config-001", "languages": ["kotlin"], "message": "[The Loop] Hardcoded URL or endpoint in code", "severity": "WARNING", "patterns": [{"pattern-regex": "val.*url.*=.*['\"]https?://.*['\"]"}], "metadata": {"category": "config"}},
    ]

    FULL_RULES_COUNT = 105
    if len(KOTLIN_RULES) != 10:
        raise RuntimeError(f"Expected 10 Kotlin rules; found {len(KOTLIN_RULES)}.")

    existing_result = connection.execute(
        sa.text("SELECT rules_json FROM rule_versions WHERE version = :version"),
        {"version": "0.4.0"},
    )
    existing_data = existing_result.first()
    if not existing_data:
        raise RuntimeError("v0.4.0 does not exist.")

    existing_rules = json.loads(existing_data[0]) if isinstance(existing_data[0], str) else existing_data[0]
    merged_rules = existing_rules + KOTLIN_RULES

    if len(merged_rules) != FULL_RULES_COUNT:
        raise RuntimeError(f"Rule count mismatch: expected {FULL_RULES_COUNT}, got {len(merged_rules)}")

    connection.execute(
        sa.text("UPDATE rule_versions SET rules_json = :json WHERE version = :version"),
        {"json": json.dumps(merged_rules), "version": "0.4.0"},
    )
    connection.commit()

def downgrade() -> None:
    connection = op.get_bind()
    result = connection.execute(
        sa.text("SELECT id, rules_json FROM rule_versions WHERE version = :version"),
        {"version": "0.4.0"},
    )
    existing_row = result.first()
    if existing_row:
        existing_rules = json.loads(existing_row[1]) if isinstance(existing_row[1], str) else existing_row[1]
        filtered_rules = [r for r in existing_rules if not r.get("id", "").startswith("kotlin-")]
        if len(filtered_rules) >= 95:
            connection.execute(
                sa.text("UPDATE rule_versions SET rules_json = :json WHERE version = :version"),
                {"json": json.dumps(filtered_rules), "version": "0.4.0"},
            )
            connection.commit()
