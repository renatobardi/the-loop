<script lang="ts">
	import DocSection from '$lib/components/docs/DocSection.svelte';
	import CodeBlock from '$lib/components/docs/CodeBlock.svelte';

	const workflowYaml = `name: "The Loop — Incident Guard"

on:
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  semgrep-scan:
    name: "Scan — Static Rules"
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Fetch rules from API
        id: fetch_rules
        run: |
          VERSION="\${{ vars.THELOOP_RULES_VERSION || 'latest' }}"

          curl -s --max-time 5 --connect-timeout 2 \\
            -H "Authorization: Bearer \${{ secrets.THELOOP_API_TOKEN }}" \\
            "https://api.loop.oute.pro/api/v1/rules/\${VERSION}" \\
            -o /tmp/rules.json || true

          if python3 -c "import json; json.load(open('/tmp/rules.json'))" 2>/dev/null; then
            echo "fallback=false" >> $GITHUB_OUTPUT
          else
            echo "fallback=true" >> $GITHUB_OUTPUT
          fi

      - name: Convert JSON to YAML
        run: |
          if [ "\${{ steps.fetch_rules.outputs.fallback }}" == "true" ]; then
            cp .semgrep/theloop-rules.yml.bak .semgrep/theloop-rules.yml
          else
            python3 scripts/json_to_semgrep_yaml.py \\
              --input /tmp/rules.json \\
              --output .semgrep/theloop-rules.yml
          fi

      - name: Run Semgrep scan
        id: semgrep
        continue-on-error: true
        run: |
          pip install semgrep --quiet
          semgrep scan \\
            --config .semgrep/theloop-rules.yml \\
            --json --output /tmp/semgrep-results.json \\
            --metrics off --quiet

      - name: Fail on critical findings
        run: |
          ERRORS=$(python3 -c "
          import json
          d = json.load(open('/tmp/semgrep-results.json'))
          print(sum(1 for r in d.get('results', [])
                    if r.get('extra', {}).get('severity', '').upper() == 'ERROR'))
          " 2>/dev/null || echo "0")
          if [ "$ERRORS" -gt "0" ]; then
            echo "❌ $ERRORS critical finding(s) — merge blocked"
            exit 1
          fi
          echo "✅ No critical findings"`;

	const localTestCmd = `# Validate rules YAML
semgrep --validate --config .semgrep/theloop-rules.yml

# Scan locally against your source
semgrep scan --config .semgrep/theloop-rules.yml

# Scan with JSON output for debugging
semgrep scan --config .semgrep/theloop-rules.yml --json | python3 -m json.tool`;

	const convertCmd = `python3 scripts/json_to_semgrep_yaml.py \\
  --input /tmp/rules.json \\
  --output .semgrep/theloop-rules.yml`;
</script>

<svelte:head>
	<title>Semgrep Integration — The Loop Docs</title>
	<meta
		name="description"
		content="Connect The Loop's scanner to your CI pipeline via GitHub Actions. Fetch rules automatically, run Semgrep on every PR, and block critical findings."
	/>
</svelte:head>

<h1 class="text-3xl font-bold text-text mb-2">Semgrep Integration</h1>
<p class="text-text-muted mb-8">
	The Loop distributes static analysis rules via API. Your CI pipeline fetches the latest rules on
	every pull request, scans your code, and blocks merges on critical findings.
</p>

<DocSection title="How It Works" id="architecture">
	<p class="text-text-muted">
		The integration has three moving parts:
	</p>
	<ol class="list-decimal list-inside text-text-muted space-y-2 ml-2">
		<li>
			<strong class="text-text">Rules API</strong> — The Loop serves Semgrep rules as JSON at
			<code class="text-accent">https://api.loop.oute.pro/api/v1/rules/latest</code>. Rules are
			versioned and filtered by your project whitelist when authenticated with an API key.
		</li>
		<li>
			<strong class="text-text">Conversion script</strong> —
			<code class="text-accent">scripts/json_to_semgrep_yaml.py</code> converts the JSON response to
			Semgrep's YAML format before scanning.
		</li>
		<li>
			<strong class="text-text">Fallback bundle</strong> —
			<code class="text-accent">.semgrep/theloop-rules.yml.bak</code> contains the last known-good
			rule set. The workflow falls back to this file if the API is unreachable.
		</li>
	</ol>
</DocSection>

<DocSection title="GitHub Actions Workflow" id="workflow">
	<p class="text-text-muted mb-4">
		Add this workflow to your repository at
		<code class="text-accent">.github/workflows/theloop-guard.yml</code>:
	</p>
	<CodeBlock
		language="yaml"
		label=".github/workflows/theloop-guard.yml"
		code={workflowYaml}
	/>
	<p class="text-text-muted mt-4">
		Add your API key as a repository secret named
		<code class="text-accent">THELOOP_API_TOKEN</code>. Generate the key in
		<a href="/docs/api-keys/" class="text-accent hover:underline">API Keys</a>.
	</p>
</DocSection>

<DocSection title="Version Pinning" id="version-pinning">
	<p class="text-text-muted">
		By default the workflow fetches the <code class="text-accent">latest</code> active rule version.
		To pin to a specific version, set a GitHub Actions variable named
		<code class="text-accent">THELOOP_RULES_VERSION</code>:
	</p>
	<ul class="list-disc list-inside text-text-muted space-y-1 ml-2">
		<li>
			Go to your repository → <strong class="text-text">Settings → Actions → Variables</strong>
		</li>
		<li>
			Add variable: <code class="text-accent">THELOOP_RULES_VERSION</code> =
			<code class="text-accent">0.4.0</code>
		</li>
	</ul>
	<p class="text-text-muted">
		Pinning is useful when you want to review a new rule version before adopting it across all
		repositories. Remove the variable to return to <code class="text-accent">latest</code>.
	</p>
</DocSection>

<DocSection title="Fallback Behavior" id="fallback">
	<p class="text-text-muted">
		If the API call fails (network timeout, invalid token, or service unavailable), the workflow
		automatically copies <code class="text-accent">.semgrep/theloop-rules.yml.bak</code> to
		<code class="text-accent">.semgrep/theloop-rules.yml</code> and continues the scan using the
		bundled rules. The scan never fails due to API unavailability.
	</p>
	<p class="text-text-muted">
		<strong class="text-text">Never delete</strong>
		<code class="text-accent">.semgrep/theloop-rules.yml.bak</code> — it is the non-negotiable
		fallback. Update it when you want to bundle a newer rule set for offline use.
	</p>
</DocSection>

<DocSection title="ERROR vs WARNING" id="severity">
	<p class="text-text-muted">
		Rules have two severity levels:
	</p>
	<ul class="list-disc list-inside text-text-muted space-y-2 ml-2">
		<li>
			<strong class="text-error">ERROR</strong> — critical patterns that block merge. Examples: SQL
			injection, hardcoded secrets, shell injection.
		</li>
		<li>
			<strong class="text-warning">WARNING</strong> — advisory findings that appear in the PR
			comment but do not block merge. Examples: bare except clauses, N+1 query patterns.
		</li>
	</ul>
	<p class="text-text-muted">
		The workflow fails the CI job only when at least one ERROR-severity finding is present.
		WARNING findings are informational only.
	</p>
</DocSection>

<DocSection title="Scan History" id="scan-history">
	<p class="text-text-muted">
		The workflow posts each scan result to
		<code class="text-accent">POST /api/v1/scans</code> automatically. This populates the scan
		history visible in your Analytics dashboard under Rule Effectiveness. The post is
		best-effort — a failure does not block CI.
	</p>
</DocSection>

<DocSection title="Local Testing" id="local-testing">
	<p class="text-text-muted mb-4">Run the scanner locally before opening a PR:</p>
	<CodeBlock language="bash" label="Local scan commands" code={localTestCmd} />
	<p class="text-text-muted mt-4 mb-4">
		To convert a rules JSON file to YAML manually (e.g. after downloading from the API):
	</p>
	<CodeBlock language="bash" label="Convert JSON → YAML" code={convertCmd} />
</DocSection>
