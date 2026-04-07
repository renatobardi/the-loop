<script lang="ts">
	import DOMPurify from 'dompurify';
	import { markAsRead } from '$lib/services/releases';
	import { releasesStore } from '$lib/stores/releases';

	let { release = null } = $props();

	function sanitizeHtml(html: string): string {
		return DOMPurify.sanitize(html, {
			ALLOWED_TAGS: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'strong', 'em', 'u', 'code', 'pre', 'ul', 'ol', 'li', 'a', 'br', 'blockquote']
		});
	}

	// Auto-mark as read on mount
	$effect(() => {
		if (release && !release.isRead) {
			(async () => {
				try {
					await markAsRead(release.id);
					releasesStore.markAsRead(release.id);
				} catch (error) {
					console.error('Failed to auto-mark as read:', error);
				}
			})();
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
	<div class="fixed inset-0 bg-black/20 z-40" onclick={closePanel} aria-hidden="true"></div>

	<!-- Side Panel -->
	<div class="fixed right-0 top-0 h-screen w-full max-w-2xl bg-bg-surface shadow-xl z-50 flex flex-col" role="dialog" aria-label="Release details">
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
						<!-- eslint-disable-next-line svelte/no-at-html-tags -->
						{@html sanitizeHtml(release.changelog_html)}
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
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
							/>
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
		font-weight: 600;
		color: var(--color-text);
		margin-top: 1rem;
		margin-bottom: 0.5rem;
	}

	:global(.prose p) {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		margin-bottom: 0.5rem;
	}

	:global(.prose ul, .prose ol) {
		margin-left: 1rem;
		margin-bottom: 0.5rem;
	}

	:global(.prose li) {
		margin-bottom: 0.25rem;
	}

	:global(.prose code) {
		background-color: var(--color-bg);
		padding: 0.125rem 0.375rem;
		border-radius: 0.25rem;
		font-family: monospace;
	}

	:global(.prose pre) {
		background-color: var(--color-bg);
		padding: 1rem;
		border-radius: 0.5rem;
		overflow-x: auto;
		margin: 1rem 0;
	}

	:global(.prose a) {
		color: var(--color-accent);
		text-decoration: underline;
	}

	:global(.prose blockquote) {
		border-left: 0.25rem solid var(--color-border);
		padding-left: 1rem;
		margin: 1rem 0;
		color: var(--color-text-muted);
		font-style: italic;
	}
</style>
