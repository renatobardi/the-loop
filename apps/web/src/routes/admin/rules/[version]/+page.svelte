<script lang="ts">
	import { page } from '$app/state';
	import { Container, Card, Button, Badge } from '$lib/ui';
	import type { RuleData } from '$lib/types/rules';

	const API_BASE =
		(typeof window !== 'undefined' && (window as Window & { __env?: Record<string, string> }).__env?.PUBLIC_API_BASE_URL) ||
		'https://api.loop.oute.pro';

	let version = $derived(page.params.version ?? '');
	let rules = $state<RuleData[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	$effect(() => {
		const v = version;
		loading = true;
		error = null;
		fetch(`${API_BASE}/api/v1/rules/${v}`)
			.then((r) => {
				if (!r.ok) throw new Error(`HTTP ${r.status}`);
				return r.json();
			})
			.then((data: { rules: RuleData[] }) => {
				rules = data.rules ?? [];
			})
			.catch((err: unknown) => {
				error = err instanceof Error ? err.message : 'Failed to load rules';
			})
			.finally(() => {
				loading = false;
			});
	});

	function severityVariant(severity: string): 'error' | 'default' {
		return severity === 'ERROR' ? 'error' : 'default';
	}
</script>

<Container>
	<div class="py-8">
		<div class="mb-6 flex items-center justify-between">
			<div>
				<a href="/admin/rules/" class="text-sm text-accent hover:underline">← All versions</a>
				<h1 class="text-2xl font-bold text-text mt-1">Version {version}</h1>
				<p class="mt-1 text-sm text-text-muted">{rules.length} rules</p>
			</div>
			<a
				href="/admin/rules/{version}/publish/"
				class="rounded-md bg-accent px-4 py-2 text-sm font-semibold text-white hover:bg-accent-hover transition-colors"
			>
				Publish
			</a>
		</div>

		{#if loading}
			<p class="text-sm text-text-muted">Loading rules…</p>
		{:else if error}
			<p class="text-sm text-error" role="alert">{error}</p>
		{:else if rules.length === 0}
			<p class="text-sm text-text-muted">No rules in this version.</p>
		{:else}
			<div class="space-y-2">
				{#each rules as rule}
					<Card>
						<div class="p-4 flex items-start justify-between gap-4">
							<div class="min-w-0 flex-1">
								<div class="flex items-center gap-2 mb-1">
									<span class="font-mono text-sm font-semibold text-text">{rule.id}</span>
									<Badge variant={severityVariant(rule.severity)}>{rule.severity}</Badge>
								</div>
								<p class="text-sm text-text-muted truncate">{rule.message}</p>
								<p class="text-xs text-text-muted mt-1">{rule.languages.join(', ')}</p>
							</div>
							<a
								href="/admin/rules/{version}/edit/?rule_id={rule.id}"
								class="shrink-0 text-sm text-accent hover:underline"
							>
								Edit
							</a>
						</div>
					</Card>
				{/each}
			</div>
		{/if}
	</div>
</Container>
