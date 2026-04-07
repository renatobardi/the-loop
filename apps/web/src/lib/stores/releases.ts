/**
 * Svelte 5 runes store for release notifications state
 * Manages: unread count, releases list, detail panel state, loading/error states
 */

import type { Release } from '$lib/types/releases';

interface ReleaseItem extends Release {
	isRead: boolean;
	readAt: string | null;
}

class ReleasesStore {
	unreadCount = $state(0);
	releases = $state<ReleaseItem[]>([]);
	selectedRelease = $state<ReleaseItem | null>(null);
	detailPanelOpen = $state(false);
	loading = $state(false);
	error = $state<string | null>(null);

	markAsRead(releaseId: string) {
		this.releases = this.releases.map((r) =>
			r.id === releaseId ? { ...r, isRead: true, readAt: new Date().toISOString() } : r
		);
		this.unreadCount = Math.max(0, this.unreadCount - 1);
	}

	reset() {
		this.unreadCount = 0;
		this.releases = [];
		this.selectedRelease = null;
		this.detailPanelOpen = false;
		this.loading = false;
		this.error = null;
	}
}

export const releasesStore = new ReleasesStore();
