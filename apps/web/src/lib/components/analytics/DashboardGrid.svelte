<script lang="ts">
	import type { AnalyticsSummary, CategoryStats, TeamStats, TimelinePoint, AnalyticsFilter } from '$lib/types/analytics';
	import SummaryCard from './SummaryCard.svelte';
	import CategoryHeatmap from './CategoryHeatmap.svelte';
	import TeamHeatmap from './TeamHeatmap.svelte';
	import PatternTimeline from './PatternTimeline.svelte';
	import AnalyticsFilters from './AnalyticsFilters.svelte';

	let {
		summary,
		byCategory,
		byTeam,
		byTeamAll,
		timeline,
		filters,
		loading = false,
		onFiltersChange
	}: {
		summary: AnalyticsSummary;
		byCategory: CategoryStats[];
		byTeam: TeamStats[];
		byTeamAll: TeamStats[];
		timeline: TimelinePoint[];
		filters: AnalyticsFilter;
		loading?: boolean;
		onFiltersChange: (_: AnalyticsFilter) => void; // eslint-disable-line no-unused-vars
	} = $props();

	const isEmpty = $derived(!loading && summary.total === 0);
</script>

<div class="space-y-6">
	<!-- Sticky filter bar -->
	<div class="sticky top-0 z-20 bg-bg pb-2 pt-4">
		<AnalyticsFilters {filters} teamOptions={byTeamAll} onApply={onFiltersChange} />
	</div>

	{#if loading}
		<!-- T106: Loading skeleton -->
		<div aria-busy="true" aria-label="Loading analytics data" class="space-y-6">
			<!-- Summary skeleton -->
			<div class="animate-pulse rounded-lg border border-border bg-bg-surface p-6">
				<div class="mb-4 h-5 w-24 rounded bg-bg-elevated"></div>
				<div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
					{#each [0, 1, 2, 3] as _ (_)}
						<div class="flex flex-col gap-2">
							<div class="h-8 w-14 rounded bg-bg-elevated"></div>
							<div class="h-3 w-10 rounded bg-bg-elevated"></div>
						</div>
					{/each}
				</div>
			</div>

			<!-- Heatmap skeletons -->
			<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
				{#each [0, 1] as _ (_)}
					<div class="animate-pulse rounded-lg border border-border bg-bg-surface p-6">
						<div class="mb-4 h-5 w-20 rounded bg-bg-elevated"></div>
						<div class="space-y-3">
							{#each [0, 1, 2, 3, 4] as __ (__)}
								<div class="h-8 rounded bg-bg-elevated"></div>
							{/each}
						</div>
					</div>
				{/each}
			</div>

			<!-- Timeline skeleton -->
			<div class="animate-pulse rounded-lg border border-border bg-bg-surface p-6">
				<div class="mb-4 h-5 w-32 rounded bg-bg-elevated"></div>
				<div class="h-64 rounded bg-bg-elevated"></div>
			</div>
		</div>

	{:else if isEmpty}
		<!-- T105: Empty state with period expansion suggestion -->
		<div class="rounded-lg border border-border bg-bg-surface px-6 py-12 text-center">
			<p class="text-lg font-semibold text-text">No incidents in this period</p>
			<p class="mt-2 text-sm text-text-muted">
				Try expanding the selected period or removing active filters to see more data.
			</p>
			<p class="mt-1 text-xs text-text-muted">
				Tip: Switch from <span class="font-medium">Week</span> to <span class="font-medium">Month</span> or <span class="font-medium">Quarter</span> for a broader view.
			</p>
		</div>

	{:else}
		<!-- Summary (full-width) -->
		<SummaryCard {summary} />

		<!-- 2-col grid for heatmaps -->
		<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
			<CategoryHeatmap stats={byCategory} />
			<TeamHeatmap stats={byTeam} />
		</div>

		<!-- Timeline (full-width) -->
		<PatternTimeline points={timeline} />
	{/if}
</div>
