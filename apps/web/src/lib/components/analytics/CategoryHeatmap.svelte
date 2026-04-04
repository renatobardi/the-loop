<script lang="ts">
	import type { CategoryStats } from '$lib/types/analytics';

	let { stats }: { stats: CategoryStats[] } = $props();

	const BAR_HEIGHT = 32;
	const BAR_GAP = 12;
	const LABEL_WIDTH = 160;
	const COUNT_WIDTH = 48;
	const SVG_WIDTH = 600;
	const BAR_AREA = SVG_WIDTH - LABEL_WIDTH - COUNT_WIDTH - 16;

	let tooltip = $state<{ x: number; y: number; item: CategoryStats } | null>(null);

	const maxCount = $derived(Math.max(...stats.map((s) => s.count), 1));
	const svgHeight = $derived(stats.length * (BAR_HEIGHT + BAR_GAP) + BAR_GAP);

	function barColor(avgSeverity: number): string {
		// 1.0 = error (red), 0.5 = warning (yellow)
		return avgSeverity >= 0.9 ? 'var(--color-error, #ef4444)' : 'var(--color-warning, #f59e0b)';
	}

	function formatCategory(cat: string): string {
		return cat.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
	}

	function handleMouseOver(e: MouseEvent, item: CategoryStats) {
		const rect = (e.currentTarget as SVGElement).closest('svg')!.getBoundingClientRect();
		tooltip = { x: e.clientX - rect.left, y: e.clientY - rect.top, item };
	}

	function handleMouseOut() {
		tooltip = null;
	}
</script>

<div class="rounded-lg border border-border bg-bg-surface p-6">
	<h2 class="mb-4 text-lg font-semibold text-text">By Root Cause</h2>
	{#if stats.length === 0}
		<p class="text-text-muted">No incidents in this period.</p>
	{:else}
		<div class="relative overflow-x-auto">
			<svg
				width={SVG_WIDTH}
				height={svgHeight}
				role="img"
				aria-label="Incident count by root cause category"
				class="w-full"
				viewBox={`0 0 ${SVG_WIDTH} ${svgHeight}`}
			>
				{#each stats as item, i (item.category)}
					{@const y = BAR_GAP + i * (BAR_HEIGHT + BAR_GAP)}
					{@const barW = (item.count / maxCount) * BAR_AREA}
					<!-- Label -->
					<text
						x={LABEL_WIDTH - 8}
						y={y + BAR_HEIGHT / 2 + 5}
						text-anchor="end"
						font-size="13"
						fill="currentColor"
						class="text-text-muted"
					>
						{formatCategory(item.category)}
					</text>
					<!-- Bar -->
					<rect
						x={LABEL_WIDTH}
						{y}
						width={Math.max(barW, 2)}
						height={BAR_HEIGHT}
						rx="4"
						fill={barColor(item.avg_severity)}
						opacity="0.85"
						role="graphics-symbol"
						aria-label={`${item.category}: ${item.count} incidents (${item.percentage.toFixed(1)}%)`}
						onmouseover={(e) => handleMouseOver(e, item)}
						onmouseout={handleMouseOut}
						style="cursor: pointer"
					/>
					<!-- Count -->
					<text
						x={LABEL_WIDTH + BAR_AREA + 8}
						y={y + BAR_HEIGHT / 2 + 5}
						font-size="13"
						fill="currentColor"
						class="font-medium text-text"
					>
						{item.count}
					</text>
				{/each}
			</svg>

			{#if tooltip}
				<div
					class="pointer-events-none absolute z-10 rounded border border-border bg-bg-elevated px-3 py-2 text-sm shadow-glow"
					style="left: {tooltip.x + 12}px; top: {tooltip.y - 8}px"
				>
					<div class="font-medium text-text">{formatCategory(tooltip.item.category)}</div>
					<div class="text-text-muted">
						{tooltip.item.count} incidents · {tooltip.item.percentage.toFixed(1)}%
					</div>
					<div class="text-text-muted">
						Avg severity: {tooltip.item.avg_severity >= 0.9 ? 'Error' : 'Warning'}
					</div>
					{#if tooltip.item.avg_resolution_days !== null}
						<div class="text-text-muted">
							Avg resolution: {tooltip.item.avg_resolution_days.toFixed(1)}d
						</div>
					{/if}
				</div>
			{/if}
		</div>
	{/if}
</div>
