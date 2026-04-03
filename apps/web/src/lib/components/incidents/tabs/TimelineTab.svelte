<script lang="ts">
	import { listTimelineEvents } from '$lib/services/incidents';
	import type { TimelineEvent } from '$lib/types/timeline_event';

	let { incidentId, active }: { incidentId: string; active: boolean } = $props();

	let events = $state<TimelineEvent[]>([]);
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
			const result = await listTimelineEvents(incidentId);
			events = result.items;
			total = result.total;
			loaded = true;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Erro ao carregar timeline';
		} finally {
			loading = false;
		}
	}

	let visibleEvents = $derived(expanded ? events : events.slice(0, 10));

	function formatDate(iso: string): string {
		return new Date(iso).toLocaleString('pt-BR');
	}
</script>

{#if loading}
	<div class="space-y-3">
		{#each [0, 1, 2] as i (i)}
			<div class="h-12 animate-pulse rounded bg-bg-elevated"></div>
		{/each}
	</div>
{:else if error}
	<div class="text-sm text-error">
		{error}
		<button onclick={load} class="ml-2 underline hover:no-underline">Tentar novamente</button>
	</div>
{:else if events.length === 0}
	<p class="text-sm text-text-muted">Nenhum evento registrado.</p>
{:else}
	<div class="space-y-4">
		{#each visibleEvents as event (event.id)}
			<div class="flex gap-3 text-sm">
				<div class="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-accent"></div>
				<div class="flex-1">
					<div class="flex items-baseline gap-2">
						<span class="font-medium text-text">{event.event_type}</span>
						<span class="text-xs text-text-muted">{formatDate(event.occurred_at)}</span>
					</div>
					<p class="mt-0.5 text-text-muted">{event.description}</p>
					{#if event.duration_minutes}
						<p class="mt-0.5 text-xs text-text-muted">Duração: {event.duration_minutes} min</p>
					{/if}
				</div>
			</div>
		{/each}

		{#if total > 10}
			<button onclick={() => (expanded = !expanded)} class="text-sm text-accent hover:underline">
				{expanded ? '▲ Ocultar' : `▼ Ver todos (${total})`}
			</button>
		{/if}
	</div>
{/if}
