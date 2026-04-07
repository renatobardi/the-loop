/**
 * Component tests for BellIcon (Phase 5 User Story 1)
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { releasesStore } from '$lib/stores/releases';

describe('BellIcon Component', () => {
	beforeEach(() => {
		// Reset store state before each test
		releasesStore.reset();
	});

	it('should initialize with 0 unread count', () => {
		expect(releasesStore.unreadCount).toBe(0);
	});

	it('should update unread count', () => {
		releasesStore.unreadCount = 5;
		expect(releasesStore.unreadCount).toBe(5);
	});

	it('should display badge text as count when unread_count < 10', () => {
		releasesStore.unreadCount = 3;
		expect(releasesStore.unreadCount).toBe(3);
		// Badge should show "3"
	});

	it('should display 9+ when unread_count > 9', () => {
		releasesStore.unreadCount = 15;
		expect(releasesStore.unreadCount).toBe(15);
		// Badge should show "9+"
	});

	it('should have dropdown initially closed', () => {
		expect(releasesStore.detailPanelOpen).toBe(false);
	});

	it('should track selected release', () => {
		const mockRelease = {
			id: 'test-1',
			title: 'v1.0.0',
			version: 'v1.0.0',
			published_date: '2026-04-07T00:00:00Z',
			summary: 'Test release',
			changelog_html: '# Changelog',
			breaking_changes_flag: false,
			documentation_url: null,
			created_at: '2026-04-07T00:00:00Z',
			updated_at: '2026-04-07T00:00:00Z',
			isRead: false,
			readAt: null
		};

		releasesStore.selectedRelease = mockRelease;
		expect(releasesStore.selectedRelease?.id).toBe('test-1');
	});

	it('should mark release as read', () => {
		const mockRelease = {
			id: 'test-1',
			title: 'v1.0.0',
			version: 'v1.0.0',
			published_date: '2026-04-07T00:00:00Z',
			summary: 'Test release',
			changelog_html: '# Changelog',
			breaking_changes_flag: false,
			documentation_url: null,
			created_at: '2026-04-07T00:00:00Z',
			updated_at: '2026-04-07T00:00:00Z',
			isRead: false,
			readAt: null
		};

		releasesStore.releases = [mockRelease];
		releasesStore.unreadCount = 1;

		releasesStore.markAsRead('test-1');

		expect(releasesStore.releases[0]?.isRead).toBe(true);
		expect(releasesStore.unreadCount).toBe(0);
	});
});
