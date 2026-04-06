<script lang="ts">
	import { onDestroy } from 'svelte';
	import { fetchUnreadCount, fetchReleases } from '$lib/services/releases';
	import { releasesStore } from '$lib/stores/releases';

	let isOpen = $state(false);
	let pollingInterval: ReturnType<typeof setInterval> | null = null;

	// Load unread count on mount
	async function loadUnreadCount() {
		try {
			const count = await fetchUnreadCount();
			releasesStore.unreadCount = count;
		} catch (error) {
			console.error('Failed to load unread count:', error);
			releasesStore.error = error instanceof Error ? error.message : 'Failed to load notifications';
		}
	}

	// Load releases list for dropdown
	async function loadReleases() {
		try {
			releasesStore.loading = true;
			const response = await fetchReleases();
			const releases = response.items.map((item) => ({
				...item.release,
				isRead: item.is_read,
				readAt: item.read_at
			}));
			releasesStore.releases = releases;
			releasesStore.error = null;
		} catch (error) {
			console.error('Failed to load releases:', error);
			releasesStore.error = error instanceof Error ? error.message : 'Failed to load releases';
		} finally {
			releasesStore.loading = false;
		}
	}

	function startPolling() {
		// Poll every 120 seconds (2 minutes)
		pollingInterval = setInterval(async () => {
			await loadUnreadCount();
		}, 120000);
	}

	function stopPolling() {
		if (pollingInterval) {
			clearInterval(pollingInterval);
			pollingInterval = null;
		}
	}

	async function toggleDropdown() {
		isOpen = !isOpen;
		if (isOpen) {
			await loadReleases();
		}
	}

	function closeDropdown() {
		isOpen = false;
	}

	// Load on component mount
	$effect.pre(() => {
		loadUnreadCount();
		startPolling();
	});

	// Cleanup on destroy
	onDestroy(() => {
		stopPolling();
	});
</script>

<script lang="ts">
	import ReleasesDropdown from './ReleasesDropdown.svelte';
	import ReleaseDetailPanel from './ReleaseDetailPanel.svelte';

	function handleClickOutside(event: MouseEvent) {
		const target = event.target as HTMLElement;
		if (!target.closest('.bell-icon-container')) {
			closeDropdown();
		}
	}
</script>

<svelte:window onmousedown={handleClickOutside} />

<div class="relative bell-icon-container">
	<button
		onclick={toggleDropdown}
		aria-label="Product release notifications"
		aria-expanded={isOpen}
		class="relative p-2 text-text hover:text-accent transition-colors"
		title="Release notifications"
	>
		<!-- Bell icon SVG -->
		<svg
			class="w-6 h-6"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
			xmlns="http://www.w3.org/2000/svg"
		>
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
			/>
		</svg>

		<!-- Badge indicator (only visible when unread_count > 0) -->
		{#if releasesStore.unreadCount > 0}
			<span
				class="absolute top-0 right-0 flex items-center justify-center w-5 h-5 bg-error text-white text-xs font-bold rounded-full"
				aria-label={`${releasesStore.unreadCount} unread releases`}
			>
				{releasesStore.unreadCount > 9 ? '9+' : releasesStore.unreadCount}
			</span>
		{/if}
	</button>

	<!-- Dropdown component -->
	<ReleasesDropdown {open} onClose={closeDropdown} />

	<!-- Detail panel component -->
	<ReleaseDetailPanel release={releasesStore.selectedRelease} />
</div>

<style>
	:global(.bell-icon-container) {
		position: relative;
	}
</style>

<style>
	/* Optional: add any component-specific styles here */
</style>
