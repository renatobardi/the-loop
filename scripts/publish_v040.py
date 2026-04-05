#!/usr/bin/env python3
"""Publish v0.4.0 rules from .semgrep/theloop-rules.yml.bak to the live API.

Usage:
    python scripts/publish_v040.py <FIREBASE_ID_TOKEN>

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
VERSION = "0.4.0"
NOTES = "Phase 2-7: 122 total rules (45 base + 15 Java + 15 C# + 10 PHP + 10 Ruby + 10 Kotlin + 8 Rust + 9 C/C++)"


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    token = sys.argv[1].removeprefix("Bearer ")

    print(f"📖 Reading rules from {BAK_FILE}...")
    with open(BAK_FILE, encoding="utf-8") as f:  # nosemgrep: path-traversal-001
        data = yaml.safe_load(f)

    rules = data.get("rules", [])
    print(f"✅ Found {len(rules)} rules")

    # Idempotency check: don't republish if v0.4.0 already exists with >= expected rules
    print(f"🔍 Checking if v{VERSION} already exists...")
    try:
        check_req = urllib.request.Request(
            f"{API_BASE}/api/v1/rules/{VERSION}",
            method="GET",
        )
        with urllib.request.urlopen(check_req) as resp:
            existing = json.loads(resp.read())
            existing_count = len(existing.get("rules", []))
            if existing_count >= len(rules):
                print(f"✅ v{VERSION} already exists with {existing_count} rules — skipping publish (API does not support updates)")
                return
            else:
                print(f"❌ v{VERSION} exists but has {existing_count} rules (expected {len(rules)}) — cannot update via API")
                sys.exit(1)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"ℹ️  v{VERSION} not found — will create new")
        else:
            print(f"⚠️  Could not check existing version: HTTP {e.code} — proceeding with publish")

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
