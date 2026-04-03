#!/usr/bin/env python3
"""
Intentionally vulnerable code - hardcoded secrets.
Rule: missing-safety-check-001-hardcoded-secret will trigger on these.
"""

# ============================================================================
# VULNERABILITY: missing-safety-check-001 (hardcoded credentials)
# ============================================================================

# ❌ VULNERABLE: Database password hardcoded
DATABASE_URL = "postgresql://admin:super_secret_password@localhost:5432/prod"

# ❌ VULNERABLE: API key hardcoded
API_KEY = "sk-prod-abc123xyz789secretkey"

# ❌ VULNERABLE: Stripe secret hardcoded
STRIPE_SECRET = "sk_live_very_secret_stripe_key_12345"

# ❌ VULNERABLE: AWS credentials
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY"

# ❌ VULNERABLE: OAuth token
OAUTH_TOKEN = "ghp_16C7e42F292c6912E7710c838347Ae178B4a"

class DatabaseConfig:
    """Configuration with hardcoded secrets"""
    password: str = "MyP@ssw0rd123"
    api_key: str = "123-456-789-abc-def-ghi"
