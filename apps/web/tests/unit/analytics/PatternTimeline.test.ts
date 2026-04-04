import { describe, it, expect } from 'vitest';

// PatternTimeline uses formatCategory from utils (tested in CategoryHeatmap.test.ts)
// and relies on TimelinePoint's by_category having all 5 RootCauseCategory keys.
// These tests verify the data contract and the type shapes.
import type { TimelinePoint, RootCauseCategory } from '$lib/types/analytics';

const ALL_CATEGORIES: RootCauseCategory[] = [
	'code_pattern',
	'infrastructure',
	'process_breakdown',
	'third_party',
	'unknown'
];

function makePoint(week: string, count: number): TimelinePoint {
	return {
		week,
		count,
		by_category: Object.fromEntries(ALL_CATEGORIES.map((c) => [c, 0])) as Record<
			RootCauseCategory,
			number
		>
	};
}

describe('PatternTimeline — data contract (T110)', () => {
	it('by_category always contains all 5 RootCauseCategory keys', () => {
		const point = makePoint('2026-01-05', 4);
		for (const cat of ALL_CATEGORIES) {
			expect(cat in point.by_category).toBe(true);
		}
	});

	it('week is an ISO date string (YYYY-MM-DD)', () => {
		const point = makePoint('2026-01-05', 4);
		expect(point.week).toMatch(/^\d{4}-\d{2}-\d{2}$/);
	});

	it('count matches sum of by_category values when all categories are populated', () => {
		const point: TimelinePoint = {
			week: '2026-01-12',
			count: 6,
			by_category: {
				code_pattern: 2,
				infrastructure: 1,
				process_breakdown: 1,
				third_party: 1,
				unknown: 1
			}
		};
		const sum = Object.values(point.by_category).reduce((a, b) => a + b, 0);
		expect(sum).toBe(point.count);
	});

	it('RootCauseCategory type covers exactly 5 values', () => {
		expect(ALL_CATEGORIES).toHaveLength(5);
	});
});
