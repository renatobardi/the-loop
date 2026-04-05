<script lang="ts">
	import type {
		AnalyticsSummary,
		CategoryStats,
		SeverityTrendPoint,
		TeamStats
	} from '$lib/types/analytics';
	import { formatDays } from '$lib/utils/analytics';

	let {
		summary,
		byCategory = [],
		byTeam = [],
		severityTrend = []
	}: {
		summary: AnalyticsSummary;
		byCategory?: CategoryStats[];
		byTeam?: TeamStats[];
		severityTrend?: SeverityTrendPoint[];
	} = $props();

	const totalErrors = $derived(severityTrend.reduce((acc, p) => acc + p.error_count, 0));
	const totalWarnings = $derived(severityTrend.reduce((acc, p) => acc + p.warning_count, 0));
	const topCategory = $derived(
		byCategory[0]?.category
			? byCategory[0].category.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
			: '—'
	);
	const topTeam = $derived(byTeam[0]?.team ?? '—');

	const kpis = $derived([
		{ label: 'Total', value: String(summary.total), color: 'text-text' },
		{ label: 'Resolved', value: String(summary.resolved), color: 'text-success' },
		{ label: 'Unresolved', value: String(summary.unresolved), color: 'text-error' },
		{ label: 'MTTR', value: formatDays(summary.avg_resolution_days), color: 'text-accent' },
		{ label: 'Errors', value: String(totalErrors), color: 'text-error' },
		{ label: 'Warnings', value: String(totalWarnings), color: 'text-warning' },
		{ label: 'Top Category', value: topCategory, color: 'text-text', small: true },
		{ label: 'Top Team', value: topTeam, color: 'text-text', small: true }
	]);
</script>

<div class="rounded-lg border border-border bg-bg-surface p-6">
	<h2 class="mb-4 text-lg font-semibold text-text">Summary</h2>
	<div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
		{#each kpis as kpi (kpi.label)}
			<div class="flex flex-col">
				<span
					class="{kpi.small ? 'text-base font-semibold' : 'text-3xl font-bold'} {kpi.color} truncate"
					title={kpi.value}
				>
					{kpi.value}
				</span>
				<span class="mt-1 text-sm text-text-muted">{kpi.label}</span>
			</div>
		{/each}
	</div>
</div>
