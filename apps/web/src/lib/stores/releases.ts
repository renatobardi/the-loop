/**
 * Svelte store for release notifications state
 * Manages: unread count, releases list, detail panel state, loading/error states
 */

import { writable } from 'svelte/store';
import type { Release } from '$lib/types/releases';

export interface ReleaseItem extends Release {
	isRead: boolean;
	readAt: string | null;
}

interface ReleaseStoreState {
	unreadCount: number;
	releases: ReleaseItem[];
	selectedRelease: ReleaseItem | null;
	detailPanelOpen: boolean;
	loading: boolean;
	error: string | null;
}

class ReleasesStore {
	private store = writable<ReleaseStoreState>({
		unreadCount: 0,
		releases: [],
		selectedRelease: null,
		detailPanelOpen: false,
		loading: false,
		error: null
	});

	// Expose store for subscriptions if needed
	subscribe = this.store.subscribe;

	// Expose state as getters
	get unreadCount(): number {
		let value = 0;
		this.store.subscribe((state) => {
			value = state.unreadCount;
		})();
		return value;
	}

	set unreadCount(value: number) {
		this.store.update((state) => ({ ...state, unreadCount: value }));
	}

	get releases(): ReleaseItem[] {
		let value: ReleaseItem[] = [];
		this.store.subscribe((state) => {
			value = state.releases;
		})();
		return value;
	}

	set releases(value: ReleaseItem[]) {
		this.store.update((state) => ({ ...state, releases: value }));
	}

	get selectedRelease(): ReleaseItem | null {
		let value: ReleaseItem | null = null;
		this.store.subscribe((state) => {
			value = state.selectedRelease;
		})();
		return value;
	}

	set selectedRelease(value: ReleaseItem | null) {
		this.store.update((state) => ({ ...state, selectedRelease: value }));
	}

	get detailPanelOpen(): boolean {
		let value = false;
		this.store.subscribe((state) => {
			value = state.detailPanelOpen;
		})();
		return value;
	}

	set detailPanelOpen(value: boolean) {
		this.store.update((state) => ({ ...state, detailPanelOpen: value }));
	}

	get loading(): boolean {
		let value = false;
		this.store.subscribe((state) => {
			value = state.loading;
		})();
		return value;
	}

	set loading(value: boolean) {
		this.store.update((state) => ({ ...state, loading: value }));
	}

	get error(): string | null {
		let value: string | null = null;
		this.store.subscribe((state) => {
			value = state.error;
		})();
		return value;
	}

	set error(value: string | null) {
		this.store.update((state) => ({ ...state, error: value }));
	}

	markAsRead(releaseId: string) {
		this.store.update((state) => ({
			...state,
			releases: state.releases.map((r) =>
				r.id === releaseId ? { ...r, isRead: true, readAt: new Date().toISOString() } : r
			),
			unreadCount: Math.max(0, state.unreadCount - 1)
		}));
	}

	reset() {
		this.store.set({
			unreadCount: 0,
			releases: [],
			selectedRelease: null,
			detailPanelOpen: false,
			loading: false,
			error: null
		});
	}
}

export const releasesStore = new ReleasesStore();
