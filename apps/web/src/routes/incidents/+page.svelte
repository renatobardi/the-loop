<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button } from '$lib/ui';
	import { i18n } from '$lib/i18n';
	import { languageTag } from '$lib/paraglide/runtime.js';
	import IncidentCard from '$lib/components/incidents/IncidentCard.svelte';
	import IncidentFilters from '$lib/components/incidents/IncidentFilters.svelte';
	import Pagination from '$lib/components/incidents/Pagination.svelte';
	import type { Category, Severity } from '$lib/types/incident';
	import * as m from '$lib/paraglide/messages.js';

	let { data } = $props();

	let category: Category | null = $state(data.filters.category ?? null);
	let severity: Severity | null = $state(data.filters.severity ?? null);
	let keyword = $state(data.filters.q ?? '');
	let currentPage = $state(data.page);
	let perPage = $state(data.per_page);
	function applyFilters() {
		const params = new URLSearchParams(); // eslint-disable-line svelte/prefer-svelte-reactivity -- not reactive, rebuilt each call
		if (currentPage > 1) params.set('page', String(currentPage));
		if (perPage !== 20) params.set('per_page', String(perPage));
		if (category) params.set('category', category);
		if (severity) params.set('severity', severity);
		if (keyword) params.set('q', keyword);
		const query = params.toString();
		const resolved = i18n.resolveRoute('/incidents', languageTag());
		goto(`${resolved}/${query ? `?${query}` : ''}`, { replaceState: true, invalidateAll: true }); // eslint-disable-line svelte/no-navigation-without-resolve -- resolved via i18n.resolveRoute above
	}
</script>

<div class="space-y-6 py-8">
	<div class="flex items-center justify-between">
		<h1 class="text-2xl font-bold text-text">{m.incidents_title()}</h1>
		<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- ParaglideJS translates href automatically -->
		<a href="/incidents/new/">
			<Button>{m.incident_create_title()}</Button>
		</a>
	</div>

	<IncidentFilters
		bind:category
		bind:severity
		bind:keyword
		onchange={applyFilters}
	/>

	{#if data.items.length === 0}
		<p class="py-12 text-center text-text-muted">{m.incidents_empty()}</p>
	{:else}
		<div class="space-y-3">
			{#each data.items as incident (incident.id)}
				<IncidentCard {incident} />
			{/each}
		</div>
	{/if}

	<Pagination bind:page={currentPage} bind:perPage total={data.total} onchange={applyFilters} />
</div>
