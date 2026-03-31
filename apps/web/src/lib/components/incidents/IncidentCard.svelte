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

<!-- eslint-disable svelte/no-navigation-without-resolve -- ParaglideJS translates href automatically -->
<a
	href="/incidents/{incident.id}/"
	class="block rounded-lg border border-border bg-bg-surface p-4 transition-colors hover:border-border-hover hover:bg-bg-elevated"
>
<!-- eslint-enable svelte/no-navigation-without-resolve -->
	<div class="flex items-start justify-between gap-3">
		<h3 class="text-base font-medium text-text">{incident.title}</h3>
		<Badge class={severityColors[incident.severity] ?? ''}>{incident.severity}</Badge>
	</div>

	<div class="mt-2 flex flex-wrap items-center gap-2 text-xs text-text-muted">
		<Badge>{incident.category}</Badge>
		{#if incident.organization}
			<span>{incident.organization}</span>
		{/if}
		<span>{m.incidents_created_at()} {new Date(incident.created_at).toLocaleDateString()}</span>
	</div>

	{#if incident.tags.length > 0}
		<div class="mt-2 flex flex-wrap gap-1">
			{#each incident.tags as tag (tag)}
				<span class="rounded bg-bg-elevated px-1.5 py-0.5 text-xs text-text-muted">{tag}</span>
			{/each}
		</div>
	{/if}
</a>
