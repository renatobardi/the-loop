<script lang="ts">
	import type { TeamStats } from '$lib/types/analytics';
	import { formatCategory, sortTeamsByCount } from '$lib/utils/analytics';
	import Badge from '$lib/ui/Badge.svelte';

	let {
		stats,
		onDrillDown
	}: {
		stats: TeamStats[];
		onDrillDown?: (_: string) => void; // eslint-disable-line no-unused-vars
	} = $props();

	let sortAsc = $state(false);

	const sorted = $derived(sortTeamsByCount(stats, sortAsc));

	function toggleSort() {
		sortAsc = !sortAsc;
	}
</script>

<div class="rounded-lg border border-border bg-bg-surface p-6">
	<h2 class="mb-4 text-lg font-semibold text-text">By Team</h2>
	{#if stats.length === 0}
		<p class="text-text-muted">No incidents in this period.</p>
	{:else}
		<div class="overflow-x-auto">
			<table class="w-full text-sm">
				<thead>
					<tr class="border-b border-border">
						<th class="pb-2 text-left font-medium text-text-muted">Team</th>
						<th class="pb-2 text-left font-medium text-text-muted">
							<button
								class="flex items-center gap-1 hover:text-text"
								onclick={toggleSort}
								aria-label="Sort by count {sortAsc ? 'descending' : 'ascending'}"
							>
								Count
								<span class="text-xs">{sortAsc ? '▲' : '▼'}</span>
							</button>
						</th>
						<th class="pb-2 text-left font-medium text-text-muted">Top Categories</th>
						<th class="pb-2 text-left font-medium text-text-muted">Avg Resolution</th>
					</tr>
				</thead>
				<tbody>
					{#each sorted as row (row.team)}
						<tr
							class="border-b border-border/50 hover:bg-bg-elevated/50 {onDrillDown ? 'cursor-pointer' : ''}"
							onclick={() => onDrillDown?.(row.team)}
							onkeydown={(e) => e.key === 'Enter' && onDrillDown?.(row.team)}
							role={onDrillDown ? 'button' : undefined}
							tabindex={onDrillDown ? 0 : undefined}
							aria-label={onDrillDown ? `Filter by team ${row.team}` : undefined}
						>
							<td class="py-2 font-medium text-text">{row.team}</td>
							<td class="py-2 text-text">{row.count}</td>
							<td class="py-2">
								<div class="flex flex-wrap gap-1">
									{#each row.top_categories as cat (cat)}
										<Badge variant="default" class="px-2 py-0.5 text-xs">
											{formatCategory(cat)}
										</Badge>
									{/each}
								</div>
							</td>
							<td class="py-2 text-text-muted">
								{row.avg_resolution_days !== null ? `${row.avg_resolution_days.toFixed(1)}d` : 'N/A'}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
