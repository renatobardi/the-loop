#!/usr/bin/env python3
"""
Intentionally vulnerable code - shell injection patterns.
"""

import os
import subprocess

# ============================================================================
# VULNERABILITY: unsafe-api-usage-001 (shell=True with variables)
# ============================================================================

def run_user_command(user_cmd: str):
    """
    VULNERABLE: os.system() with user input.
    Rule: unsafe-api-usage-001-shell-injection will trigger.
    """
    # ❌ VULNERABLE: os.system with user input
    os.system(user_cmd)

def compress_file(filename: str):
    """
    VULNERABLE: subprocess with shell=True and variable.
    Rule: unsafe-api-usage-001-shell-injection will trigger.
    """
    # ❌ VULNERABLE: shell=True with user input
    cmd = f"tar -czf {filename}.tar.gz {filename}"
    subprocess.run(cmd, shell=True)

def execute_pipe(input_file: str):
    """
    VULNERABLE: subprocess.call with shell=True.
    """
    # ❌ VULNERABLE: subprocess.call with shell=True
    subprocess.call(f"cat {input_file} | grep pattern", shell=True)

def popen_command(cmd: str):
    """
    VULNERABLE: os.popen with user input.
    """
    # ❌ VULNERABLE: os.popen
    result = os.popen(cmd)
    return result.read()
