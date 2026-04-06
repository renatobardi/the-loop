<script lang="ts">
	import { page } from '$app/state';
	import type { NavItem } from './nav';

	let { items }: { items: NavItem[] } = $props();

	function isActive(slug: string): boolean {
		return page.url.pathname === `/docs/${slug}/`;
	}

	function isHome(): boolean {
		return page.url.pathname === '/docs/';
	}
</script>

<nav aria-label="Documentation" class="p-4">
	<a
		href="/docs/"
		aria-current={isHome() ? 'page' : undefined}
		class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors mb-1
			{isHome()
			? 'bg-accent/10 text-accent font-medium'
			: 'text-text-muted hover:text-text hover:bg-bg-elevated'}"
	>
		<span aria-hidden="true">📖</span>
		Home
	</a>

	<div class="mt-4 mb-2 px-3">
		<span class="text-xs font-semibold uppercase tracking-widest text-text-subtle">Sections</span>
	</div>

	{#each items as item (item.slug)}
		<a
			href="/docs/{item.slug}/"
			aria-current={isActive(item.slug) ? 'page' : undefined}
			class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors mb-1
				{isActive(item.slug)
				? 'bg-accent/10 text-accent font-medium'
				: 'text-text-muted hover:text-text hover:bg-bg-elevated'}"
		>
			<span aria-hidden="true">{item.icon}</span>
			{item.label}
		</a>
	{/each}
</nav>
