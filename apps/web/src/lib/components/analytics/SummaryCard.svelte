<script lang="ts">
	import type { AnalyticsSummary } from '$lib/types/analytics';

	let { summary }: { summary: AnalyticsSummary } = $props();

	function formatDays(days: number | null): string {
		if (days === null) return 'N/A';
		return `${days.toFixed(1)}d`;
	}
</script>

<div class="rounded-lg border border-border bg-bg-surface p-6">
	<h2 class="mb-4 text-lg font-semibold text-text">Summary</h2>
	<div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
		<div class="flex flex-col">
			<span class="text-3xl font-bold text-text">{summary.total}</span>
			<span class="mt-1 text-sm text-text-muted">Total</span>
		</div>
		<div class="flex flex-col">
			<span class="text-3xl font-bold text-success">{summary.resolved}</span>
			<span class="mt-1 text-sm text-text-muted">Resolved</span>
		</div>
		<div class="flex flex-col">
			<span class="text-3xl font-bold text-error">{summary.unresolved}</span>
			<span class="mt-1 text-sm text-text-muted">Unresolved</span>
		</div>
		<div class="flex flex-col">
			<span class="text-3xl font-bold text-accent">{formatDays(summary.avg_resolution_days)}</span>
			<span class="mt-1 text-sm text-text-muted">Avg Resolution</span>
		</div>
	</div>
</div>
