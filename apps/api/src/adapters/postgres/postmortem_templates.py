"""Hardcoded postmortem root cause templates (Phase C MVP).

These 15 templates are built-in and cannot be customized in Phase C.1.
Dynamic templates will be added in Spec-015 (Webhooks + Admin).
"""

from src.domain.models import PostmortumSeverity, RootCauseCategory, RootCauseTemplate

__all__ = ["POSTMORTEM_TEMPLATES"]

POSTMORTEM_TEMPLATES: dict[str, RootCauseTemplate] = {
    "sql-injection": RootCauseTemplate(
        id="sql-injection",
        category=RootCauseCategory.CODE_PATTERN,
        title="SQL Injection",
        description_template=(
            "SQL injection via string concatenation detected. The query was built by "
            "concatenating user input directly into the SQL string (e.g., "
            "'SELECT * FROM users WHERE id = ' + user_id). "
            "Fix: Use parameterized queries or prepared statements."
        ),
        pattern_example=r'execute\(".*"\s\+\s\w+\)',
        severity_default=PostmortumSeverity.ERROR,
    ),
    "n-plus-one-query": RootCauseTemplate(
        id="n-plus-one-query",
        category=RootCauseCategory.CODE_PATTERN,
        title="N+1 Query Pattern",
        description_template=(
            "N+1 query performance issue detected. A query was executed inside a loop, "
            "causing one query per iteration plus one initial query (N+1 total). "
            "Example: fetching user list, then fetching profile for each user in a loop. "
            "Fix: Use JOIN or eager loading (SQLAlchemy joinedload, Django select_related)."
        ),
        pattern_example=None,
        severity_default=PostmortumSeverity.WARNING,
    ),
    "hardcoded-secret": RootCauseTemplate(
        id="hardcoded-secret",
        category=RootCauseCategory.CODE_PATTERN,
        title="Hardcoded Credential/Secret",
        description_template=(
            "Hardcoded credential or secret found in source code "
            "(e.g., API_KEY = 'sk-prod-xyz...'). Secrets should never be committed to "
            "version control. Fix: Move to environment variables (os.environ) or "
            "Secret Manager (GCP, AWS, Vault)."
        ),
        pattern_example=None,
        severity_default=PostmortumSeverity.ERROR,
    ),
    "redos-pattern": RootCauseTemplate(
        id="redos-pattern",
        category=RootCauseCategory.CODE_PATTERN,
        title="Regular Expression Denial of Service (ReDoS)",
        description_template=(
            "Regular expression with catastrophic backtracking detected (e.g., (a+)+). "
            "This pattern can cause exponential time complexity with specially crafted input, "
            "potentially leading to service unavailability. "
            "Fix: Simplify regex or use a dedicated parser. Test with long strings."
        ),
        pattern_example=r"\(\.\+\)\+|\(\.\*\)\+",
        severity_default=PostmortumSeverity.WARNING,
    ),
    "weak-md5": RootCauseTemplate(
        id="weak-md5",
        category=RootCauseCategory.CODE_PATTERN,
        title="Weak Cryptographic Hash (MD5)",
        description_template=(
            "MD5 hash function used for security-sensitive data (passwords, etc). "
            "MD5 is cryptographically broken and should not be used for hashing secrets. "
            "Fix: Use bcrypt, argon2, or PBKDF2 for passwords. Use SHA-256 or SHA-3 "
            "for non-password hashing."
        ),
        pattern_example="hashlib.md5()",
        severity_default=PostmortumSeverity.ERROR,
    ),
    "weak-random": RootCauseTemplate(
        id="weak-random",
        category=RootCauseCategory.CODE_PATTERN,
        title="Weak Random Number Generation",
        description_template=(
            "Non-cryptographic random number generator used for security purposes "
            "(e.g., Math.random() in JS, random.random() in Python). These are "
            "predictable and unsuitable for tokens, nonces, or secrets. "
            "Fix: Use secrets.token_bytes() (Python) or crypto.getRandomValues() (JS)."
        ),
        pattern_example="random.random()|Math.random()",
        severity_default=PostmortumSeverity.ERROR,
    ),
    "tls-verify-false": RootCauseTemplate(
        id="tls-verify-false",
        category=RootCauseCategory.CODE_PATTERN,
        title="TLS/SSL Certificate Verification Disabled",
        description_template=(
            "HTTPS certificate verification was disabled in HTTP client "
            "(e.g., requests.get(..., verify=False)). This opens the door to "
            "man-in-the-middle attacks. Fix: Enable verification (verify=True, "
            "the default) or provide CA bundle path."
        ),
        pattern_example="verify=False",
        severity_default=PostmortumSeverity.ERROR,
    ),
    "hardcoded-jwt": RootCauseTemplate(
        id="hardcoded-jwt",
        category=RootCauseCategory.CODE_PATTERN,
        title="Hardcoded JWT Secret",
        description_template=(
            "JWT signing secret was hardcoded in source code. Anyone with access "
            "to the code can forge valid JWT tokens. "
            "Fix: Use environment variable or Secret Manager for JWT_SECRET."
        ),
        pattern_example=r'JWT_SECRET\s*=\s*["\'].*["\']',
        severity_default=PostmortumSeverity.ERROR,
    ),
    "cors-wildcard": RootCauseTemplate(
        id="cors-wildcard",
        category=RootCauseCategory.CODE_PATTERN,
        title="CORS Wildcard Origin",
        description_template=(
            "CORS (Cross-Origin Resource Sharing) configured to allow requests from "
            "any origin (Access-Control-Allow-Origin: *). This can expose sensitive "
            "endpoints to any website. Fix: Whitelist specific trusted origins "
            "instead of using wildcard."
        ),
        pattern_example=r"Access-Control-Allow-Origin.*\*",
        severity_default=PostmortumSeverity.ERROR,
    ),
    "sql-without-timeout": RootCauseTemplate(
        id="sql-without-timeout",
        category=RootCauseCategory.CODE_PATTERN,
        title="SQL Query Without Timeout",
        description_template=(
            "Database query executed without timeout, risking resource exhaustion. "
            "A slow or hung query can block the entire connection pool. "
            "Fix: Add explicit timeout (e.g., cursor.execute(..., timeout=30))."
        ),
        pattern_example=None,
        severity_default=PostmortumSeverity.WARNING,
    ),
    "docker-root": RootCauseTemplate(
        id="docker-root",
        category=RootCauseCategory.INFRASTRUCTURE,
        title="Docker Container Running as Root",
        description_template=(
            "Docker container runs as root (UID 0) instead of a non-privileged "
            "user. If the container is compromised, attacker has root access. "
            "Fix: Create a non-root user in Dockerfile (RUN useradd -m appuser) "
            "and USER appuser."
        ),
        pattern_example=None,
        severity_default=PostmortumSeverity.ERROR,
    ),
    "hardcoded-url": RootCauseTemplate(
        id="hardcoded-url",
        category=RootCauseCategory.CODE_PATTERN,
        title="Hardcoded API URL or Domain",
        description_template=(
            "API URL or external service domain was hardcoded in source code. "
            "This makes it difficult to change endpoints (dev vs prod) or migrate "
            "services. Fix: Move to environment variable (API_BASE_URL, "
            "SERVICE_ENDPOINT)."
        ),
        pattern_example=r"https?://[a-z.-]+\.[a-z]{2,}",
        severity_default=PostmortumSeverity.WARNING,
    ),
    "debug-enabled-prod": RootCauseTemplate(
        id="debug-enabled-prod",
        category=RootCauseCategory.CODE_PATTERN,
        title="Debug Mode Enabled in Production",
        description_template=(
            "Debug flag (DEBUG = True, FLASK_DEBUG=1, etc.) was left enabled in "
            "production. Debug mode may expose stack traces, environment variables, "
            "and other sensitive information. Fix: Ensure DEBUG is False in "
            "production (use environment variable to control)."
        ),
        pattern_example="DEBUG\\s*=\\s*True|FLASK_DEBUG",
        severity_default=PostmortumSeverity.ERROR,
    ),
    "xxe-parsing": RootCauseTemplate(
        id="xxe-parsing",
        category=RootCauseCategory.CODE_PATTERN,
        title="XXE (XML External Entity) Vulnerability",
        description_template=(
            "XML parsing without disabling external entity processing. "
            "Attacker can exploit XXE to read local files or cause DoS. "
            "Fix: Use defusedxml library or disable DTD/external entities in XML parser."
        ),
        pattern_example="ElementTree.parse\\(|lxml.etree",
        severity_default=PostmortumSeverity.ERROR,
    ),
    "unsafe-deserialization": RootCauseTemplate(
        id="unsafe-deserialization",
        category=RootCauseCategory.CODE_PATTERN,
        title="Unsafe Object Deserialization",
        description_template=(
            "Untrusted data deserialized using unsafe methods (pickle.loads, "
            "yaml.load with Loader not safe). Attacker can achieve remote code "
            "execution by crafting malicious serialized data. Fix: Use "
            "pickle.loads with restrict=True, yaml.safe_load, or json.loads."
        ),
        pattern_example="pickle.load|yaml.load",
        severity_default=PostmortumSeverity.ERROR,
    ),
}
