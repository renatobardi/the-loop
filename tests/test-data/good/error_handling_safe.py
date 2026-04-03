#!/usr/bin/env python3
"""
Safe code - proper error handling with specific exceptions.
These should NOT trigger missing-error-handling-001 rule.
"""

import requests
import json
import logging

# Setup logging
logger = logging.getLogger(__name__)

# ============================================================================
# CORRECT: Specific exception handling with logging
# ============================================================================

def fetch_user_data(user_id: int):
    """
    SAFE: Specific exception handling with logging.
    Rule missing-error-handling-001 will NOT trigger.
    """
    try:
        response = requests.get(
            f'https://api.example.com/users/{user_id}',
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.Timeout as e:
        # ✅ SAFE: Specific exception with logging
        logger.error(f"Request timeout for user {user_id}: {e}")
        raise
    except requests.HTTPError as e:
        # ✅ SAFE: Specific exception with logging
        logger.error(f"HTTP error for user {user_id}: {e}")
        raise
    except Exception as e:
        # ✅ SAFE: General exception (not bare except) with logging and re-raise
        logger.exception(f"Unexpected error fetching user {user_id}")
        raise RuntimeError(f"Failed to fetch user data: {e}") from e

def parse_config_file(filepath: str):
    """
    SAFE: Specific exception handling for file operations.
    """
    try:
        with open(filepath) as f:
            config = json.load(f)
            return config
    except FileNotFoundError as e:
        # ✅ SAFE: Specific exception
        logger.warning(f"Config file not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        # ✅ SAFE: Specific exception
        logger.error(f"Invalid JSON in config file: {e}")
        return {}

def process_batch(items: list):
    """
    SAFE: Specific exception handling in loop.
    """
    results = []
    for item in items:
        try:
            result = int(item) * 2
            results.append(result)
        except ValueError as e:
            # ✅ SAFE: Specific exception, log and continue
            logger.warning(f"Could not convert {item}: {e}")
            continue
        except Exception as e:
            # ✅ SAFE: Generic exception with logging and re-raise
            logger.exception(f"Unexpected error processing {item}")
            raise
    return results

def safe_operation_with_cleanup():
    """
    SAFE: try-except-finally with proper cleanup.
    """
    db = None
    try:
        # ✅ SAFE: Specific exception handling
        db = connect_database()
        result = db.query()
        return result
    except ConnectionError as e:
        logger.error(f"Database connection failed: {e}")
        raise
    except Exception as e:
        logger.exception("Unexpected database error")
        raise
    finally:
        # ✅ SAFE: Cleanup always runs
        if db:
            db.close()

def connect_database():
    """Helper to connect database."""
    pass
