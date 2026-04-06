<script lang="ts">
	import DocSection from '$lib/components/docs/DocSection.svelte';
	import CodeBlock from '$lib/components/docs/CodeBlock.svelte';

	const authHeader = `# Firebase JWT
Authorization: Bearer <firebase-id-token>

# API Key
Authorization: Bearer tlp_<your-api-key>`;

	const listEnvelope = `{
  "items": [...],
  "total": 42
}`;

	const errorFormat = `{
  "detail": "Incident not found"
}`;

	const rateLimitHeaders = `X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1712345678
Retry-After: 15   # present only on 429 responses`;
</script>

<svelte:head>
	<title>API Reference — The Loop Docs</title>
	<meta
		name="description"
		content="Complete API reference: base URL, authentication, all endpoints by group, response envelopes, error format, and rate limit headers."
	/>
</svelte:head>

<h1 class="text-3xl font-bold text-text mb-2">API Reference</h1>
<p class="text-text-muted mb-8">
	Complete reference for The Loop REST API. All endpoints return JSON. Authentication is required
	for all endpoints except the health check and public rule browser.
</p>

<DocSection title="Base URL & Authentication" id="base-url">
	<p class="text-text-muted mb-4">
		All endpoints are relative to: <code class="text-accent">https://api.loop.oute.pro</code>
	</p>
	<CodeBlock language="text" label="Authorization header" code={authHeader} />
</DocSection>

<DocSection title="Response Format" id="response-format">
	<p class="text-text-muted mb-2">
		List endpoints return a standard envelope:
	</p>
	<CodeBlock language="json" label="List response envelope" code={listEnvelope} />
	<p class="text-text-muted mt-4 mb-2">Error responses use a consistent format:</p>
	<CodeBlock language="json" label="Error response" code={errorFormat} />
</DocSection>

<DocSection title="Rate Limit Headers" id="rate-limits">
	<CodeBlock language="text" label="Rate limit response headers" code={rateLimitHeaders} />
</DocSection>

<DocSection title="Endpoint Index" id="endpoints">
	<div class="overflow-x-auto">
		<table class="w-full text-sm">
			<thead>
				<tr class="border-b border-border text-left">
					<th class="pb-2 pr-3 text-text font-semibold w-16">Method</th>
					<th class="pb-2 pr-3 text-text font-semibold">Path</th>
					<th class="pb-2 pr-3 text-text font-semibold w-24">Auth</th>
					<th class="pb-2 text-text font-semibold">Description</th>
				</tr>
			</thead>
			<tbody class="text-text-muted">
				<!-- Health -->
				<tr class="border-b border-border/30">
					<td colspan={4} class="py-2 text-xs font-semibold uppercase tracking-widest text-text-subtle">Health</td>
				</tr>
				<tr class="border-b border-border/20">
					<td class="py-1.5 pr-3 font-mono text-success text-xs">GET</td>
					<td class="py-1.5 pr-3 font-mono text-accent text-xs">/api/v1/health</td>
					<td class="py-1.5 pr-3 text-xs">None</td>
					<td class="py-1.5 text-xs">Service health check</td>
				</tr>
				<!-- Incidents -->
				<tr class="border-b border-border/30">
					<td colspan={4} class="py-2 text-xs font-semibold uppercase tracking-widest text-text-subtle">Incidents</td>
				</tr>
				{#each [
					['GET', '/api/v1/incidents', 'Firebase', 'List incidents (paginated, filterable)'],
					['POST', '/api/v1/incidents', 'Firebase', 'Create incident'],
					['GET', '/api/v1/incidents/{id}', 'Firebase', 'Get incident by ID'],
					['PATCH', '/api/v1/incidents/{id}', 'Firebase', 'Update incident fields'],
					['DELETE', '/api/v1/incidents/{id}', 'Firebase', 'Soft-delete incident'],
				] as row (row[1])}
					<tr class="border-b border-border/20">
						<td class="py-1.5 pr-3 font-mono text-xs {row[0] === 'GET' ? 'text-success' : row[0] === 'POST' ? 'text-accent' : row[0] === 'DELETE' ? 'text-error' : 'text-warning'}">{row[0]}</td>
						<td class="py-1.5 pr-3 font-mono text-accent text-xs">{row[1]}</td>
						<td class="py-1.5 pr-3 text-xs">{row[2]}</td>
						<td class="py-1.5 text-xs">{row[3]}</td>
					</tr>
				{/each}
				<!-- Sub-resources -->
				<tr class="border-b border-border/30">
					<td colspan={4} class="py-2 text-xs font-semibold uppercase tracking-widest text-text-subtle">Incident Sub-resources</td>
				</tr>
				{#each [
					['GET', '/api/v1/incidents/{id}/timeline', 'Firebase', 'List timeline events'],
					['POST', '/api/v1/incidents/{id}/timeline', 'Firebase', 'Add timeline event'],
					['GET', '/api/v1/incidents/{id}/responders', 'Firebase', 'List responders'],
					['POST', '/api/v1/incidents/{id}/responders', 'Firebase', 'Add responder'],
					['DELETE', '/api/v1/incidents/{id}/responders/{uid}', 'Firebase', 'Remove responder'],
					['GET', '/api/v1/incidents/{id}/action-items', 'Firebase', 'List action items'],
					['POST', '/api/v1/incidents/{id}/action-items', 'Firebase', 'Create action item'],
					['PATCH', '/api/v1/incidents/{id}/action-items/{aid}', 'Firebase', 'Update action item'],
					['GET', '/api/v1/incidents/{id}/attachments', 'Firebase', 'List attachments'],
					['POST', '/api/v1/incidents/{id}/attachments', 'Firebase', 'Upload attachment'],
				] as row (row[1])}
					<tr class="border-b border-border/20">
						<td class="py-1.5 pr-3 font-mono text-xs {row[0] === 'GET' ? 'text-success' : row[0] === 'POST' ? 'text-accent' : row[0] === 'DELETE' ? 'text-error' : 'text-warning'}">{row[0]}</td>
						<td class="py-1.5 pr-3 font-mono text-accent text-xs">{row[1]}</td>
						<td class="py-1.5 pr-3 text-xs">{row[2]}</td>
						<td class="py-1.5 text-xs">{row[3]}</td>
					</tr>
				{/each}
				<!-- Postmortems -->
				<tr class="border-b border-border/30">
					<td colspan={4} class="py-2 text-xs font-semibold uppercase tracking-widest text-text-subtle">Postmortems</td>
				</tr>
				{#each [
					['GET', '/api/v1/incidents/{id}/postmortems', 'Firebase', 'Get postmortem for incident'],
					['POST', '/api/v1/incidents/{id}/postmortems', 'Firebase', 'Create postmortem (1 per incident)'],
					['PUT', '/api/v1/incidents/{id}/postmortems', 'Firebase', 'Update postmortem (fails if locked)'],
					['GET', '/api/v1/incidents/{id}/postmortems/templates', 'Firebase', 'List available templates'],
				] as row (row[1])}
					<tr class="border-b border-border/20">
						<td class="py-1.5 pr-3 font-mono text-xs {row[0] === 'GET' ? 'text-success' : row[0] === 'POST' ? 'text-accent' : 'text-warning'}">{row[0]}</td>
						<td class="py-1.5 pr-3 font-mono text-accent text-xs">{row[1]}</td>
						<td class="py-1.5 pr-3 text-xs">{row[2]}</td>
						<td class="py-1.5 text-xs">{row[3]}</td>
					</tr>
				{/each}
				<!-- Analytics -->
				<tr class="border-b border-border/30">
					<td colspan={4} class="py-2 text-xs font-semibold uppercase tracking-widest text-text-subtle">Analytics (60 req/min)</td>
				</tr>
				{#each [
					['GET', '/api/v1/incidents/analytics/summary', 'Firebase', 'KPI summary cards'],
					['GET', '/api/v1/incidents/analytics/by-category', 'Firebase', 'Category breakdown'],
					['GET', '/api/v1/incidents/analytics/by-team', 'Firebase', 'Team breakdown'],
					['GET', '/api/v1/incidents/analytics/by-team/all', 'Firebase', 'All teams breakdown'],
					['GET', '/api/v1/incidents/analytics/timeline', 'Firebase', 'Weekly incident timeline'],
					['GET', '/api/v1/incidents/analytics/severity-trend', 'Firebase', 'Severity trend over time'],
				] as row (row[1])}
					<tr class="border-b border-border/20">
						<td class="py-1.5 pr-3 font-mono text-success text-xs">{row[0]}</td>
						<td class="py-1.5 pr-3 font-mono text-accent text-xs">{row[1]}</td>
						<td class="py-1.5 pr-3 text-xs">{row[2]}</td>
						<td class="py-1.5 text-xs">{row[3]}</td>
					</tr>
				{/each}
				<!-- Rules -->
				<tr class="border-b border-border/30">
					<td colspan={4} class="py-2 text-xs font-semibold uppercase tracking-widest text-text-subtle">Rules</td>
				</tr>
				{#each [
					['GET', '/api/v1/rules/latest', 'Optional API key', 'Latest active rules (JSON); filtered by whitelist if authenticated'],
					['GET', '/api/v1/rules/{version}', 'Optional API key', 'Specific version rules (JSON)'],
					['GET', '/api/v1/rules/active', 'Admin', 'List all active versions (metadata)'],
				] as row (row[1])}
					<tr class="border-b border-border/20">
						<td class="py-1.5 pr-3 font-mono text-success text-xs">{row[0]}</td>
						<td class="py-1.5 pr-3 font-mono text-accent text-xs">{row[1]}</td>
						<td class="py-1.5 pr-3 text-xs">{row[2]}</td>
						<td class="py-1.5 text-xs">{row[3]}</td>
					</tr>
				{/each}
				<!-- API Keys -->
				<tr class="border-b border-border/30">
					<td colspan={4} class="py-2 text-xs font-semibold uppercase tracking-widest text-text-subtle">API Keys</td>
				</tr>
				{#each [
					['GET', '/api/v1/api-keys', 'Firebase', 'List your API keys'],
					['POST', '/api/v1/api-keys', 'Firebase', 'Create API key'],
					['GET', '/api/v1/api-keys/{id}', 'Firebase', 'Get API key details'],
					['DELETE', '/api/v1/api-keys/{id}', 'Firebase', 'Revoke API key'],
				] as row (row[1])}
					<tr class="border-b border-border/20">
						<td class="py-1.5 pr-3 font-mono text-xs {row[0] === 'GET' ? 'text-success' : row[0] === 'POST' ? 'text-accent' : 'text-error'}">{row[0]}</td>
						<td class="py-1.5 pr-3 font-mono text-accent text-xs">{row[1]}</td>
						<td class="py-1.5 pr-3 text-xs">{row[2]}</td>
						<td class="py-1.5 text-xs">{row[3]}</td>
					</tr>
				{/each}
				<!-- Scans -->
				<tr class="border-b border-border/30">
					<td colspan={4} class="py-2 text-xs font-semibold uppercase tracking-widest text-text-subtle">Scans</td>
				</tr>
				{#each [
					['POST', '/api/v1/scans', 'API Key', 'Ingest scan result from CI'],
					['GET', '/api/v1/scans', 'Firebase', 'List scan history'],
				] as row (row[1])}
					<tr class="border-b border-border/20">
						<td class="py-1.5 pr-3 font-mono text-xs {row[0] === 'GET' ? 'text-success' : 'text-accent'}">{row[0]}</td>
						<td class="py-1.5 pr-3 font-mono text-accent text-xs">{row[1]}</td>
						<td class="py-1.5 pr-3 text-xs">{row[2]}</td>
						<td class="py-1.5 text-xs">{row[3]}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</DocSection>
