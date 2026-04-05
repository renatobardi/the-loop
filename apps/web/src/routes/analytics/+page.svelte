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
	let abortController: AbortController | null = $state(null);

	// Load analytics data on mount and when filters change
	$effect(() => {
		// Cancel any in-flight requests when filters change
		if (abortController) {
			abortController.abort();
		}

		abortController = new AbortController();
		const currentAbort = abortController;

		(async () => {
			loading = true;
			loadError = null;

			try {
				const teamAllFilters: AnalyticsFilter = { ...data.filters, teams: [] };
				const [s, bc, bt, bta, t, st, tr] = await Promise.all([
					getAnalyticsSummary(data.filters),
					getAnalyticsByCategory(data.filters),
					getAnalyticsByTeam(data.filters),
					getAnalyticsByTeam(teamAllFilters),
					getAnalyticsTimeline(data.filters),
					getAnalyticsSeverityTrend(data.filters),
					getAnalyticsTopRules(data.filters)
				]);

				// Only update state if this abort controller wasn't cancelled
				if (!currentAbort.signal.aborted) {
					summary = s;
					byCategory = bc;
					byTeam = bt;
					byTeamAll = bta;
					timeline = t;
					severityTrend = st;
					topRules = tr;
				}
			} catch (err) {
				// Only show error if this abort controller wasn't cancelled
				if (!currentAbort.signal.aborted) {
					loadError = err instanceof Error ? err.message : 'Unable to load analytics data';
				}
			} finally {
				if (!currentAbort.signal.aborted) {
					loading = false;
				}
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

	{#if loadError}
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
		<DashboardGrid
			{summary}
			{byCategory}
			{byTeam}
			{byTeamAll}
			{timeline}
			{severityTrend}
			{topRules}
			filters={data.filters}
			loading={navigating !== null || loading}
			onFiltersChange={handleFiltersChange}
		/>
	{:else if loading}
		<div class="text-center py-12">
			<p class="text-text-muted">Loading analytics...</p>
		</div>
	{/if}
</div>
