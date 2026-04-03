#!/usr/bin/env python3
"""
Safe code - correct patterns for injection prevention.
These should NOT trigger any rules.
"""

import sqlite3
from flask import Flask, request
import ast

app = Flask(__name__)

# ============================================================================
# CORRECT: SQL injection prevention via parameterized queries
# ============================================================================

def get_user_by_name(db_path: str, username: str):
    """
    SAFE: Using parameterized queries.
    Rule injection-001 will NOT trigger.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ✅ SAFE: Parameterized query with placeholders
    query = "SELECT * FROM users WHERE name = ?"
    cursor.execute(query, (username,))
    return cursor.fetchall()

# ============================================================================
# CORRECT: eval() replacement with safe alternatives
# ============================================================================

def evaluate_expression(user_input: str):
    """
    SAFE: Using ast.literal_eval instead of eval.
    Rule injection-002 will NOT trigger.
    """
    try:
        # ✅ SAFE: ast.literal_eval only evaluates literals
        result = ast.literal_eval(user_input)
        return result
    except (ValueError, SyntaxError):
        raise ValueError("Invalid expression")

def evaluate_math(user_input: str):
    """
    SAFE: Explicit expression evaluation without eval.
    """
    # ✅ SAFE: No eval, explicit parsing
    import operator
    import re

    # Only allow numbers and basic operators
    if not re.match(r'^[\d+\-*/().\s]+$', user_input):
        raise ValueError("Invalid characters")

    # Use a safe evaluator
    return _safe_eval(user_input)

def _safe_eval(expr):
    """Safe expression evaluator without eval()."""
    # Implementation here
    pass
