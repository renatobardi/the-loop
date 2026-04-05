<script lang="ts">
	import type { SeverityTrendPoint } from '$lib/types/analytics';

	let { data }: { data: SeverityTrendPoint[] } = $props();

	const SVG_WIDTH = 800;
	const SVG_HEIGHT = 240;
	const PADDING = { top: 16, right: 24, bottom: 40, left: 40 };
	const CHART_W = SVG_WIDTH - PADDING.left - PADDING.right;
	const CHART_H = SVG_HEIGHT - PADDING.top - PADDING.bottom;

	let tooltip = $state<{ x: number; y: number; point: SeverityTrendPoint } | null>(null);

	const maxTotal = $derived(Math.max(...data.map((p) => p.error_count + p.warning_count), 1));

	function cx(i: number): number {
		if (data.length <= 1) return PADDING.left + CHART_W / 2;
		return PADDING.left + (i / (data.length - 1)) * CHART_W;
	}

	function cy(val: number): number {
		return PADDING.top + CHART_H - (val / maxTotal) * CHART_H;
	}

	// Build stacked area path: errors stacked on top of warnings
	function buildAreaPath(values: number[], baselines: number[]): string {
		if (data.length === 0) return '';
		const top = values.map((v, i) => ({ x: cx(i), y: cy(baselines[i] + v) }));
		const base = baselines.map((b, i) => ({ x: cx(i), y: cy(b) }));
		const forward = top.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
		const backward = base
			.slice()
			.reverse()
			.map((p) => `L ${p.x} ${p.y}`)
			.join(' ');
		return `${forward} ${backward} Z`;
	}

	const warningBaselines = $derived(data.map(() => 0));
	const warningValues = $derived(data.map((p) => p.warning_count));
	const errorBaselines = $derived(data.map((p) => p.warning_count));
	const errorValues = $derived(data.map((p) => p.error_count));

	const warningPath = $derived(buildAreaPath(warningValues, warningBaselines));
	const errorPath = $derived(buildAreaPath(errorValues, errorBaselines));

	const monthLabels = $derived(
		data
			.map((p, i) => ({ p, i }))
			.filter(({ i }) => i % 4 === 0)
			.map(({ p, i }) => ({
				label: new Date(p.week).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
				x: cx(i)
			}))
	);

	function handleMouseOver(e: MouseEvent, point: SeverityTrendPoint) {
		const rect = (e.currentTarget as SVGElement).closest('svg')!.getBoundingClientRect();
		tooltip = { x: e.clientX - rect.left, y: e.clientY - rect.top, point };
	}

	function handleMouseOut() {
		tooltip = null;
	}

	function handleFocus(e: FocusEvent, point: SeverityTrendPoint) {
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
	<div class="mb-4 flex items-center justify-between">
		<h2 class="text-lg font-semibold text-text">Severity Trend</h2>
		<div class="flex gap-4">
			<div class="flex items-center gap-1.5">
				<span class="h-3 w-3 rounded-full" style="background: var(--color-chart-error)"></span>
				<span class="text-xs text-text-muted">Error</span>
			</div>
			<div class="flex items-center gap-1.5">
				<span class="h-3 w-3 rounded-full" style="background: var(--color-chart-warning)"></span>
				<span class="text-xs text-text-muted">Warning</span>
			</div>
		</div>
	</div>

	{#if data.length === 0}
		<p class="text-text-muted">No severity data in this period.</p>
	{:else}
		<div class="relative overflow-x-auto">
			<svg
				width={SVG_WIDTH}
				height={SVG_HEIGHT}
				viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
				role="img"
				aria-label="Severity trend chart — stacked area of error and warning counts per week"
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
					<text
						x={PADDING.left - 4}
						y={y + 4}
						text-anchor="end"
						font-size="10"
						fill="currentColor"
						opacity="0.5"
					>
						{Math.round(frac * maxTotal)}
					</text>
				{/each}

				<!-- Warning area (bottom) -->
				<path d={warningPath} fill="var(--color-chart-warning)" fill-opacity="0.3" stroke="none" />
				<path
					d={data.map((p, i) => `${i === 0 ? 'M' : 'L'} ${cx(i)} ${cy(p.warning_count)}`).join(' ')}
					fill="none"
					stroke="var(--color-chart-warning)"
					stroke-width="1.5"
					stroke-linejoin="round"
				/>

				<!-- Error area (stacked on top) -->
				<path d={errorPath} fill="var(--color-chart-error)" fill-opacity="0.3" stroke="none" />
				<path
					d={data
						.map((p, i) => `${i === 0 ? 'M' : 'L'} ${cx(i)} ${cy(p.warning_count + p.error_count)}`)
						.join(' ')}
					fill="none"
					stroke="var(--color-chart-error)"
					stroke-width="1.5"
					stroke-linejoin="round"
				/>

				<!-- Hover targets -->
				{#each data as point, i (point.week)}
					<circle
						cx={cx(i)}
						cy={cy(point.warning_count + point.error_count)}
						r="5"
						fill="transparent"
						stroke="transparent"
						stroke-width="12"
						role="button"
						tabindex="0"
						aria-label={`Week of ${point.week}: ${point.error_count} errors, ${point.warning_count} warnings`}
						onmouseover={(e) => handleMouseOver(e, point)}
						onmouseout={handleMouseOut}
						onfocus={(e) => handleFocus(e, point)}
						onblur={handleBlur}
						style="cursor: default"
					/>
				{/each}

				<!-- X-axis labels -->
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
					class="pointer-events-none absolute z-10 rounded border border-border bg-bg-elevated px-3 py-2 text-sm shadow-glow"
					style="left: {Math.min(tooltip.x + 12, SVG_WIDTH - 180)}px; top: {Math.max(0, tooltip.y - 60)}px"
				>
					<div class="mb-1 font-medium text-text">Week of {tooltip.point.week}</div>
					<div class="flex items-center gap-1.5 text-xs text-text-muted">
						<span class="h-2 w-2 rounded-full" style="background: var(--color-chart-error)"></span>
						Errors: {tooltip.point.error_count}
					</div>
					<div class="flex items-center gap-1.5 text-xs text-text-muted">
						<span
							class="h-2 w-2 rounded-full"
							style="background: var(--color-chart-warning)"
						></span>
						Warnings: {tooltip.point.warning_count}
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>
