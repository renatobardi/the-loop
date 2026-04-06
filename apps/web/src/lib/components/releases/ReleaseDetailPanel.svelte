<script lang="ts">
	import { markAsRead } from '$lib/services/releases';
	import { releasesStore } from '$lib/stores/releases';

	let { release = $state(null) } = $props();
	let isMarking = $state(false);

	// Auto-mark as read on mount
	$effect(async () => {
		if (release && !release.isRead) {
			try {
				isMarking = true;
				await markAsRead(release.id);
				releasesStore.markAsRead(release.id);
			} catch (error) {
				console.error('Failed to auto-mark as read:', error);
			} finally {
				isMarking = false;
			}
		}
	});

	function closePanel() {
		releasesStore.detailPanelOpen = false;
		releasesStore.selectedRelease = null;
	}

	function formatDate(dateStr: string) {
		const date = new Date(dateStr);
		return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
	}
</script>

<svelte:window onkeydown={(e) => e.key === 'Escape' && closePanel()} />

{#if releasesStore.detailPanelOpen && release}
	<!-- Overlay -->
	<div
		class="fixed inset-0 bg-black/20 z-40"
		onclick={closePanel}
		aria-hidden="true"
	></div>

	<!-- Side Panel -->
	<div
		class="fixed right-0 top-0 h-screen w-full max-w-2xl bg-bg-surface shadow-xl z-50 flex flex-col"
		role="dialog"
		aria-label="Release details"
	>
		<!-- Header -->
		<div class="flex items-center justify-between p-6 border-b border-border/50">
			<div class="flex-1">
				<h2 class="text-2xl font-bold text-text">{release.title}</h2>
				<p class="text-sm text-text-muted mt-1">Version {release.version}</p>
				<p class="text-xs text-text-muted mt-1">{formatDate(release.published_date)}</p>
			</div>
			<button
				onclick={closePanel}
				aria-label="Close panel"
				class="p-2 text-text-muted hover:text-text transition-colors"
			>
				<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		</div>

		<!-- Content -->
		<div class="flex-1 overflow-y-auto p-6">
			{#if release.breaking_changes_flag}
				<div class="mb-4 p-3 bg-error/10 border border-error/30 rounded-lg">
					<p class="text-sm font-semibold text-error">⚠️ Breaking Changes</p>
					<p class="text-xs text-error/80 mt-1">This release contains breaking changes. Please review carefully.</p>
				</div>
			{/if}

			{#if release.summary}
				<div class="mb-6">
					<h3 class="text-sm font-semibold text-text mb-2">Summary</h3>
					<p class="text-sm text-text-muted">{release.summary}</p>
				</div>
			{/if}

			{#if release.changelog_html}
				<div class="mb-6">
					<h3 class="text-sm font-semibold text-text mb-3">Changelog</h3>
					<div class="prose prose-sm text-text-muted space-y-4">
						{@html release.changelog_html}
					</div>
				</div>
			{:else}
				<p class="text-sm text-text-muted">No changelog details available.</p>
			{/if}

			{#if release.documentation_url}
				<div class="mt-6">
					<a
						href={release.documentation_url}
						target="_blank"
						rel="noopener noreferrer"
						class="inline-flex items-center gap-2 text-accent hover:text-accent/80 text-sm font-medium"
					>
						View Full Documentation
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
						</svg>
					</a>
				</div>
			{/if}
		</div>

		<!-- Footer -->
		<div class="border-t border-border/50 p-6 bg-bg-elevated">
			<button
				onclick={closePanel}
				class="w-full px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors text-sm font-medium"
			>
				Close
			</button>
		</div>
	</div>
{/if}

<style>
	:global(.prose) {
		all: revert;
	}

	:global(.prose h1, .prose h2, .prose h3, .prose h4, .prose h5, .prose h6) {
		@apply font-semibold text-text mt-4 mb-2;
	}

	:global(.prose p) {
		@apply text-sm text-text-muted mb-2;
	}

	:global(.prose ul, .prose ol) {
		@apply ml-4 mb-2;
	}

	:global(.prose li) {
		@apply text-sm text-text-muted mb-1;
	}

	:global(.prose code) {
		@apply bg-bg-elevated px-1 py-0.5 rounded text-xs font-mono;
	}

	:global(.prose pre) {
		@apply bg-bg-elevated p-3 rounded overflow-x-auto mb-2;
	}

	:global(.prose pre code) {
		@apply bg-transparent px-0 py-0;
	}
</style>
