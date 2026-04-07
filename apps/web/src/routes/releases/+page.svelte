<script lang="ts">
	import DOMPurify from 'dompurify';
	import { Container, Section } from '$lib/ui';
	import { fetchReleases } from '$lib/services/releases';
	import type { ReleasesListResponse } from '$lib/types/releases';

	let releases: ReleasesListResponse | null = $state(null);
	let loading = $state(true);
	let error: string | null = $state(null);

	async function loadReleases() {
		try {
			loading = true;
			releases = await fetchReleases();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load releases';
		} finally {
			loading = false;
		}
	}

	// Load on mount
	$effect.pre(() => {
		loadReleases();
	});

	function formatDate(dateStr: string) {
		const date = new Date(dateStr);
		return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
	}

	function sanitizeHtml(html: string): string {
		return DOMPurify.sanitize(html, {
			ALLOWED_TAGS: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'strong', 'em', 'u', 'code', 'pre', 'ul', 'ol', 'li', 'a', 'br', 'blockquote']
		});
	}
</script>

<Container>
	<Section>
		<div class="py-12">
			<h1 class="text-4xl font-bold text-text mb-4">Product Releases</h1>
			<p class="text-lg text-text-muted mb-8">Latest updates and improvements to The Loop</p>

			{#if loading}
				<div class="text-center py-12">
					<p class="text-text-muted">Loading releases...</p>
				</div>
			{:else if error}
				<div class="rounded-lg border border-error/40 bg-error/10 px-6 py-5 mb-8">
					<p class="font-medium text-error">Failed to load releases</p>
					<p class="mt-1 text-sm text-error/80">{error}</p>
					<button
						onclick={loadReleases}
						class="mt-3 rounded border border-error/40 px-3 py-1.5 text-sm text-error hover:bg-error/10 focus:outline-none focus:ring-2 focus:ring-error"
					>
						Retry
					</button>
				</div>
			{:else if releases && releases.items.length > 0}
				<div class="space-y-6">
					{#each releases.items as item (item.release.id)}
						<article class="rounded-lg border border-border/50 bg-bg-elevated p-6">
							<div class="flex items-start justify-between gap-4">
								<div class="flex-1">
									<h2 class="text-2xl font-bold text-text">{item.release.title}</h2>
									<div class="flex items-center gap-4 mt-2">
										<span class="text-sm text-text-muted">v{item.release.version}</span>
										<span class="text-sm text-text-muted">
											{formatDate(item.release.published_date)}
										</span>
										{#if item.release.breaking_changes_flag}
											<span class="inline-block px-2 py-1 bg-error/20 text-error text-xs font-medium rounded">
												Breaking Changes
											</span>
										{/if}
									</div>

									{#if item.release.summary}
										<p class="text-text-muted mt-4">{item.release.summary}</p>
									{/if}

									{#if item.release.changelog_html}
										<div class="mt-4 prose prose-sm text-text-muted">
											<!-- eslint-disable-next-line svelte/no-at-html-tags -->
											{@html sanitizeHtml(item.release.changelog_html)}
										</div>
									{/if}

									{#if item.release.documentation_url}
										<a
											href={item.release.documentation_url}
											target="_blank"
											rel="noopener noreferrer"
											class="inline-flex items-center gap-2 mt-4 text-accent hover:text-accent/80 text-sm font-medium"
										>
											View on GitHub
											<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
												/>
											</svg>
										</a>
									{/if}
								</div>
							</div>
						</article>
					{/each}
				</div>
			{:else}
				<div class="text-center py-12">
					<p class="text-text-muted">No releases available yet</p>
				</div>
			{/if}
		</div>
	</Section>
</Container>

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
</style>
