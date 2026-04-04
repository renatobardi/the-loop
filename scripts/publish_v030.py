#!/usr/bin/env python3
"""Publish v0.3.0 rules from .semgrep/theloop-rules.yml.bak to the live API.

Usage:
    python scripts/publish_v030.py <FIREBASE_ID_TOKEN>

How to get the Firebase token:
    1. Abra loop.oute.pro no browser (logado como admin)
    2. DevTools → Network → filtre por "api.loop.oute.pro"
    3. Copie o valor do header "Authorization" de qualquer request (sem o "Bearer ")

    Ou via console do browser (na aba Console):
        (await (await import('/@firebase/auth')).getAuth().currentUser?.getIdToken(true))
"""

import json
import sys
import urllib.request
import urllib.error

import yaml

API_BASE = "https://api.loop.oute.pro"
BAK_FILE = ".semgrep/theloop-rules.yml.bak"
VERSION = "0.3.0"
NOTES = "Phase C: 45 rules (20 Python + 15 JS/TS + 10 Go)"


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    token = sys.argv[1].removeprefix("Bearer ")

    print(f"📖 Reading rules from {BAK_FILE}...")
    with open(BAK_FILE, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    rules = data.get("rules", [])
    print(f"✅ Found {len(rules)} rules")

    payload = json.dumps({
        "version": VERSION,
        "rules": rules,
        "notes": NOTES,
    }).encode()

    print(f"🚀 Publishing v{VERSION} to {API_BASE}...")
    req = urllib.request.Request(
        f"{API_BASE}/api/v1/rules/publish",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"✅ Published! version={result.get('version')} rules={result.get('rules_count')}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"❌ HTTP {e.code}: {body}")
        sys.exit(1)

    print()
    print("✅ Version is now live and active.")


if __name__ == "__main__":
    main()
