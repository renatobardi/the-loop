"""Add 15 Java rules to v0.4.0 (Spec-018 Phase 2)

Revision ID: 016_add_java_rules
Revises: 015_fix_rule_versions_v030_full_rules
Create Date: 2026-04-05

"""

import json
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "016_add_java_rules"
down_revision = "015_fix_rule_versions_v030_full_rules"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add 15 Java rules to v0.4.0, bringing total from 45 to 60 rules."""
    connection = op.get_bind()

    # Idempotency guard: check if rules already exist for v0.4.0
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

        # If already at full count (60), skip safely
        if isinstance(existing_rules, list) and len(existing_rules) >= 60:
            return  # Already patched

        # Corruption detected
        raise RuntimeError(
            f"Version v0.4.0 exists with {len(existing_rules)} rules; expected 60 after Java phase. "
            "Possible data corruption. Manual review required."
        )

    # Hardcoded Java rules (Phase 2)
    JAVA_RULES = [
        {
            "id": "java-injection-001",
            "languages": ["java"],
            "message": "[The Loop] SQL injection via string concatenation with JDBC",
            "severity": "ERROR",
            "patterns": [{"pattern": "$STMT.executeQuery($X + $INPUT)"}],
            "metadata": {"category": "injection", "cwe": "CWE-89"},
        },
        {
            "id": "java-injection-002",
            "languages": ["java"],
            "message": "[The Loop] SQL injection via string interpolation in dynamic SQL",
            "severity": "ERROR",
            "patterns": [{"pattern": "new PreparedStatement($X + $Y)"}],
            "metadata": {"category": "injection", "cwe": "CWE-89"},
        },
        {
            "id": "java-injection-003",
            "languages": ["java"],
            "message": "[The Loop] XPath injection via string concatenation",
            "severity": "ERROR",
            "patterns": [
                {"pattern": "XPathFactory.newInstance().newXPath().compile($X + $INPUT)"}
            ],
            "metadata": {"category": "injection", "cwe": "CWE-643"},
        },
        {
            "id": "java-injection-004",
            "languages": ["java"],
            "message": "[The Loop] Shell command injection via Runtime.exec()",
            "severity": "ERROR",
            "patterns": [{"pattern": 'Runtime.getRuntime().exec("..." + $INPUT)'}],
            "metadata": {"category": "injection", "cwe": "CWE-78"},
        },
        {
            "id": "java-injection-005",
            "languages": ["java"],
            "message": "[The Loop] XXE (XML External Entity) injection risk",
            "severity": "ERROR",
            "patterns": [
                {
                    "pattern": "DocumentBuilderFactory.newInstance().newDocumentBuilder().parse($UNTRUSTED_INPUT)"
                }
            ],
            "metadata": {"category": "injection", "cwe": "CWE-611"},
        },
        {
            "id": "java-crypto-001",
            "languages": ["java"],
            "message": "[The Loop] Weak cryptographic hash MD5 or SHA1",
            "severity": "WARNING",
            "patterns": [{"pattern": "MessageDigest.getInstance(\"MD5\")"}],
            "metadata": {"category": "crypto", "cwe": "CWE-327"},
        },
        {
            "id": "java-crypto-002",
            "languages": ["java"],
            "message": "[The Loop] java.util.Random used for security-sensitive value — use SecureRandom",
            "severity": "ERROR",
            "patterns": [{"pattern": "new Random().nextInt(...)"}],
            "metadata": {"category": "crypto", "cwe": "CWE-338"},
        },
        {
            "id": "java-crypto-003",
            "languages": ["java"],
            "message": "[The Loop] Hardcoded encryption key in source code",
            "severity": "ERROR",
            "patterns": [{"pattern": "String encryptionKey = \"...\";"}],
            "metadata": {"category": "crypto", "cwe": "CWE-798"},
        },
        {
            "id": "java-security-001",
            "languages": ["java"],
            "message": "[The Loop] Hardcoded API key or database credential detected",
            "severity": "ERROR",
            "patterns": [{"pattern": "String API_KEY = \"sk_live_...\";"}],
            "metadata": {"category": "security", "cwe": "CWE-798"},
        },
        {
            "id": "java-security-002",
            "languages": ["java"],
            "message": "[The Loop] TLS certificate verification disabled via X509TrustManager",
            "severity": "ERROR",
            "patterns": [
                {"pattern": "new X509TrustManager() { ... checkServerTrusted(...) {} ... }"}
            ],
            "metadata": {"category": "security", "cwe": "CWE-295"},
        },
        {
            "id": "java-security-003",
            "languages": ["java"],
            "message": "[The Loop] Unsafe deserialization with ObjectInputStream",
            "severity": "ERROR",
            "patterns": [
                {"pattern": "new ObjectInputStream($INPUT).readObject()"}
            ],
            "metadata": {"category": "security", "cwe": "CWE-502"},
        },
        {
            "id": "java-security-004",
            "languages": ["java"],
            "message": "[The Loop] JDBC connection without SSL/TLS enabled",
            "severity": "WARNING",
            "patterns": [
                {"pattern": "DriverManager.getConnection(\"jdbc:mysql://...\")"}
            ],
            "metadata": {"category": "security", "cwe": "CWE-295"},
        },
        {
            "id": "java-perf-001",
            "languages": ["java"],
            "message": "[The Loop] N+1 query pattern — database query inside loop",
            "severity": "WARNING",
            "patterns": [{"pattern": "$DB.execute(...)"}],
            "metadata": {"category": "performance"},
        },
        {
            "id": "java-error-001",
            "languages": ["java"],
            "message": "[The Loop] Exception caught and silently discarded (empty catch block)",
            "severity": "WARNING",
            "patterns": [{"pattern": "catch ($EXCEPTION $E) { }"}],
            "metadata": {"category": "error-handling"},
        },
        {
            "id": "java-config-001",
            "languages": ["java"],
            "message": "[The Loop] Hardcoded production/staging URL in source code",
            "severity": "WARNING",
            "patterns": [{"pattern": "String url = \"https://api.prod...\";"}],
            "metadata": {"category": "config"},
        },
    ]

    # Expected count after Java phase
    FULL_RULES_COUNT = 60  # 45 existing + 15 Java
    JAVA_RULES_COUNT = len(JAVA_RULES)

    if JAVA_RULES_COUNT != 15:
        raise RuntimeError(
            f"Expected 15 Java rules; found {JAVA_RULES_COUNT}. "
            "Data integrity check failed."
        )

    # Fetch existing 45 rules and APPEND Java rules (don't overwrite!)
    existing_result = connection.execute(
        sa.text("SELECT rules_json FROM rule_versions WHERE version = :version"),
        {"version": "v0.4.0"},
    )
    existing_data = existing_result.first()
    if not existing_data:
        raise RuntimeError("v0.4.0 does not exist. Run migration 015 first.")

    existing_rules = (
        json.loads(existing_data[0])
        if isinstance(existing_data[0], str)
        else existing_data[0]
    )

    # Merge: existing 45 + new 15 Java = 60 total
    merged_rules = existing_rules + JAVA_RULES

    if len(merged_rules) != FULL_RULES_COUNT:
        raise RuntimeError(
            f"Rule count mismatch: expected {FULL_RULES_COUNT}, got {len(merged_rules)}"
        )

    # UPDATE rule_versions with merged rules
    connection.execute(
        sa.text(
            "UPDATE rule_versions SET rules_json = :json WHERE version = :version"
        ),
        {"json": json.dumps(merged_rules), "version": "v0.4.0"},
    )
    connection.commit()


def downgrade() -> None:
    """Downgrade: remove Java rules from v0.4.0, keeping only Python rules."""
    connection = op.get_bind()

    # Fetch current rules for v0.4.0
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

        # Filter out Java rules (keep Python + any C# if migration 017 already ran)
        filtered_rules = [
            r for r in existing_rules if not r.get("id", "").startswith("java-")
        ]

        # If we only have Python rules left, we're at 45
        # If we also have C# rules, we'll be at 60 (45 + 15 C#)
        # Both are valid downgrade states
        if len(filtered_rules) >= 45:
            connection.execute(
                sa.text(
                    "UPDATE rule_versions SET rules_json = :json WHERE version = :version"
                ),
                {"json": json.dumps(filtered_rules), "version": "v0.4.0"},
            )
            connection.commit()
