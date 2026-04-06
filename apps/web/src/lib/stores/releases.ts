/**
 * Svelte 5 runes store for release notifications state
 * Manages: unread count, releases list, detail panel state, loading/error states
 */

import { $state } from 'svelte';
import type { Release, ReleaseNotificationStatus } from '$lib/types/releases';

interface ReleasesStoreState {
	unreadCount: number;
	releases: (Release & { isRead: boolean; readAt: string | null })[];
	selectedRelease: (Release & { isRead: boolean; readAt: string | null }) | null;
	detailPanelOpen: boolean;
	loading: boolean;
	error: string | null;
}

function createReleasesStore() {
	let state = $state<ReleasesStoreState>({
		unreadCount: 0,
		releases: [],
		selectedRelease: null,
		detailPanelOpen: false,
		loading: false,
		error: null
	});

	return {
		get unreadCount() {
			return state.unreadCount;
		},
		set unreadCount(value: number) {
			state.unreadCount = value;
		},

		get releases() {
			return state.releases;
		},
		set releases(value: (Release & { isRead: boolean; readAt: string | null })[]) {
			state.releases = value;
		},

		get selectedRelease() {
			return state.selectedRelease;
		},
		set selectedRelease(value: (Release & { isRead: boolean; readAt: string | null }) | null) {
			state.selectedRelease = value;
		},

		get detailPanelOpen() {
			return state.detailPanelOpen;
		},
		set detailPanelOpen(value: boolean) {
			state.detailPanelOpen = value;
		},

		get loading() {
			return state.loading;
		},
		set loading(value: boolean) {
			state.loading = value;
		},

		get error() {
			return state.error;
		},
		set error(value: string | null) {
			state.error = value;
		},

		// Update unread count for a specific release
		markAsRead(releaseId: string) {
			state.releases = state.releases.map((r) =>
				r.id === releaseId ? { ...r, isRead: true, readAt: new Date().toISOString() } : r
			);
			state.unreadCount = Math.max(0, state.unreadCount - 1);
		},

		// Clear all state
		reset() {
			state.unreadCount = 0;
			state.releases = [];
			state.selectedRelease = null;
			state.detailPanelOpen = false;
			state.loading = false;
			state.error = null;
		}
	};
}

export const releasesStore = createReleasesStore();
