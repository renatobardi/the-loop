<script lang="ts">
	import type { Snippet } from 'svelte';
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores/auth';
	import { profile } from '$lib/stores/profile';

	let { children }: { children: Snippet } = $props();

	// Mirrors the pattern used in routes/admin/+layout.svelte.
	// Wait for auth to resolve before deciding to redirect or render.
	$effect(() => {
		// $user === null means Firebase has resolved with no authenticated user.
		// The auth store starts at null and stays null until onAuthStateChanged fires.
		// We use $profile to distinguish "loading" from "resolved non-admin":
		// - $profile === null + $user !== null → still loading profile
		// - $profile !== null + !$profile.is_admin → non-admin authenticated user
		if ($user === null) {
			goto('/login/');
			return;
		}
		if ($profile !== null && !$profile?.is_admin) {
			goto('/docs/');
		}
	});
</script>

{#if $user !== null && $profile?.is_admin}
	{@render children()}
{:else if $user !== null && $profile === null}
	<!-- Authenticated but profile not yet loaded — show loading state to prevent flash -->
	<div class="flex items-center justify-center min-h-[calc(100vh-3.5rem)]">
		<div class="text-text-muted text-sm">Loading…</div>
	</div>
{/if}
