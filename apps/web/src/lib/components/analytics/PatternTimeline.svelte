<script lang="ts">
	import type { TimelinePoint, RootCauseCategory } from '$lib/types/analytics';
	import { formatCategory } from '$lib/utils/analytics';

	let { points }: { points: TimelinePoint[] } = $props();

	const SVG_WIDTH = 800;
	const SVG_HEIGHT = 260;
	const PADDING = { top: 16, right: 24, bottom: 48, left: 40 };
	const CHART_W = SVG_WIDTH - PADDING.left - PADDING.right;
	const CHART_H = SVG_HEIGHT - PADDING.top - PADDING.bottom;

	const CATEGORIES: RootCauseCategory[] = [
		'code_pattern',
		'infrastructure',
		'process_breakdown',
		'third_party',
		'unknown'
	];

	const COLORS: Record<RootCauseCategory, string> = {
		code_pattern: '#3b82f6',
		infrastructure: '#ef4444',
		process_breakdown: '#f59e0b',
		third_party: '#8b5cf6',
		unknown: '#6b7280'
	};

	let tooltip = $state<{ x: number; y: number; point: TimelinePoint } | null>(null);

	const maxCount = $derived(Math.max(...points.map((p) => p.count), 1));

	function cx(i: number): number {
		if (points.length <= 1) return PADDING.left + CHART_W / 2;
		return PADDING.left + (i / (points.length - 1)) * CHART_W;
	}

	function cy(val: number): number {
		return PADDING.top + CHART_H - (val / maxCount) * CHART_H;
	}

	function buildPath(cat: RootCauseCategory): string {
		return points
			.map((p, i) => `${i === 0 ? 'M' : 'L'} ${cx(i)} ${cy(p.by_category[cat] ?? 0)}`)
			.join(' ');
	}

	// Monthly labels: one tick per ~4 weeks
	const monthLabels = $derived(
		points
			.map((p, i) => ({ p, i }))
			.filter(({ i }) => i % 4 === 0)
			.map(({ p, i }) => ({
				label: new Date(p.week).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
				x: cx(i)
			}))
	);

function handleMouseOver(e: MouseEvent, point: TimelinePoint) {
		const rect = (e.currentTarget as SVGElement).closest('svg')!.getBoundingClientRect();
		tooltip = { x: e.clientX - rect.left, y: e.clientY - rect.top, point };
	}

	function handleMouseOut() {
		tooltip = null;
	}

	function handleFocus(e: FocusEvent, point: TimelinePoint) {
		const el = e.currentTarget as SVGElement;
		const rect = el.closest('svg')!.getBoundingClientRect();
		const selfRect = el.getBoundingClientRect();
		tooltip = { x: selfRect.left - rect.left, y: selfRect.top - rect.top, point };
	}

	function handleBlur() {
		tooltip = null;
	}
</script>

<div class="rounded-lg border border-border bg-bg-surface p-6">
	<h2 class="mb-4 text-lg font-semibold text-text">Pattern Timeline</h2>

	<!-- Legend -->
	<div class="mb-4 flex flex-wrap gap-4">
		{#each CATEGORIES as cat (cat)}
			<div class="flex items-center gap-1.5">
				<span class="h-3 w-3 rounded-full" style="background: {COLORS[cat]}"></span>
				<span class="text-xs text-text-muted">{formatCategory(cat)}</span>
			</div>
		{/each}
	</div>

	{#if points.length === 0}
		<p class="text-text-muted">No timeline data in this period.</p>
	{:else}
		<div class="relative overflow-x-auto">
			<svg
				width={SVG_WIDTH}
				height={SVG_HEIGHT}
				viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
				role="img"
				aria-label="Incident pattern timeline — 5 lines, one per root cause category"
				class="w-full"
			>
				<!-- Y-axis gridlines -->
				{#each [0, 0.25, 0.5, 0.75, 1] as frac (frac)}
					{@const y = PADDING.top + CHART_H * (1 - frac)}
					<line
						x1={PADDING.left}
						y1={y}
						x2={PADDING.left + CHART_W}
						y2={y}
						stroke="currentColor"
						stroke-opacity="0.1"
						stroke-width="1"
					/>
					<text x={PADDING.left - 4} y={y + 4} text-anchor="end" font-size="10" fill="currentColor" opacity="0.5">
						{Math.round(frac * maxCount)}
					</text>
				{/each}

				<!-- Lines per category -->
				{#each CATEGORIES as cat (cat)}
					<path
						d={buildPath(cat)}
						fill="none"
						stroke={COLORS[cat]}
						stroke-width="2"
						stroke-linejoin="round"
						stroke-linecap="round"
					/>
				{/each}

				<!-- Hover dots (total count) -->
				{#each points as point, i (point.week)}
					<circle
						cx={cx(i)}
						cy={cy(point.count)}
						r="5"
						fill="transparent"
						stroke="transparent"
						stroke-width="12"
						role="button"
						tabindex="0"
						aria-label={`Week of ${point.week}: ${point.count} incidents`}
						onmouseover={(e) => handleMouseOver(e, point)}
						onmouseout={handleMouseOut}
						onfocus={(e) => handleFocus(e, point)}
						onblur={handleBlur}
						style="cursor: pointer"
					/>
				{/each}

				<!-- X-axis month labels -->
				{#each monthLabels as { label, x } (label)}
					<text
						{x}
						y={SVG_HEIGHT - 8}
						text-anchor="middle"
						font-size="11"
						fill="currentColor"
						opacity="0.6"
					>
						{label}
					</text>
				{/each}
			</svg>

			{#if tooltip}
				<div
					class="pointer-events-none absolute z-10 min-w-40 rounded border border-border bg-bg-elevated px-3 py-2 text-sm shadow-glow"
					style="left: {tooltip.x + 12}px; top: {Math.max(0, tooltip.y - 80)}px"
				>
					<div class="mb-1 font-medium text-text">Week of {tooltip.point.week}</div>
					<div class="mb-1 text-text-muted">Total: {tooltip.point.count}</div>
					{#each CATEGORIES as cat (cat)}
						<div class="flex items-center gap-1.5 text-xs text-text-muted">
							<span class="h-2 w-2 rounded-full" style="background: {COLORS[cat]}"></span>
							{formatCategory(cat)}: {tooltip.point.by_category[cat] ?? 0}
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>
