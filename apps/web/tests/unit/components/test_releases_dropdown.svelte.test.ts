/**
 * Component tests for ReleasesDropdown (Phase 5 User Story 2)
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import ReleasesDropdown from '$lib/components/releases/ReleasesDropdown.svelte';
import { releasesStore } from '$lib/stores/releases';

describe('ReleasesDropdown Component', () => {
	beforeEach(() => {
		releasesStore.reset();
		vi.clearAllMocks();
	});

	it('should render empty state when no releases', () => {
		render(ReleasesDropdown, { props: { open: true, onClose: () => {} } });
		expect(screen.getByText(/no releases/i)).toBeInTheDocument();
	});

	it('should display releases list when open and releases exist', () => {
		const mockRelease = {
			id: '1',
			title: 'v1.0.0',
			version: '1.0.0',
			published_date: '2026-04-06T00:00:00Z',
			summary: 'Initial release',
			changelog_html: null,
			breaking_changes_flag: false,
			documentation_url: null,
			isRead: false,
			readAt: null
		};

		releasesStore.releases = [mockRelease];
		render(ReleasesDropdown, { props: { open: true, onClose: () => {} } });

		expect(screen.getByText('v1.0.0')).toBeInTheDocument();
		expect(screen.getByText('Initial release')).toBeInTheDocument();
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
			isRead: false,
			readAt: null
		};

		releasesStore.releases = [release1, release2];
		render(ReleasesDropdown, { props: { open: true, onClose: () => {} } });

		const titles = screen.getAllByText(/v\d+\.\d+\.\d+/);
		// First should be unread (v1.1.0)
		expect(titles[0]).toHaveTextContent('v1.1.0');
		expect(titles[1]).toHaveTextContent('v1.0.0');
	});

	it('should render "View All Releases" link', () => {
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
				isRead: false,
				readAt: null
			}
		];

		render(ReleasesDropdown, { props: { open: true, onClose: () => {} } });
		const link = screen.getByText(/view all releases/i);
		expect(link).toHaveAttribute('href', '/releases/');
	});

	it('should call onClose when close button clicked', async () => {
		const onClose = vi.fn();
		render(ReleasesDropdown, { props: { open: true, onClose } });

		const closeBtn = screen.getByRole('button', { name: /close/i });
		await fireEvent.click(closeBtn);

		expect(onClose).toHaveBeenCalled();
	});
});
