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
		onFiltersChange
	}: {
		summary: AnalyticsSummary;
		byCategory: CategoryStats[];
		byTeam: TeamStats[];
		byTeamAll: TeamStats[];
		timeline: TimelinePoint[];
		filters: AnalyticsFilter;
		onFiltersChange: (_: AnalyticsFilter) => void; // eslint-disable-line no-unused-vars
	} = $props();
</script>

<div class="space-y-6">
	<!-- Sticky filter bar -->
	<div class="sticky top-0 z-20 bg-bg pb-2 pt-4">
		<AnalyticsFilters {filters} teamOptions={byTeamAll} onApply={onFiltersChange} />
	</div>

	<!-- Summary (full-width) -->
	<SummaryCard {summary} />

	<!-- 2-col grid for heatmaps -->
	<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
		<CategoryHeatmap stats={byCategory} />
		<TeamHeatmap stats={byTeam} />
	</div>

	<!-- Timeline (full-width) -->
	<PatternTimeline points={timeline} />
</div>
