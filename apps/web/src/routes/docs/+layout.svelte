<script lang="ts">
	import type { Snippet } from 'svelte';
	import { profile } from '$lib/stores/profile';
	import { USER_SECTIONS, ADMIN_SECTIONS } from '$lib/components/docs/nav';
	import DocSidebar from '$lib/components/docs/DocSidebar.svelte';

	let { children }: { children: Snippet } = $props();

	let navItems = $derived(
		$profile?.is_admin ? [...USER_SECTIONS, ...ADMIN_SECTIONS] : USER_SECTIONS
	);
</script>

<div class="flex min-h-[calc(100vh-3.5rem)]">
	<!-- Sidebar: sticky, scrollable, hidden on mobile -->
	<aside
		class="hidden md:block w-60 shrink-0 border-r border-border/50 sticky top-14 h-[calc(100vh-3.5rem)] overflow-y-auto"
	>
		<DocSidebar items={navItems} />
	</aside>

	<!-- Main content -->
	<main id="main-content" class="flex-1 min-w-0 px-6 py-8 max-w-3xl">
		{@render children()}
	</main>
</div>
