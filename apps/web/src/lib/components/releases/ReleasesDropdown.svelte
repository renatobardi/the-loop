<script lang="ts">
	import { releasesStore } from '$lib/stores/releases';
	import ReleaseItem from './ReleaseItem.svelte';

	type Props = {
		open: boolean;
		onClose: () => void;
	};

	let { open = false, onClose }: Props = $props();

	// Sort releases: unread first, then by date descending
	const sortedReleases = $derived.by(() => {
		if (!releasesStore.releases) return [];
		return [...releasesStore.releases].sort((a, b) => {
			// Unread first (false < true)
			if (a.isRead !== b.isRead) {
				return a.isRead ? 1 : -1;
			}
			// Then by date descending
			const dateA = new Date(a.published_date).getTime();
			const dateB = new Date(b.published_date).getTime();
			return dateB - dateA;
		});
	});

	function selectRelease(release: any) {
		releasesStore.selectedRelease = release;
		releasesStore.detailPanelOpen = true;
	}
</script>

{#if open}
	<div class="absolute right-0 top-full mt-2 w-80 bg-bg-surface rounded-lg shadow-xl z-50 border border-border">
		<div class="flex items-center justify-between p-4 border-b border-border/50">
			<h3 class="font-semibold text-text">Product Releases</h3>
			<button
				onclick={onClose}
				aria-label="Close"
				class="p-1 text-text-muted hover:text-text transition-colors"
			>
				<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		</div>

		<div class="max-h-96 overflow-y-auto">
			{#if releasesStore.loading}
				<div class="p-4 text-center text-text-muted">Loading releases...</div>
			{:else if sortedReleases.length === 0}
				<div class="p-4 text-center text-text-muted">
					<p class="text-sm">No releases available yet</p>
				</div>
			{:else}
				{#each sortedReleases as release (release.id)}
					<button
						onclick={() => selectRelease(release)}
						class="w-full text-left hover:bg-bg-elevated transition-colors"
					>
						<ReleaseItem {release} />
					</button>
				{/each}
			{/if}
		</div>

		<div class="border-t border-border/50 p-3">
			<a
				href="/releases/"
				class="block text-center text-xs text-accent hover:text-accent/80 font-medium transition-colors py-2"
			>
				View All Releases →
			</a>
		</div>
	</div>
{/if}
