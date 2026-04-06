/**
 * Component tests for BellIcon (Phase 5 User Story 1)
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import BellIcon from '$lib/components/releases/BellIcon.svelte';
import { releasesStore } from '$lib/stores/releases';

// Mock the services
vi.mock('$lib/services/releases', () => ({
	fetchUnreadCount: vi.fn(async () => 0)
}));

describe('BellIcon Component', () => {
	beforeEach(() => {
		// Reset store state before each test
		releasesStore.reset();
		vi.clearAllMocks();
	});

	it('should render bell icon button', () => {
		render(BellIcon);
		const button = screen.getByRole('button', { name: /release notifications/i });
		expect(button).toBeInTheDocument();
	});

	it('should display badge when unread_count > 0', async () => {
		render(BellIcon);
		releasesStore.unreadCount = 3;

		const badge = screen.getByText('3');
		expect(badge).toBeInTheDocument();
		expect(badge).toHaveClass('bg-error');
	});

	it('should not display badge when unread_count = 0', () => {
		render(BellIcon);
		releasesStore.unreadCount = 0;

		// Should not have any badge text
		expect(screen.queryByText(/\d+/)).not.toBeInTheDocument();
	});

	it('should display 9+ when unread_count > 9', () => {
		render(BellIcon);
		releasesStore.unreadCount = 15;

		const badge = screen.getByText('9+');
		expect(badge).toBeInTheDocument();
	});

	it('should toggle dropdown on bell icon click', async () => {
		render(BellIcon);
		const button = screen.getByRole('button', { name: /release notifications/i });

		// Initially dropdown should not be visible
		expect(button).toHaveAttribute('aria-expanded', 'false');

		// Click to open
		await fireEvent.click(button);
		expect(button).toHaveAttribute('aria-expanded', 'true');

		// Click to close
		await fireEvent.click(button);
		expect(button).toHaveAttribute('aria-expanded', 'false');
	});

	it('should have correct aria-label for accessibility', () => {
		render(BellIcon);
		const button = screen.getByRole('button', { name: /release notifications/i });
		expect(button).toHaveAttribute('aria-label', 'Product release notifications');
	});

	it('should have correct badge aria-label with count', () => {
		render(BellIcon);
		releasesStore.unreadCount = 5;

		const badge = screen.getByLabelText('5 unread releases');
		expect(badge).toBeInTheDocument();
	});
});
