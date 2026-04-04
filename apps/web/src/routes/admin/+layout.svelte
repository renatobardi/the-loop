<script lang="ts">
	import { profile } from '$lib/stores/profile';
	import { goto } from '$app/navigation';
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();

	$effect(() => {
		// Wait until profile has loaded (null = not loaded yet, undefined would be unset)
		if ($profile !== null && !$profile?.is_admin) {
			goto('/');
		}
	});
</script>

{@render children()}
