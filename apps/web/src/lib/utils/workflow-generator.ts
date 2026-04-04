/** Generates a GitHub Actions workflow YAML for The Loop Incident Guard. */

export function generateWorkflowYaml(keyPrefix: string): string {
	return `name: "The Loop - Incident Guard"

on:
  pull_request:
    branches: [main, master, develop]
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

env:
  THELOOP_API_TOKEN: \${{ secrets.THELOOP_API_TOKEN }}
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

# Key prefix: ${keyPrefix}
# Go to your repository Settings → Secrets and variables → Actions
# Create a secret named THELOOP_API_TOKEN with the full token shown at key creation

jobs:
  theloop-guard:
    name: "The Loop - Incident Guard"
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - name: Fetch rules
        run: |
          curl -s --max-time 5 \\
            -H "Authorization: Bearer \${{ secrets.THELOOP_API_TOKEN }}" \\
            "https://api.loop.oute.pro/api/v1/rules/latest" \\
            -o /tmp/rules.json || true
      - name: Run scan
        run: |
          pip install semgrep --quiet
          semgrep scan --config /tmp/rules.json --json --output /tmp/results.json || true
`;
}
