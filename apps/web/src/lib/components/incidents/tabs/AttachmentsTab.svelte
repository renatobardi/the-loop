<script lang="ts">
	import { listAttachments } from '$lib/services/incidents';
	import type { Attachment } from '$lib/types/attachment';

	let { incidentId, active }: { incidentId: string; active: boolean } = $props();

	let attachments = $state<Attachment[]>([]);
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
			const result = await listAttachments(incidentId);
			attachments = result.items;
			total = result.total;
			loaded = true;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error loading attachments';
		} finally {
			loading = false;
		}
	}

	let visibleAttachments = $derived(expanded ? attachments : attachments.slice(0, 10));

	function formatFileSize(bytes: number): string {
		if (bytes < 1024) return `${bytes} B`;
		if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
		return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
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
		<button onclick={load} class="ml-2 underline hover:no-underline">Retry</button>
	</div>
{:else if attachments.length === 0}
	<p class="text-sm text-text-muted">No attachments recorded.</p>
{:else}
	<div class="space-y-2">
		{#each visibleAttachments as attachment (attachment.id)}
			<div class="flex items-start gap-3 rounded border border-border bg-bg-surface p-3 text-sm">
				<span class="text-lg">📎</span>
				<div class="flex-1">
					<div class="flex flex-wrap items-center gap-2">
						{#if attachment.source_url}
							<a
								href={attachment.source_url}
								target="_blank"
								rel="noopener noreferrer"
								class="font-medium text-accent hover:underline"
							>{attachment.filename}</a>
						{:else}
							<span class="font-medium text-text">{attachment.filename}</span>
						{/if}
						<span class="text-xs text-text-muted">{attachment.attachment_type}</span>
						{#if attachment.source_system}
							<span class="text-xs text-text-muted">· {attachment.source_system}</span>
						{/if}
					</div>
					<p class="mt-0.5 text-xs text-text-muted">{formatFileSize(attachment.file_size_bytes)}</p>
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
