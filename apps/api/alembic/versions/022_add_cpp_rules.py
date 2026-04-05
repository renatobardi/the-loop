"""Add 10 C/C++ rules to v0.4.0 (Spec-017 Phase 7B)

Revision ID: 022
Revises: 021
Create Date: 2026-04-05

"""

import json
from alembic import op
import sqlalchemy as sa

revision = "022"
down_revision = "021"
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
        if rule_count >= 122:
            return  # Already patched — migration 022 completed (113 + 9 = 122)
        if rule_count not in (45, 60, 75, 85, 95, 105, 113):
            raise RuntimeError(f"Version v0.4.0 exists with {rule_count} rules; expected intermediate state.")

    CPP_RULES = [
        {"id": "cpp-injection-001", "languages": ["c", "cpp"], "message": "[The Loop] SQL injection via string formatting in SQL query", "severity": "ERROR", "patterns": [{"pattern-either": ["sprintf($BUFFER, \"SELECT ... %s ...\", $INPUT)", "sqlite3_prepare_v2($DB, \"...\" + $INPUT, ...)"]}], "metadata": {"category": "injection", "cwe": "CWE-89"}},
        {"id": "cpp-injection-002", "languages": ["c", "cpp"], "message": "[The Loop] Command injection via system() with unsanitized input", "severity": "ERROR", "patterns": [{"pattern": "system($CMD)"}], "metadata": {"category": "injection", "cwe": "CWE-78"}},
        {"id": "cpp-memory-001", "languages": ["c", "cpp"], "message": "[The Loop] Buffer overflow risk — use of strcpy() instead of strncpy()", "severity": "ERROR", "patterns": [{"pattern": "strcpy($DST, $SRC)"}], "metadata": {"category": "memory-safety", "cwe": "CWE-120"}},
        {"id": "cpp-memory-002", "languages": ["c", "cpp"], "message": "[The Loop] Use-after-free — pointer used after deletion", "severity": "ERROR", "patterns": [{"pattern-regex": "delete.*;"}], "metadata": {"category": "memory-safety", "cwe": "CWE-416"}},
        {"id": "cpp-memory-003", "languages": ["c", "cpp"], "message": "[The Loop] Memory leak — allocated but not freed", "severity": "WARNING", "patterns": [{"pattern": "new $TYPE(...)"}], "metadata": {"category": "memory-safety", "cwe": "CWE-401"}},
        {"id": "cpp-crypto-001", "languages": ["c", "cpp"], "message": "[The Loop] Hardcoded encryption key or IV in source", "severity": "ERROR", "patterns": [{"pattern-regex": "(const\\s+)?unsigned char.*key.*=.*\\{[0-9x,\\s]+\\}"}], "metadata": {"category": "crypto", "cwe": "CWE-798"}},
        {"id": "cpp-crypto-002", "languages": ["c", "cpp"], "message": "[The Loop] Weak random number generation (rand instead of secure source)", "severity": "WARNING", "patterns": [{"pattern": "rand()"}], "metadata": {"category": "crypto", "cwe": "CWE-338"}},
        {"id": "cpp-error-001", "languages": ["c", "cpp"], "message": "[The Loop] Unchecked return value from system function — check errno", "severity": "WARNING", "patterns": [{"pattern-regex": "(open|read|write|recv|send)\\([^)]*\\)"}], "metadata": {"category": "error-handling"}},
        {"id": "cpp-error-002", "languages": ["c", "cpp"], "message": "[The Loop] Missing null pointer check before dereference", "severity": "ERROR", "patterns": [{"pattern-regex": "->[a-zA-Z_]"}], "metadata": {"category": "error-handling", "cwe": "CWE-476"}},
    ]

    # Only 9 C/C++ rules in YAML (matched count)
    FULL_RULES_COUNT = 122  # 113 + 9
    if len(CPP_RULES) != 9:
        raise RuntimeError(f"Expected 9 C/C++ rules; found {len(CPP_RULES)}.")

    existing_result = connection.execute(
        sa.text("SELECT rules_json FROM rule_versions WHERE version = :version"),
        {"version": "0.4.0"},
    )
    existing_data = existing_result.first()
    if not existing_data:
        raise RuntimeError("v0.4.0 does not exist.")

    existing_rules = json.loads(existing_data[0]) if isinstance(existing_data[0], str) else existing_data[0]
    merged_rules = existing_rules + CPP_RULES

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
        filtered_rules = [r for r in existing_rules if not r.get("id", "").startswith("cpp-")]
        if len(filtered_rules) >= 113:
            connection.execute(
                sa.text("UPDATE rule_versions SET rules_json = :json WHERE version = :version"),
                {"json": json.dumps(filtered_rules), "version": "0.4.0"},
            )
            connection.commit()
