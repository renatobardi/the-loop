<script lang="ts">
	import { goto } from '$app/navigation';
	import { navigating } from '$app/state';
	import DashboardGrid from '$lib/components/analytics/DashboardGrid.svelte';
	import type {
		AnalyticsFilter,
		AnalyticsSummary,
		CategoryStats,
		TeamStats,
		TimelinePoint,
		SeverityTrendPoint,
		RuleEffectivenessStats
	} from '$lib/types/analytics';
	import {
		getAnalyticsSummary,
		getAnalyticsByCategory,
		getAnalyticsByTeam,
		getAnalyticsTimeline,
		getAnalyticsSeverityTrend,
		getAnalyticsTopRules
	} from '$lib/services/analytics';

	let { data } = $props();

	let loading = $state(true);
	let summary: AnalyticsSummary | null = $state(null);
	let byCategory: CategoryStats[] = $state([]);
	let byTeam: TeamStats[] = $state([]);
	let byTeamAll: TeamStats[] = $state([]);
	let timeline: TimelinePoint[] = $state([]);
	let severityTrend: SeverityTrendPoint[] = $state([]);
	let topRules: RuleEffectivenessStats[] = $state([]);
	let loadError: string | null = $state(null);

	// Generation counter (plain variable, not reactive) guards against stale results
	// when filters change while a previous fetch is still in-flight.
	let loadGeneration = 0;

	// Load analytics data on mount and when filters change
	$effect(() => {
		const gen = ++loadGeneration;
		(async () => {
			loading = true;
			loadError = null;

			try {
				const teamAllFilters: AnalyticsFilter = { ...data.filters, teams: [] };
				const results = await Promise.allSettled([
					getAnalyticsSummary(data.filters),
					getAnalyticsByCategory(data.filters),
					getAnalyticsByTeam(data.filters),
					getAnalyticsByTeam(teamAllFilters),
					getAnalyticsTimeline(data.filters),
					getAnalyticsSeverityTrend(data.filters),
					getAnalyticsTopRules(data.filters)
				]);

				if (gen !== loadGeneration) return; // stale — newer fetch superseded this one

				const val = <T>(r: PromiseSettledResult<T>, fallback: T): T =>
					r.status === 'fulfilled' ? r.value : fallback;

				summary = val(results[0], null);
				byCategory = val(results[1], []);
				byTeam = val(results[2], []);
				byTeamAll = val(results[3], []);
				timeline = val(results[4], []);
				severityTrend = val(results[5], []);
				topRules = val(results[6], []);

				const failures = results.filter((r) => r.status === 'rejected');
				if (failures.length > 0) {
					const reason = (failures[0] as PromiseRejectedResult).reason;
					loadError =
						failures.length === results.length
							? (reason?.message ?? 'Unable to load analytics data')
							: `Some analytics data unavailable: ${reason?.message ?? 'Unknown error'}`;
				}
			} catch (err) {
				if (gen !== loadGeneration) return;
				loadError = err instanceof Error ? err.message : 'Unable to load analytics data';
			} finally {
				if (gen === loadGeneration) loading = false;
			}
		})();
	});

	function handleFiltersChange(f: AnalyticsFilter) {
		// eslint-disable-next-line svelte/prefer-svelte-reactivity
		const params = new URLSearchParams();
		params.set('period', f.period);
		for (const t of f.teams ?? []) {
			params.append('team', t); // multi-select: repeated params
		}
		if (f.category) params.set('category', f.category);
		if (f.status !== 'all') params.set('status', f.status);
		if (f.period === 'custom') {
			if (f.start_date) params.set('start_date', f.start_date);
			if (f.end_date) params.set('end_date', f.end_date);
		}
		goto(`/analytics/?${params.toString()}`, { replaceState: true, invalidateAll: true });
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

	{#if loadError && !summary}
		<div
			class="rounded-lg border border-error/40 bg-error/10 px-6 py-5"
			role="alert"
			aria-live="assertive"
		>
			<p class="font-medium text-error">Failed to load analytics</p>
			<p class="mt-1 text-sm text-error/80">{loadError}</p>
			<button
				class="mt-3 rounded border border-error/40 px-3 py-1.5 text-sm text-error hover:bg-error/10 focus:outline-none focus:ring-2 focus:ring-error"
				onclick={() => goto('/analytics/', { invalidateAll: true })}
				aria-label="Retry loading analytics"
			>
				Retry
			</button>
		</div>
	{:else if summary}
		{#if loadError}
			<div
				class="mb-4 rounded-lg border border-warning/40 bg-warning/10 px-4 py-3 text-sm text-warning"
				role="status"
			>
				{loadError}
			</div>
		{/if}
		<DashboardGrid
			{summary}
			{byCategory}
			{byTeam}
			{byTeamAll}
			{timeline}
			{severityTrend}
			{topRules}
			filters={data.filters}
			loading={navigating.to !== null || loading}
			onFiltersChange={handleFiltersChange}
		/>
	{:else if loading}
		<div class="text-center py-12">
			<p class="text-text-muted">Loading analytics...</p>
		</div>
	{/if}
</div>
