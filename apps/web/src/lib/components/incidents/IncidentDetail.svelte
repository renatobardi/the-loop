<script lang="ts">
	import { Badge } from '$lib/ui';
	import type { Incident } from '$lib/types/incident';
	import * as m from '$lib/paraglide/messages.js';

	let { incident }: { incident: Incident } = $props();

	const severityColors: Record<string, string> = {
		critical: 'bg-error text-white',
		high: 'bg-accent text-white',
		medium: 'bg-accent-light text-text',
		low: 'bg-bg-elevated text-text-muted'
	};
</script>

<div class="space-y-8">
	<div class="flex items-start justify-between">
		<div>
			<h1 class="text-2xl font-bold text-text">{incident.title}</h1>
			<div class="mt-2 flex gap-2">
				<Badge>{incident.category}</Badge>
				<Badge class={severityColors[incident.severity] ?? ''}>{incident.severity}</Badge>
			</div>
		</div>
	</div>

	<section>
		<h2 class="mb-3 text-lg font-semibold text-text">{m.incident_detail_section_description()}</h2>
		<dl class="grid gap-3 text-sm md:grid-cols-2">
			{#if incident.date}
				<div><dt class="text-text-muted">{m.incident_field_date()}</dt><dd class="text-text">{incident.date}</dd></div>
			{/if}
			{#if incident.organization}
				<div><dt class="text-text-muted">{m.incident_field_organization()}</dt><dd class="text-text">{incident.organization}</dd></div>
			{/if}
			{#if incident.source_url}
				<div class="md:col-span-2"><dt class="text-text-muted">{m.incident_field_source_url()}</dt><dd><a href={incident.source_url} target="_blank" rel="noopener" class="text-accent hover:underline">{incident.source_url}</a></dd></div>
			{/if}
			{#if incident.failure_mode}
				<div class="md:col-span-2"><dt class="text-text-muted">{m.incident_field_failure_mode()}</dt><dd class="text-text">{incident.failure_mode}</dd></div>
			{/if}
		</dl>
	</section>

	<section>
		<h2 class="mb-3 text-lg font-semibold text-text">{m.incident_detail_section_classification()}</h2>
		<dl class="grid gap-3 text-sm md:grid-cols-2">
			{#if incident.subcategory}
				<div><dt class="text-text-muted">{m.incident_field_subcategory()}</dt><dd class="text-text">{incident.subcategory}</dd></div>
			{/if}
			{#if incident.affected_languages.length > 0}
				<div><dt class="text-text-muted">{m.incident_field_affected_languages()}</dt><dd class="flex gap-1">{#each incident.affected_languages as lang}<Badge>{lang}</Badge>{/each}</dd></div>
			{/if}
			{#if incident.tags.length > 0}
				<div><dt class="text-text-muted">{m.incident_field_tags()}</dt><dd class="flex flex-wrap gap-1">{#each incident.tags as tag}<span class="rounded bg-bg-elevated px-1.5 py-0.5 text-xs text-text-muted">{tag}</span>{/each}</dd></div>
			{/if}
		</dl>
	</section>

	<section>
		<h2 class="mb-3 text-lg font-semibold text-text">{m.incident_detail_section_remediation()}</h2>
		<div class="space-y-4 text-sm">
			<div>
				<h3 class="font-medium text-text-muted">{m.incident_field_anti_pattern()}</h3>
				<p class="mt-1 whitespace-pre-wrap text-text">{incident.anti_pattern}</p>
			</div>
			{#if incident.code_example}
				<div>
					<h3 class="font-medium text-text-muted">{m.incident_field_code_example()}</h3>
					<pre class="mt-1 overflow-x-auto rounded-md bg-bg-elevated p-3 font-mono text-xs text-text">{incident.code_example}</pre>
				</div>
			{/if}
			<div>
				<h3 class="font-medium text-text-muted">{m.incident_field_remediation()}</h3>
				<p class="mt-1 whitespace-pre-wrap text-text">{incident.remediation}</p>
			</div>
			<div class="flex items-center gap-2 text-text-muted">
				<span>{m.incident_field_static_rule_possible()}:</span>
				<span class="font-medium text-text">{incident.static_rule_possible ? 'Yes' : 'No'}</span>
			</div>
			{#if incident.semgrep_rule_id}
				<div><span class="text-text-muted">{m.incident_field_semgrep_rule_id()}:</span> <code class="rounded bg-bg-elevated px-1 text-xs">{incident.semgrep_rule_id}</code></div>
			{/if}
		</div>
	</section>

	<section class="border-t border-border pt-4 text-xs text-text-muted">
		<h2 class="mb-2 text-sm font-semibold text-text">{m.incident_detail_section_metadata()}</h2>
		<div class="flex flex-wrap gap-4">
			<span>{m.incident_field_version()}: {incident.version}</span>
			<span>{m.incidents_created_at()} {new Date(incident.created_at).toLocaleString()}</span>
			<span>{m.incident_field_created_by()}: {incident.created_by}</span>
		</div>
	</section>
</div>
