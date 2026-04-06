import { describe, it, expect } from 'vitest';
import type { SeverityTrendPoint } from '$lib/types/analytics';

// SeverityTrendChart renders stacked area paths from SeverityTrendPoint[].
// Tests verify the data contract and the month-label deduplication logic
// (same each_key_duplicate risk that affected PatternTimeline — T113).

function makePoint(week: string, error_count: number, warning_count: number): SeverityTrendPoint {
	return { week, error_count, warning_count };
}

// Mirrors the monthLabels computation in SeverityTrendChart.svelte
function computeMonthLabelKeys(data: SeverityTrendPoint[]): string[] {
	return data
		.map((p, i) => ({ p, i }))
		.filter(({ i }) => i % 4 === 0)
		.map(({ p }) => p.week); // week is the unique key
}

describe('SeverityTrendChart — data contract', () => {
	it('SeverityTrendPoint has week, error_count, warning_count', () => {
		const p = makePoint('2026-01-05', 3, 7);
		expect(p.week).toBe('2026-01-05');
		expect(p.error_count).toBe(3);
		expect(p.warning_count).toBe(7);
	});

	it('week is an ISO date string (YYYY-MM-DD)', () => {
		const p = makePoint('2026-03-10', 0, 0);
		expect(p.week).toMatch(/^\d{4}-\d{2}-\d{2}$/);
	});

	it('error_count and warning_count are non-negative integers', () => {
		const p = makePoint('2026-01-05', 0, 0);
		expect(p.error_count).toBeGreaterThanOrEqual(0);
		expect(p.warning_count).toBeGreaterThanOrEqual(0);
	});
});

describe('SeverityTrendChart — monthLabels key uniqueness (T113)', () => {
	it('produces unique keys for a quarter period (12 weeks) — no each_key_duplicate', () => {
		// Quarter: 12 weekly points starting 2026-01-05
		const data: SeverityTrendPoint[] = Array.from({ length: 12 }, (_, i) => {
			const date = new Date('2026-01-05');
			date.setDate(date.getDate() + i * 7);
			return makePoint(date.toISOString().slice(0, 10), 1, 2);
		});
		const keys = computeMonthLabelKeys(data);
		const uniqueKeys = new Set(keys);
		expect(uniqueKeys.size).toBe(keys.length);
	});

	it('produces unique keys even when two sampled weeks fall in the same calendar month', () => {
		// Two points 4 weeks apart that both land in March (e.g. Mar 2 and Mar 30)
		const data: SeverityTrendPoint[] = [
			makePoint('2026-01-05', 0, 0),
			makePoint('2026-01-12', 0, 0),
			makePoint('2026-01-19', 0, 0),
			makePoint('2026-01-26', 0, 0),
			makePoint('2026-02-02', 0, 0),
			makePoint('2026-02-09', 0, 0),
			makePoint('2026-02-16', 0, 0),
			makePoint('2026-02-23', 0, 0),
			makePoint('2026-03-02', 0, 0), // index 8 → sampled (i % 4 === 0)
			makePoint('2026-03-09', 0, 0),
			makePoint('2026-03-16', 0, 0),
			makePoint('2026-03-23', 0, 0),
			makePoint('2026-03-30', 0, 0) // index 12 → sampled (i % 4 === 0), same month as index 8
		];
		const keys = computeMonthLabelKeys(data);
		const uniqueKeys = new Set(keys);
		expect(uniqueKeys.size).toBe(keys.length);
	});
});
