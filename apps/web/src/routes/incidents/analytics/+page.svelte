<script lang="ts">
	import { goto } from '$app/navigation';
	import DashboardGrid from '$lib/components/analytics/DashboardGrid.svelte';
	import type { AnalyticsFilter } from '$lib/types/analytics';

	let { data } = $props();

	function handleFiltersChange(f: AnalyticsFilter) {
		const params = new URLSearchParams(); // eslint-disable-line svelte/prefer-svelte-reactivity -- not reactive, rebuilt each call
		params.set('period', f.period);
		if (f.team) params.set('team', f.team);
		if (f.category) params.set('category', f.category);
		if (f.status !== 'all') params.set('status', f.status);
		if (f.period === 'custom') {
			if (f.start_date) params.set('start_date', f.start_date);
			if (f.end_date) params.set('end_date', f.end_date);
		}
		goto(`/incidents/analytics/?${params.toString()}`, { replaceState: true, invalidateAll: true });
	}
</script>

<div class="py-8">
	<div class="mb-6 flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold text-text">Analytics</h1>
			<p class="mt-1 text-sm text-text-muted">Incident patterns and trends</p>
		</div>
		<a href="/incidents/" class="text-sm text-accent hover:underline">← All Incidents</a>
	</div>

	{#if data.loadError}
		<div class="rounded-lg border border-error/40 bg-error/10 px-4 py-3 text-sm text-error">
			Failed to load analytics: {data.loadError}
			<button
				class="ml-3 underline hover:no-underline"
				onclick={() => goto('/incidents/analytics/', { invalidateAll: true })}
			>
				Retry
			</button>
		</div>
	{:else}
		<DashboardGrid
			summary={data.summary}
			byCategory={data.byCategory}
			byTeam={data.byTeam}
			byTeamAll={data.byTeamAll}
			timeline={data.timeline}
			filters={data.filters}
			onFiltersChange={handleFiltersChange}
		/>
	{/if}
</div>
