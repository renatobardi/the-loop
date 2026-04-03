#!/usr/bin/env python3
"""
Safe code - shell command execution without injection risk.
These should NOT trigger unsafe-api-usage-001 rule.
"""

import subprocess
import shlex
import os

# ============================================================================
# CORRECT: subprocess with argument list (shell=False)
# ============================================================================

def run_user_command(user_cmd: str):
    """
    SAFE: subprocess.run with list of arguments (no shell=True).
    Rule unsafe-api-usage-001 will NOT trigger.
    """
    # ✅ SAFE: subprocess.run with shell=False and list
    try:
        result = subprocess.run(
            user_cmd.split(),  # Split into argument list
            shell=False,       # Explicit - no shell
            capture_output=True,
            check=True
        )
        return result.stdout.decode()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {e}")

def compress_file(filename: str):
    """
    SAFE: subprocess with explicit argument list.
    """
    # ✅ SAFE: Arguments as list, no shell=True
    subprocess.run(
        ['tar', '-czf', f'{filename}.tar.gz', filename],
        shell=False,
        check=True
    )

def execute_pipe(input_file: str):
    """
    SAFE: Pipes implemented without shell=True.
    """
    # ✅ SAFE: No shell=True, explicit processes
    cat = subprocess.Popen(
        ['cat', input_file],
        stdout=subprocess.PIPE,
        shell=False
    )
    grep = subprocess.run(
        ['grep', 'pattern'],
        stdin=cat.stdout,
        shell=False
    )
    return grep.returncode == 0

def run_with_env(program: str, **kwargs):
    """
    SAFE: subprocess with environment variables, no shell.
    """
    # ✅ SAFE: shell=False, explicit env
    env = os.environ.copy()
    env.update(kwargs)
    subprocess.run(
        [program],
        shell=False,
        env=env,
        check=True
    )
