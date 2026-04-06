<script lang="ts">
	import DocSection from '$lib/components/docs/DocSection.svelte';
	import CodeBlock from '$lib/components/docs/CodeBlock.svelte';

	const ciHeader = `curl -s \\
  -H "Authorization: Bearer tlp_your_key_here" \\
  "https://api.loop.oute.pro/api/v1/rules/latest"`;

	const githubActionsSecret = `# In your GitHub Actions workflow:
- name: Fetch rules from API
  run: |
    curl -s \\
      -H "Authorization: Bearer \${{ secrets.THELOOP_API_TOKEN }}" \\
      "https://api.loop.oute.pro/api/v1/rules/latest" \\
      -o /tmp/rules.json`;
</script>

<svelte:head>
	<title>API Keys — The Loop Docs</title>
	<meta
		name="description"
		content="Create and manage API keys to authenticate your CI scanner with The Loop. Understand key format, scope, project whitelist, and rotation."
	/>
</svelte:head>

<h1 class="text-3xl font-bold text-text mb-2">API Keys</h1>
<p class="text-text-muted mb-8">
	API keys authenticate your CI scanner with The Loop's rules API. Each key is scoped to a
	specific project and prefixed with <code class="text-accent">tlp_</code> for easy identification.
</p>

<DocSection title="What Is an API Key?" id="what-is-it">
	<p class="text-text-muted">
		An API key is a bearer token used by automated systems (CI pipelines, scripts) to fetch rules
		from The Loop API. Keys are not user session tokens — they represent a project's access to the
		rules distribution endpoint.
	</p>
	<ul class="list-disc list-inside text-text-muted space-y-1 ml-2">
		<li>
			<strong class="text-text">Prefix:</strong>
			<code class="text-accent">tlp_</code> — all keys start with this prefix
		</li>
		<li>
			<strong class="text-text">Scope:</strong> one key per project; the key filters rules to your
			project's whitelist
		</li>
		<li>
			<strong class="text-text">Storage:</strong> store in GitHub Secrets or your CI secret manager
			— never in source code
		</li>
	</ul>
</DocSection>

<DocSection title="Creating a Key" id="creating">
	<ol class="list-decimal list-inside text-text-muted space-y-2 ml-2">
		<li>
			Navigate to <strong class="text-text">Profile → API Keys</strong> (top-right avatar menu).
		</li>
		<li>
			Click <strong class="text-text">New API Key</strong>.
		</li>
		<li>Enter a descriptive name (e.g., <code class="text-accent">github-actions-prod</code>).</li>
		<li>
			Copy the key immediately — it is shown only once. Store it in your CI secret manager.
		</li>
	</ol>
	<p class="text-text-muted">
		The key appears in the list after creation but the value is never shown again. If you lose the
		key, revoke it and create a new one.
	</p>
</DocSection>

<DocSection title="Using the Key in CI" id="ci-usage">
	<p class="text-text-muted mb-4">
		Pass the key as a bearer token in the <code class="text-accent">Authorization</code> header:
	</p>
	<CodeBlock language="bash" label="Direct curl usage" code={ciHeader} />
	<p class="text-text-muted mt-4 mb-4">
		In GitHub Actions, store the key as a repository secret named
		<code class="text-accent">THELOOP_API_TOKEN</code> and reference it in your workflow:
	</p>
	<CodeBlock language="yaml" label="GitHub Actions usage" code={githubActionsSecret} />
</DocSection>

<DocSection title="Project Whitelist" id="whitelist">
	<p class="text-text-muted">
		When you authenticate with an API key, the rules API filters the response to include only rules
		in your project's whitelist. This means different projects can receive different rule subsets
		even within the same organization.
	</p>
	<p class="text-text-muted">
		Contact your administrator to adjust the rule whitelist for a project. Whitelist changes take
		effect on the next CI run.
	</p>
</DocSection>

<DocSection title="Rotating and Revoking" id="rotating">
	<p class="text-text-muted">
		<strong class="text-text">To rotate:</strong> create a new key, update the CI secret, verify
		the pipeline runs successfully, then revoke the old key.
	</p>
	<p class="text-text-muted">
		<strong class="text-text">To revoke:</strong> navigate to
		<strong class="text-text">Profile → API Keys</strong>, find the key by name, and click
		<strong class="text-text">Revoke</strong>. Revocation is immediate — the key stops working
		within seconds. Any CI run using the revoked key will fall back to the
		<code class="text-accent">.bak</code> rule bundle automatically.
	</p>
</DocSection>
