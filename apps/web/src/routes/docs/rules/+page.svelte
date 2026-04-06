<script lang="ts">
	import DocSection from '$lib/components/docs/DocSection.svelte';
	import CodeBlock from '$lib/components/docs/CodeBlock.svelte';

	const ruleIdFormat = `# Format: theloop.<language>.<category>.<descriptor>
#
# Examples:
theloop.python.injection.sql-parameterized
theloop.javascript.security.eval-usage
theloop.go.crypto.weak-hash
theloop.typescript.performance.n-plus-one
theloop.java.injection.xxe-parser`;

	const localValidate = `# Validate rule YAML syntax
semgrep --validate --config .semgrep/theloop-rules.yml

# Scan test data against rules
semgrep scan --config .semgrep/theloop-rules.yml tests/test-data/`;
</script>

<svelte:head>
	<title>Rules — The Loop Docs</title>
	<meta
		name="description"
		content="Understand The Loop's rule library: version history, severity model, 10 supported languages, rule ID format, and how to request new rules."
	/>
</svelte:head>

<h1 class="text-3xl font-bold text-text mb-2">Rules</h1>
<p class="text-text-muted mb-8">
	The Loop distributes static analysis rules that detect incident-causing patterns in your code.
	Rules are versioned, language-specific, and scoped to your project whitelist.
</p>

<DocSection title="Version History" id="versions">
	<p class="text-text-muted mb-4">Rules are versioned using semantic versioning. Active versions:</p>
	<div class="overflow-x-auto">
		<table class="w-full text-sm">
			<thead>
				<tr class="border-b border-border text-left">
					<th class="pb-2 pr-4 text-text font-semibold">Version</th>
					<th class="pb-2 pr-4 text-text font-semibold">Rules</th>
					<th class="pb-2 text-text font-semibold">Highlights</th>
				</tr>
			</thead>
			<tbody class="text-text-muted">
				<tr class="border-b border-border/50">
					<td class="py-2 pr-4 font-mono text-accent">v0.4.0</td>
					<td class="py-2 pr-4">122</td>
					<td class="py-2">Java, C#, PHP, Ruby, Kotlin, Rust, C/C++ support added</td>
				</tr>
				<tr class="border-b border-border/50">
					<td class="py-2 pr-4 font-mono text-accent">v0.3.0</td>
					<td class="py-2 pr-4">45</td>
					<td class="py-2">JavaScript/TypeScript (15 rules) + Go (10 rules)</td>
				</tr>
				<tr class="border-b border-border/50">
					<td class="py-2 pr-4 font-mono text-accent">v0.2.0</td>
					<td class="py-2 pr-4">20</td>
					<td class="py-2">Path traversal, XXE, weak crypto, Docker security, CORS</td>
				</tr>
				<tr>
					<td class="py-2 pr-4 font-mono text-accent">v0.1.0</td>
					<td class="py-2 pr-4">6</td>
					<td class="py-2">SQL injection, eval, shell injection, hardcoded secrets, bare except, ReDoS</td>
				</tr>
			</tbody>
		</table>
	</div>
	<p class="text-text-muted mt-4">
		The latest active version is always served by default. Pin to a specific version with the
		<code class="text-accent">THELOOP_RULES_VERSION</code> GitHub Actions variable (see
		<a href="/docs/semgrep/" class="text-accent hover:underline">Semgrep Integration</a>).
	</p>
</DocSection>

<DocSection title="Rule Browser" id="browser">
	<p class="text-text-muted">
		Browse all active rules at <a href="/rules/latest/" class="text-accent hover:underline"
			>loop.oute.pro/rules/latest</a
		>. The rule browser shows rule ID, language, severity, description, and example bad/good code
		patterns. No authentication is required to browse rules.
	</p>
	<p class="text-text-muted">
		When authenticated with an API key, only rules in your project's whitelist are visible.
	</p>
</DocSection>

<DocSection title="Severity Model" id="severity">
	<p class="text-text-muted">Each rule has one of two severity levels:</p>
	<ul class="list-disc list-inside text-text-muted space-y-2 ml-2">
		<li>
			<strong class="text-error">ERROR</strong> — patterns that directly cause production incidents
			(injection, hardcoded secrets, shell execution). Findings at this level
			<strong class="text-text">block merge</strong>.
		</li>
		<li>
			<strong class="text-warning">WARNING</strong> — patterns that increase incident risk but are
			context-dependent (N+1 queries, weak crypto, debug mode enabled). Findings at this level are
			<strong class="text-text">advisory</strong> and do not block merge.
		</li>
	</ul>
</DocSection>

<DocSection title="Supported Languages" id="languages">
	<p class="text-text-muted">Rules are available for 10 languages as of v0.4.0:</p>
	<div class="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-2">
		{#each ['Python', 'JavaScript', 'TypeScript', 'Go', 'Java', 'C#', 'PHP', 'Ruby', 'Kotlin', 'Rust', 'C', 'C++'] as lang (lang)}
			<span class="px-3 py-1.5 rounded-lg bg-bg-elevated border border-border text-sm text-text-muted font-mono">
				{lang}
			</span>
		{/each}
	</div>
</DocSection>

<DocSection title="Rule ID Format" id="rule-id">
	<p class="text-text-muted mb-4">
		All rule IDs follow a consistent naming convention:
	</p>
	<CodeBlock language="text" label="Rule ID format" code={ruleIdFormat} />
	<p class="text-text-muted mt-4">
		The rule ID is shown in CI output and PR comments. Use it to look up the rule in the browser
		or to request an exemption for a specific pattern.
	</p>
</DocSection>

<DocSection title="Requesting a New Rule" id="request">
	<p class="text-text-muted">
		If you encounter an incident-causing pattern not covered by the current rule set, you can
		request a new rule:
	</p>
	<ol class="list-decimal list-inside text-text-muted space-y-2 ml-2">
		<li>Identify the pattern in your post-mortem — what code construct caused the incident?</li>
		<li>Open a GitHub issue on the platform repository describing the pattern and the incident.</li>
		<li>The platform team reviews and, if approved, adds it to the next versioned release.</li>
	</ol>
	<p class="text-text-muted">
		New rules are always released under a new version number. Your existing pipeline continues
		using the pinned version until you update.
	</p>
</DocSection>

<DocSection title="Validating Rules Locally" id="validate">
	<CodeBlock language="bash" label="Local validation" code={localValidate} />
</DocSection>
