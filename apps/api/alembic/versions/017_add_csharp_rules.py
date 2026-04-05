"""Add 15 C# rules to v0.4.0 (Spec-018 Phase 3)

Revision ID: 017
Revises: 016
Create Date: 2026-04-05

"""

import json
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "017"
down_revision = "016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add 15 C# rules to v0.4.0, bringing total from 60 to 75 rules."""
    connection = op.get_bind()

    # Idempotency guard
    existing_check = connection.execute(
        sa.text("SELECT id, rules_json FROM rule_versions WHERE version = :version"),
        {"version": "v0.4.0"},
    )
    existing_row = existing_check.first()

    if existing_row:
        existing_rules = (
            json.loads(existing_row[1])
            if isinstance(existing_row[1], str)
            else existing_row[1]
        )

        if isinstance(existing_rules, list) and len(existing_rules) >= 75:
            return  # Already patched

        raise RuntimeError(
            f"Version v0.4.0 exists with {len(existing_rules)} rules; expected 75 after C# phase."
        )

    # Hardcoded C# rules (Phase 3)
    CSHARP_RULES = [
        {
            "id": "csharp-sql-001",
            "languages": ["csharp"],
            "message": "[The Loop] SQL injection via string concatenation with SqlCommand",
            "severity": "ERROR",
            "patterns": [{"pattern": "new SqlCommand(\"...\" + $INPUT, ...)"}],
            "metadata": {"category": "injection", "cwe": "CWE-89"},
        },
        {
            "id": "csharp-linq-001",
            "languages": ["csharp"],
            "message": "[The Loop] LINQ injection via dynamic expression trees",
            "severity": "ERROR",
            "patterns": [{"pattern": "$CTX.FromSqlRaw($X + $INPUT)"}],
            "metadata": {"category": "injection", "cwe": "CWE-89"},
        },
        {
            "id": "csharp-injection-002",
            "languages": ["csharp"],
            "message": "[The Loop] XPath injection in .NET XML parsing",
            "severity": "ERROR",
            "patterns": [{"pattern": "$XPATH.Compile($X + $INPUT)"}],
            "metadata": {"category": "injection", "cwe": "CWE-643"},
        },
        {
            "id": "csharp-crypto-001",
            "languages": ["csharp"],
            "message": "[The Loop] Weak hash algorithm (MD5 or SHA1) in cryptography",
            "severity": "WARNING",
            "patterns": [{"pattern": "MD5.Create()"}],
            "metadata": {"category": "crypto", "cwe": "CWE-327"},
        },
        {
            "id": "csharp-crypto-002",
            "languages": ["csharp"],
            "message": "[The Loop] Hardcoded encryption key in C# code",
            "severity": "ERROR",
            "patterns": [{"pattern": "String encryptionKey = \"...\";"}],
            "metadata": {"category": "crypto", "cwe": "CWE-798"},
        },
        {
            "id": "csharp-security-001",
            "languages": ["csharp"],
            "message": "[The Loop] Hardcoded credential (password, API key) detected",
            "severity": "ERROR",
            "patterns": [{"pattern": "String password = \"Admin@123456\";"}],
            "metadata": {"category": "security", "cwe": "CWE-798"},
        },
        {
            "id": "csharp-security-002",
            "languages": ["csharp"],
            "message": "[The Loop] TLS certificate validation disabled in HttpClientHandler",
            "severity": "ERROR",
            "patterns": [
                {
                    "pattern": "new HttpClientHandler { ServerCertificateCustomValidationCallback = ... }"
                }
            ],
            "metadata": {"category": "security", "cwe": "CWE-295"},
        },
        {
            "id": "csharp-security-003",
            "languages": ["csharp"],
            "message": "[The Loop] Unsafe BinaryFormatter deserialization",
            "severity": "ERROR",
            "patterns": [
                {"pattern": "new BinaryFormatter().Deserialize($STREAM)"}
            ],
            "metadata": {"category": "security", "cwe": "CWE-502"},
        },
        {
            "id": "csharp-perf-001",
            "languages": ["csharp"],
            "message": "[The Loop] N+1 query pattern in Entity Framework loop",
            "severity": "WARNING",
            "patterns": [{"pattern": "$DB.Database.ExecuteSql(...)"}],
            "metadata": {"category": "performance"},
        },
        {
            "id": "csharp-perf-002",
            "languages": ["csharp"],
            "message": "[The Loop] Missing .AsNoTracking() in readonly Entity Framework queries",
            "severity": "WARNING",
            "patterns": [
                {"pattern": "$CTX.Set<$T>().Where(...).FirstOrDefault()"}
            ],
            "metadata": {"category": "performance"},
        },
        {
            "id": "csharp-error-001",
            "languages": ["csharp"],
            "message": "[The Loop] Overly broad exception catch (catching Exception instead of specific type)",
            "severity": "WARNING",
            "patterns": [{"pattern": "catch (Exception) { ... }"}],
            "metadata": {"category": "error-handling"},
        },
        {
            "id": "csharp-error-002",
            "languages": ["csharp"],
            "message": "[The Loop] Swallowing exception without logging",
            "severity": "WARNING",
            "patterns": [{"pattern": "catch (...) { }"}],
            "metadata": {"category": "error-handling"},
        },
        {
            "id": "csharp-config-001",
            "languages": ["csharp"],
            "message": "[The Loop] Hardcoded production URL in application configuration",
            "severity": "WARNING",
            "patterns": [{"pattern": "\"https://api.prod...\""}],
            "metadata": {"category": "config"},
        },
        {
            "id": "csharp-injection-003",
            "languages": ["csharp"],
            "message": "[The Loop] Command injection via ProcessStartInfo with UseShellExecute",
            "severity": "ERROR",
            "patterns": [{"pattern": "new ProcessStartInfo($CMD) { UseShellExecute = true }"}],
            "metadata": {"category": "injection", "cwe": "CWE-78"},
        },
        {
            "id": "csharp-security-004",
            "languages": ["csharp"],
            "message": "[The Loop] SQL connection without encryption (Encrypt=false)",
            "severity": "WARNING",
            "patterns": [{"pattern": "\"Server=...;Encrypt=false;\""}],
            "metadata": {"category": "security", "cwe": "CWE-295"},
        },
    ]

    FULL_RULES_COUNT = 75  # 60 from Java + 15 C#
    CSHARP_RULES_COUNT = len(CSHARP_RULES)

    if CSHARP_RULES_COUNT != 15:
        raise RuntimeError(f"Expected 15 C# rules; found {CSHARP_RULES_COUNT}.")

    # Fetch existing 60 rules (45 Python + 15 Java) and APPEND C# rules (don't overwrite!)
    existing_result = connection.execute(
        sa.text("SELECT rules_json FROM rule_versions WHERE version = :version"),
        {"version": "v0.4.0"},
    )
    existing_data = existing_result.first()
    if not existing_data:
        raise RuntimeError("v0.4.0 does not exist. Run migration 016 first.")

    existing_rules = (
        json.loads(existing_data[0])
        if isinstance(existing_data[0], str)
        else existing_data[0]
    )

    # Merge: existing 60 (45 Python + 15 Java) + new 15 C# = 75 total
    merged_rules = existing_rules + CSHARP_RULES

    if len(merged_rules) != FULL_RULES_COUNT:
        raise RuntimeError(
            f"Rule count mismatch: expected {FULL_RULES_COUNT}, got {len(merged_rules)}"
        )

    connection.execute(
        sa.text(
            "UPDATE rule_versions SET rules_json = :json WHERE version = :version"
        ),
        {"json": json.dumps(merged_rules), "version": "v0.4.0"},
    )
    connection.commit()


def downgrade() -> None:
    """Downgrade: remove C# rules from v0.4.0, keeping Java + Python rules."""
    connection = op.get_bind()

    result = connection.execute(
        sa.text("SELECT id, rules_json FROM rule_versions WHERE version = :version"),
        {"version": "v0.4.0"},
    )
    existing_row = result.first()

    if existing_row:
        existing_rules = (
            json.loads(existing_row[1])
            if isinstance(existing_row[1], str)
            else existing_row[1]
        )

        # Filter out C# rules (keep Python + Java rules = 60 rules)
        filtered_rules = [
            r for r in existing_rules if not r.get("id", "").startswith("csharp-")
        ]

        # After removing C# rules, we should have 60 (45 Python + 15 Java)
        if len(filtered_rules) == 60:
            connection.execute(
                sa.text(
                    "UPDATE rule_versions SET rules_json = :json WHERE version = :version"
                ),
                {"json": json.dumps(filtered_rules), "version": "v0.4.0"},
            )
            connection.commit()
