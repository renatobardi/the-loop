<script lang="ts">
	import { Container, Card } from '$lib/ui';
	import { getAdminMetrics } from '$lib/services/admin';
	import type { AdminMetrics } from '$lib/types/rules';

	let metrics = $state<AdminMetrics | null>(null);
	let error = $state<string | null>(null);
	let loading = $state(true);

	$effect(() => {
		getAdminMetrics()
			.then((data) => {
				metrics = data;
			})
			.catch((err: unknown) => {
				error = err instanceof Error ? err.message : 'Failed to load metrics';
			})
			.finally(() => {
				loading = false;
			});
	});

	const maxCount = $derived.by(() => {
		if (!metrics?.scans_by_week.length) return 1;
		return Math.max(...metrics.scans_by_week.map((w) => w.count), 1);
	});
</script>

<Container>
	<div class="py-8">
		<div class="mb-6">
			<h1 class="text-2xl font-bold text-text">Admin Metrics</h1>
			<p class="mt-1 text-sm text-text-muted">Global platform adoption overview</p>
		</div>

		{#if loading}
			<p class="text-sm text-text-muted">Loading metrics…</p>
		{:else if error}
			<p class="text-sm text-error" role="alert">{error}</p>
		{:else if metrics}
			<div class="grid gap-4 sm:grid-cols-3 mb-8">
				<Card>
					<div class="p-4">
						<p class="text-xs text-text-muted uppercase tracking-wide">Active Repos</p>
						<p class="text-3xl font-bold text-accent mt-1">{metrics.active_repos}</p>
						<p class="text-xs text-text-muted mt-1">last 30 days</p>
					</div>
				</Card>
				<Card>
					<div class="p-4">
						<p class="text-xs text-text-muted uppercase tracking-wide">Total Scans</p>
						<p class="text-3xl font-bold text-text mt-1">
							{metrics.scans_by_week.reduce((s, w) => s + w.count, 0)}
						</p>
						<p class="text-xs text-text-muted mt-1">all time</p>
					</div>
				</Card>
				<Card>
					<div class="p-4">
						<p class="text-xs text-text-muted uppercase tracking-wide">Top Language</p>
						<p class="text-3xl font-bold text-text mt-1">
							{metrics.top_languages[0]?.language ?? '—'}
						</p>
						<p class="text-xs text-text-muted mt-1">
							{metrics.top_languages[0]?.count ?? 0} findings
						</p>
					</div>
				</Card>
			</div>

			<!-- Scans by week sparkline -->
			<Card>
				<div class="p-4">
					<p class="text-sm font-medium text-text mb-3">Scans by Week</p>
					{#if metrics.scans_by_week.length}
						<div class="flex items-end gap-1 h-16">
							{#each metrics.scans_by_week.slice(-24) as week}
								<div class="flex-1 flex flex-col items-center gap-0.5">
									<div
										class="w-full rounded-sm bg-accent/60"
										style="height: {Math.max(4, (week.count / maxCount) * 56)}px"
										title="{week.week}: {week.count} scans, {week.findings} findings"
									></div>
								</div>
							{/each}
						</div>
						<p class="text-xs text-text-muted mt-2">Last {Math.min(metrics.scans_by_week.length, 24)} weeks</p>
					{:else}
						<p class="text-sm text-text-muted">No scan data yet.</p>
					{/if}
				</div>
			</Card>

			<!-- Top languages -->
			{#if metrics.top_languages.length}
				<Card>
					<div class="p-4 mt-4">
						<p class="text-sm font-medium text-text mb-3">Top Languages</p>
						<div class="space-y-2">
							{#each metrics.top_languages as lang}
								<div class="flex items-center justify-between">
									<span class="text-sm text-text">{lang.language}</span>
									<span class="text-sm text-text-muted">{lang.count} findings</span>
								</div>
							{/each}
						</div>
					</div>
				</Card>
			{/if}
		{/if}
	</div>
</Container>
