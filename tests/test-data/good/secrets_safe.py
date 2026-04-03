#!/usr/bin/env python3
"""
Safe code - credentials via environment variables and Secret Manager.
These should NOT trigger missing-safety-check-001 rule.
"""

import os
from typing import Optional

# ============================================================================
# CORRECT: Credentials from environment variables
# ============================================================================

def get_database_url() -> str:
    """
    SAFE: Database URL from environment variable.
    Rule missing-safety-check-001 will NOT trigger.
    """
    # ✅ SAFE: From environment variable
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL not configured")
    return db_url

def get_api_key() -> str:
    """
    SAFE: API key from environment.
    """
    # ✅ SAFE: From environment variable
    api_key = os.environ.get('API_KEY')
    if not api_key:
        raise ValueError("API_KEY not configured")
    return api_key

class Config:
    """
    SAFE: Configuration using environment variables.
    """
    # ✅ SAFE: All secrets from environment
    DATABASE_PASSWORD = os.environ.get('DB_PASSWORD', '')
    STRIPE_SECRET = os.environ.get('STRIPE_SECRET_KEY', '')
    AWS_SECRET = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    OAUTH_TOKEN = os.environ.get('GITHUB_TOKEN', '')

# ============================================================================
# CORRECT: Using Secret Manager (GCP)
# ============================================================================

def get_secret_from_gcp(secret_name: str) -> str:
    """
    SAFE: Retrieve secret from GCP Secret Manager.
    """
    # ✅ SAFE: From GCP Secret Manager (not hardcoded)
    try:
        from google.cloud import secretmanager
        client = secretmanager.SecretManagerServiceClient()
        project_id = os.environ.get('GCP_PROJECT_ID')
        secret_id = secret_name

        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except ImportError:
        raise RuntimeError("google-cloud-secret-manager not installed")

# ============================================================================
# CORRECT: Using Secret Manager (AWS)
# ============================================================================

def get_secret_from_aws(secret_name: str) -> Optional[str]:
    """
    SAFE: Retrieve secret from AWS Secrets Manager.
    """
    # ✅ SAFE: From AWS Secrets Manager (not hardcoded)
    try:
        import boto3
        client = boto3.client('secretsmanager')
        response = client.get_secret_value(SecretId=secret_name)
        return response.get('SecretString')
    except ImportError:
        raise RuntimeError("boto3 not installed")
