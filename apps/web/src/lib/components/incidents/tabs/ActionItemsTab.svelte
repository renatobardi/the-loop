<script lang="ts">
	import { listActionItems, updateActionItemStatus } from '$lib/services/incidents';
	import type { ActionItem } from '$lib/types/action_item';

	let { incidentId, active }: { incidentId: string; active: boolean } = $props();

	let items = $state<ActionItem[]>([]);
	let total = $state(0);
	let loading = $state(false);
	let error = $state('');
	let loaded = $state(false);
	let expanded = $state(false);
	let updatingIds = $state<Set<string>>(new Set());

	$effect(() => {
		if (active && !loaded) {
			load();
		}
	});

	async function load() {
		loading = true;
		error = '';
		try {
			const result = await listActionItems(incidentId);
			items = result.items;
			total = result.total;
			loaded = true;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error loading action items';
		} finally {
			loading = false;
		}
	}

	async function toggleStatus(item: ActionItem) {
		if (item.status === 'completed' || updatingIds.has(item.id)) return;
		updatingIds = new Set([...updatingIds, item.id]);
		try {
			await updateActionItemStatus(incidentId, item.id, 'completed');
			// Pessimistic update: only update after server confirms
			items = items.map((i) => (i.id === item.id ? { ...i, status: 'completed' } : i));
		} catch {
			// Revert: no change to items since we didn't update optimistically
		} finally {
			updatingIds = new Set([...updatingIds].filter((id) => id !== item.id));
		}
	}

	let visibleItems = $derived(expanded ? items : items.slice(0, 10));

	function isOverdue(dateStr: string | null): boolean {
		if (!dateStr) return false;
		return new Date(dateStr) < new Date();
	}

	const priorityClass: Record<string, string> = {
		critical: 'bg-error/20 text-error',
		high: 'bg-accent/20 text-accent',
		medium: 'bg-accent/20 text-accent',
		low: 'bg-bg-elevated text-text-muted'
	};

	const statusClass: Record<string, string> = {
		open: 'text-text-muted',
		in_progress: 'text-accent',
		completed: 'text-accent',
		cancelled: 'text-text-muted'
	};
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
		<button onclick={load} class="ml-2 underline hover:no-underline">Retry</button>
	</div>
{:else if items.length === 0}
	<p class="text-sm text-text-muted">No action items recorded.</p>
{:else}
	<div class="space-y-2">
		{#each visibleItems as item (item.id)}
			<div class="flex items-start gap-3 rounded border border-border bg-bg-surface p-3 text-sm">
				<button
					onclick={() => toggleStatus(item)}
					disabled={item.status === 'completed' || updatingIds.has(item.id)}
					class="mt-0.5 h-4 w-4 shrink-0 rounded border border-border text-accent disabled:cursor-default"
					aria-label="Mark as completed"
				>
					{#if item.status === 'completed'}✓{/if}
				</button>
				<div class="flex-1">
					<div class="flex flex-wrap items-center gap-2">
						<span
							class="font-medium text-text {item.status === 'completed'
								? 'line-through text-text-muted'
								: ''}">{item.title}</span
						>
						<span
							class="rounded px-1.5 py-0.5 text-xs {priorityClass[item.priority] ??
								'bg-bg-elevated text-text-muted'}">{item.priority.toUpperCase()}</span
						>
						<span class="text-xs {statusClass[item.status] ?? 'text-text-muted'}"
							>{item.status}</span
						>
					</div>
					{#if item.due_date}
						<p
							class="mt-0.5 text-xs {isOverdue(item.due_date) && item.status !== 'completed'
								? 'text-error'
								: 'text-text-muted'}"
						>
							Due: {new Date(item.due_date).toLocaleDateString()}
						</p>
					{/if}
				</div>
			</div>
		{/each}

		{#if total > 10}
			<button onclick={() => (expanded = !expanded)} class="text-sm text-accent hover:underline">
				{expanded ? '▲ Hide' : `▼ Show all (${total})`}
			</button>
		{/if}
	</div>
{/if}
