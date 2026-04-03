#!/usr/bin/env python3
"""
Intentionally vulnerable code - missing error handling.
Rule: missing-error-handling-001-bare-except will trigger.
"""

import requests
import json

# ============================================================================
# VULNERABILITY: missing-error-handling-001 (bare except blocks)
# ============================================================================

def fetch_user_data(user_id: int):
    """
    VULNERABLE: Bare except that swallows all errors.
    Rule: missing-error-handling-001-bare-except will trigger.
    """
    try:
        response = requests.get(f'https://api.example.com/users/{user_id}', timeout=5)
        response.raise_for_status()
        return response.json()
    except:
        # ❌ VULNERABLE: bare except clause
        pass

def parse_config_file(filepath: str):
    """
    VULNERABLE: Bare except hiding JSON parsing errors.
    """
    try:
        with open(filepath) as f:
            config = json.load(f)
            return config
    except:
        # ❌ VULNERABLE: bare except
        return {}

def process_batch(items: list):
    """
    VULNERABLE: Bare except in loop.
    """
    results = []
    for item in items:
        try:
            # Some processing
            result = int(item) * 2
            results.append(result)
        except:
            # ❌ VULNERABLE: bare except
            continue
    return results

def risky_operation():
    """
    VULNERABLE: Multiple bare except clauses.
    """
    try:
        x = 1 / 0
    except:
        pass

    try:
        y = undefined_variable
    except:
        pass
