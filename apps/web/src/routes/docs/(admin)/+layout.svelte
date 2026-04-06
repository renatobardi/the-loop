<script lang="ts">
	import type { Snippet } from 'svelte';
	import { goto } from '$app/navigation';
	import { profile } from '$lib/stores/profile';

	let { children }: { children: Snippet } = $props();

	// Same pattern as routes/admin/+layout.svelte: gate only on $profile.
	// $profile === null means either loading or not authenticated — show loading state.
	// $profile !== null && !is_admin means authenticated non-admin — redirect.
	// Never check $user directly: the auth store starts at null before onAuthStateChanged
	// fires, so a $user === null check would redirect authenticated users on every page load.
	$effect(() => {
		if ($profile !== null && !$profile?.is_admin) {
			goto('/docs/');
		}
	});
</script>

{#if $profile?.is_admin}
	{@render children()}
{:else}
	<!-- Profile loading or unauthenticated — prevent flash of admin content -->
	<div class="flex items-center justify-center min-h-[calc(100vh-3.5rem)]">
		<div class="text-text-muted text-sm">Loading…</div>
	</div>
{/if}
