#!/usr/bin/env python3
"""
Intentionally vulnerable code for testing The Loop incident guard.
DO NOT USE IN PRODUCTION.
"""

import sqlite3
from flask import Flask, request

app = Flask(__name__)

# ============================================================================
# VULNERABILITY: injection-001 (SQL via string concatenation)
# ============================================================================
def get_user_by_name(db_path: str, username: str):
    """
    VULNERABLE: SQL injection via string concatenation.
    Rule: injection-001-sql-string-concat will trigger on this.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ❌ VULNERABLE: SQL injection via concatenation
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchall()

# ============================================================================
# VULNERABILITY: injection-002 (eval with dynamic input)
# ============================================================================
def evaluate_expression(user_input: str):
    """
    VULNERABLE: eval() with user-supplied input.
    Rule: injection-002-eval-dynamic-input will trigger on this.
    """
    # ❌ VULNERABLE: eval() with dynamic input
    result = eval(user_input)
    return result

@app.route('/calc')
def calculate():
    """
    VULNERABLE: Direct eval of user input.
    """
    expression = request.args.get('expr', '')
    # ❌ VULNERABLE: eval on request parameter
    return str(eval(expression))
