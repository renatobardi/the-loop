<script lang="ts">
	import { Container, Section } from '$lib/ui';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const { summary } = data;
	const isEmpty = $derived(summary.total_scans === 0);

	// Sparkline computation
	const MAX_WEEKS = 8;
	const weekData = $derived(summary.scans_by_week.slice(-MAX_WEEKS));
	const maxFindings = $derived(Math.max(...weekData.map((w) => w.findings), 1));

	// SVG sparkline dimensions
	const SPARK_W = 400;
	const SPARK_H = 60;
	const sparkPoints = $derived(
		weekData.length < 2
			? ''
			: weekData
					.map((w, i) => {
						const x = (i / (weekData.length - 1)) * SPARK_W;
						const y = SPARK_H - (w.findings / maxFindings) * SPARK_H;
						return `${x},${y}`;
					})
					.join(' ')
	);
</script>

<Container>
	<Section>
		<div class="py-8">
			<!-- Header -->
			<div class="mb-8">
				<h1 class="text-2xl font-bold text-text">Violations Dashboard</h1>
				<p class="mt-1 text-sm text-text-muted">Semgrep scan results across your repositories</p>
			</div>

			{#if data.loadError}
				<div
					class="rounded-lg border border-error/40 bg-error/10 px-6 py-5"
					role="alert"
					aria-live="assertive"
				>
					<p class="font-medium text-error">Failed to load scan data</p>
					<p class="mt-1 text-sm text-error/80">{data.loadError}</p>
				</div>
			{:else if isEmpty}
				<!-- Empty state -->
				<div class="flex flex-col items-center justify-center py-24 text-center">
					<svg
						class="mb-6 h-16 w-16 text-text-muted"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
						stroke-width="1.5"
						aria-hidden="true"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
					<h2 class="text-xl font-semibold text-text">No scans yet</h2>
					<p class="mt-2 max-w-sm text-text-muted">
						No scan data available. Connect your repositories to start detecting violations.
					</p>
					<a
						href="/settings/"
						class="mt-6 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover focus:outline-none focus:ring-2 focus:ring-accent"
					>
						Go to Settings
					</a>
				</div>
			{:else}
				<!-- Stats cards -->
				<div class="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
					<div class="rounded-lg border border-border bg-bg-surface p-6">
						<p class="text-sm text-text-muted">Total Scans</p>
						<p class="mt-2 text-3xl font-bold text-text">{summary.total_scans.toLocaleString()}</p>
					</div>
					<div class="rounded-lg border border-border bg-bg-surface p-6">
						<p class="text-sm text-text-muted">Total Findings</p>
						<p class="mt-2 text-3xl font-bold text-text">
							{summary.total_findings.toLocaleString()}
						</p>
					</div>
					<div class="rounded-lg border border-border bg-bg-surface p-6">
						<p class="text-sm text-text-muted">Active Repos</p>
						<p class="mt-2 text-3xl font-bold text-text">{summary.active_repos.toLocaleString()}</p>
					</div>
				</div>

				<!-- Charts row -->
				<div class="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
					<!-- Weekly findings sparkline -->
					<div class="rounded-lg border border-border bg-bg-surface p-6">
						<h2 class="mb-4 text-sm font-semibold text-text">Weekly Findings</h2>
						{#if weekData.length >= 2}
							<svg
								viewBox="0 0 {SPARK_W} {SPARK_H}"
								class="h-16 w-full text-accent"
								preserveAspectRatio="none"
								aria-hidden="true"
							>
								<polyline points={sparkPoints} fill="none" stroke="currentColor" stroke-width="2" />
							</svg>
							<!-- Week labels -->
							<div class="mt-2 flex justify-between">
								{#each weekData as w (w.week)}
									<span class="text-xs text-text-muted">{w.week.replace(/^\d{4}-/, '')}</span>
								{/each}
							</div>
						{:else}
							<p class="text-sm text-text-muted">Not enough data to display chart.</p>
						{/if}
					</div>

					<!-- Top rules -->
					<div class="rounded-lg border border-border bg-bg-surface p-6">
						<h2 class="mb-4 text-sm font-semibold text-text">Top Rules</h2>
						{#if summary.top_rules.length === 0}
							<p class="text-sm text-text-muted">No rules data available.</p>
						{:else}
							<div class="flex flex-col gap-3">
								{#each summary.top_rules.slice(0, 5) as rule, i (rule.rule_id)}
									<div class="flex items-center gap-3">
										<span class="w-4 text-sm text-text-muted">{i + 1}</span>
										<code class="flex-1 truncate text-xs font-mono text-accent">{rule.rule_id}</code>
										<div class="h-1.5 w-24 overflow-hidden rounded-full bg-bg">
											<div
												class="h-full rounded-full bg-accent"
												style="width: {(rule.count / (summary.top_rules[0]?.count || 1)) * 100}%"
											></div>
										</div>
										<span class="w-6 text-right text-xs text-text-muted">{rule.count}</span>
									</div>
								{/each}
							</div>
						{/if}
					</div>
				</div>
			{/if}
		</div>
	</Section>
</Container>
