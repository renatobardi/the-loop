import { describe, it, expect } from 'vitest';
import { formatDays } from '$lib/utils/analytics';

describe('formatDays (SummaryCard display logic)', () => {
	it('formats a positive number with one decimal and "d" suffix', () => {
		expect(formatDays(3.2)).toBe('3.2d');
	});

	it('rounds to one decimal place', () => {
		expect(formatDays(2.56789)).toBe('2.6d');
	});

	it('returns "N/A" when avg_resolution_days is null', () => {
		expect(formatDays(null)).toBe('N/A');
	});

	it('handles zero correctly', () => {
		expect(formatDays(0)).toBe('0.0d');
	});
});
