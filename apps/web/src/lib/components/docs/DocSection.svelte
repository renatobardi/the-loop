<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		title,
		id,
		children
	}: {
		title: string;
		id: string;
		children: Snippet;
	} = $props();
</script>

<section {id} class="mb-10">
	<h2 class="text-xl font-semibold text-text mb-4 scroll-mt-20">{title}</h2>
	<div class="space-y-3">
		{@render children()}
	</div>
</section>
