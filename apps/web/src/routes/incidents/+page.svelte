<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button } from '$lib/ui';
	import IncidentCard from '$lib/components/incidents/IncidentCard.svelte';
	import IncidentFilters from '$lib/components/incidents/IncidentFilters.svelte';
	import Pagination from '$lib/components/incidents/Pagination.svelte';
	import type { Category, Severity } from '$lib/types/incident';

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
		goto(`/incidents/${query ? `?${query}` : ''}`, { replaceState: true, invalidateAll: true });
	}
</script>

<div class="space-y-6 py-8">
	<div class="flex items-center justify-between">
		<h1 class="text-2xl font-bold text-text">Incidents</h1>
		<a href="/incidents/new/">
			<Button>New Incident</Button>
		</a>
	</div>

	<IncidentFilters
		bind:category
		bind:severity
		bind:keyword
		onchange={applyFilters}
	/>

	{#if data.loadError}
		<p class="py-12 text-center text-error">Unable to connect to the server. Please try again later.</p>
	{:else if data.items.length === 0}
		<p class="py-12 text-center text-text-muted">No incidents found.</p>
	{:else}
		<div class="space-y-3">
			{#each data.items as incident (incident.id)}
				<IncidentCard {incident} />
			{/each}
		</div>
	{/if}

	<Pagination bind:page={currentPage} bind:perPage total={data.total} onchange={applyFilters} />
</div>
