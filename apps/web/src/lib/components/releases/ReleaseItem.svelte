<script lang="ts">
	import { markAsRead } from '$lib/services/releases';
	import { releasesStore } from '$lib/stores/releases';

	let { release } = $props();
	let isMarking = $state(false);

	async function handleMarkAsRead(e: Event) {
		e.preventDefault();
		e.stopPropagation();

		if (release.isRead) return;

		try {
			isMarking = true;
			await markAsRead(release.id);
			releasesStore.markAsRead(release.id);
		} catch (error) {
			console.error('Failed to mark as read:', error);
			releasesStore.error = error instanceof Error ? error.message : 'Failed to mark as read';
		} finally {
			isMarking = false;
		}
	}

	function formatDate(dateStr: string) {
		const date = new Date(dateStr);
		return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
	}
</script>

<div class={`px-4 py-3 border-b border-border/30 last:border-b-0 ${release.isRead ? 'opacity-75' : ''}`}>
	<div class="flex items-start justify-between gap-2">
		<div class="flex-1">
			<div class="font-semibold text-sm flex items-center gap-2">
				<span class={release.isRead ? 'text-text-muted' : 'text-text'}>
					{release.title}
				</span>
				{#if !release.isRead}
					<span
						class="inline-block w-2 h-2 bg-accent rounded-full"
						aria-label="Unread"
					></span>
				{/if}
			</div>
			<p class="text-xs text-text-muted mt-1">{formatDate(release.published_date)}</p>
			{#if release.summary}
				<p class="text-xs text-text-muted mt-2 line-clamp-2">{release.summary}</p>
			{/if}
			{#if release.breaking_changes_flag}
				<span class="inline-block mt-2 px-2 py-1 bg-error/20 text-error text-xs font-medium rounded">
					Breaking Changes
				</span>
			{/if}
		</div>

		{#if !release.isRead}
			<button
				onclick={handleMarkAsRead}
				disabled={isMarking}
				class="px-2 py-1 text-xs bg-accent/10 text-accent hover:bg-accent/20 rounded transition-colors disabled:opacity-50"
				aria-label={`Mark ${release.title} as read`}
			>
				{isMarking ? '...' : 'Mark read'}
			</button>
		{/if}
	</div>
</div>
