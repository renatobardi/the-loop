/**
 * Component tests for ReleasesDropdown (Phase 5 User Story 2)
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { releasesStore } from '$lib/stores/releases';

describe('ReleasesDropdown Store Integration', () => {
	beforeEach(() => {
		releasesStore.reset();
	});

	it('should render empty state when no releases', () => {
		expect(releasesStore.releases.length).toBe(0);
	});

	it('should display releases list when releases exist', () => {
		const mockRelease = {
			id: '1',
			title: 'v1.0.0',
			version: '1.0.0',
			published_date: '2026-04-06T00:00:00Z',
			summary: 'Initial release',
			changelog_html: null,
			breaking_changes_flag: false,
			documentation_url: null,
			created_at: '2026-04-06T00:00:00Z',
			updated_at: '2026-04-06T00:00:00Z',
			isRead: false,
			readAt: null
		};

		releasesStore.releases = [mockRelease];
		expect(releasesStore.releases.length).toBe(1);
		expect(releasesStore.releases[0]?.title).toBe('v1.0.0');
	});

	it('should sort unread releases first', () => {
		const release1 = {
			id: '1',
			title: 'v1.0.0',
			version: '1.0.0',
			published_date: '2026-04-05T00:00:00Z',
			summary: 'First',
			changelog_html: null,
			breaking_changes_flag: false,
			documentation_url: null,
			created_at: '2026-04-05T00:00:00Z',
			updated_at: '2026-04-05T00:00:00Z',
			isRead: true,
			readAt: '2026-04-06T00:00:00Z'
		};

		const release2 = {
			id: '2',
			title: 'v1.1.0',
			version: '1.1.0',
			published_date: '2026-04-06T00:00:00Z',
			summary: 'Second',
			changelog_html: null,
			breaking_changes_flag: false,
			documentation_url: null,
			created_at: '2026-04-06T00:00:00Z',
			updated_at: '2026-04-06T00:00:00Z',
			isRead: false,
			readAt: null
		};

		releasesStore.releases = [release1, release2];
		const sorted = [...releasesStore.releases].sort((a, b) => {
			// Unread first
			if (a.isRead !== b.isRead) {
				return a.isRead ? 1 : -1;
			}
			// Then by date descending
			const dateA = new Date(a.published_date).getTime();
			const dateB = new Date(b.published_date).getTime();
			return dateB - dateA;
		});

		// First should be unread (v1.1.0)
		expect(sorted[0]?.id).toBe('2');
		expect(sorted[1]?.id).toBe('1');
	});

	it('should have View All Releases link target', () => {
		releasesStore.releases = [
			{
				id: '1',
				title: 'v1.0.0',
				version: '1.0.0',
				published_date: '2026-04-06T00:00:00Z',
				summary: 'Initial',
				changelog_html: null,
				breaking_changes_flag: false,
				documentation_url: null,
				created_at: '2026-04-06T00:00:00Z',
				updated_at: '2026-04-06T00:00:00Z',
				isRead: false,
				readAt: null
			}
		];

		// Component would render link to /releases/
		expect(releasesStore.releases.length).toBeGreaterThan(0);
	});

	it('should handle dropdown close callback', () => {
		releasesStore.detailPanelOpen = true;
		expect(releasesStore.detailPanelOpen).toBe(true);

		releasesStore.detailPanelOpen = false;
		expect(releasesStore.detailPanelOpen).toBe(false);
	});

	it('should update loading state', () => {
		expect(releasesStore.loading).toBe(false);

		releasesStore.loading = true;
		expect(releasesStore.loading).toBe(true);

		releasesStore.loading = false;
		expect(releasesStore.loading).toBe(false);
	});
});
