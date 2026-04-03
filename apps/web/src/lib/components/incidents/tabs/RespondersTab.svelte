<script lang="ts">
	import { listResponders } from '$lib/services/incidents';
	import type { Responder } from '$lib/types/responder';

	let { incidentId, active }: { incidentId: string; active: boolean } = $props();

	let responders = $state<Responder[]>([]);
	let total = $state(0);
	let loading = $state(false);
	let error = $state('');
	let loaded = $state(false);
	let expanded = $state(false);

	$effect(() => {
		if (active && !loaded) {
			load();
		}
	});

	async function load() {
		loading = true;
		error = '';
		try {
			const result = await listResponders(incidentId);
			responders = result.items;
			total = result.total;
			loaded = true;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error loading responders';
		} finally {
			loading = false;
		}
	}

	let visibleResponders = $derived(expanded ? responders : responders.slice(0, 10));

	function formatDate(iso: string): string {
		return new Date(iso).toLocaleString();
	}

	function truncateId(id: string): string {
		return id.slice(0, 8) + '...';
	}
</script>

{#if loading}
	<div class="space-y-3">
		{#each [0, 1, 2] as i (i)}
			<div class="h-14 animate-pulse rounded bg-bg-elevated"></div>
		{/each}
	</div>
{:else if error}
	<div class="text-sm text-error">
		{error}
		<button onclick={load} class="ml-2 underline hover:no-underline">Retry</button>
	</div>
{:else if responders.length === 0}
	<p class="text-sm text-text-muted">No responders recorded.</p>
{:else}
	<div class="space-y-3">
		{#each visibleResponders as responder (responder.id)}
			<div class="rounded border border-border bg-bg-surface p-3 text-sm">
				<div class="flex items-center justify-between">
					<span class="font-mono text-xs text-text-muted">{truncateId(responder.user_id)}</span>
					<span class="rounded bg-bg-elevated px-2 py-0.5 text-xs text-text">{responder.role}</span>
				</div>
				<div class="mt-1 text-xs text-text-muted">
					Joined: {formatDate(responder.joined_at)}
					{#if responder.left_at}
						· Left: {formatDate(responder.left_at)}
					{/if}
				</div>
				{#if responder.contribution_summary}
					<p class="mt-1 text-text-muted">{responder.contribution_summary}</p>
				{/if}
			</div>
		{/each}

		{#if total > 10}
			<button onclick={() => (expanded = !expanded)} class="text-sm text-accent hover:underline">
				{expanded ? '▲ Hide' : `▼ Show all (${total})`}
			</button>
		{/if}
	</div>
{/if}
