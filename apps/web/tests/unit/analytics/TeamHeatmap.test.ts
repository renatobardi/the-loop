import { describe, it, expect } from 'vitest';
import { sortTeamsByCount } from '$lib/utils/analytics';
import type { TeamStats } from '$lib/types/analytics';

const teams: TeamStats[] = [
	{ team: 'frontend', count: 3, top_categories: [], avg_resolution_days: null },
	{ team: 'backend', count: 12, top_categories: [], avg_resolution_days: 2.0 },
	{ team: 'platform', count: 7, top_categories: [], avg_resolution_days: 1.5 }
];

describe('sortTeamsByCount (TeamHeatmap sort logic — T109)', () => {
	it('sorts descending by default (highest count first)', () => {
		const result = sortTeamsByCount(teams, false);
		expect(result.map((t) => t.team)).toEqual(['backend', 'platform', 'frontend']);
	});

	it('sorts ascending when asc=true (lowest count first)', () => {
		const result = sortTeamsByCount(teams, true);
		expect(result.map((t) => t.team)).toEqual(['frontend', 'platform', 'backend']);
	});

	it('does not mutate the original array', () => {
		const original = [...teams];
		sortTeamsByCount(teams, true);
		expect(teams).toEqual(original);
	});

	it('handles empty array', () => {
		expect(sortTeamsByCount([], false)).toEqual([]);
	});

	it('handles single-item array', () => {
		const single = [teams[0]];
		expect(sortTeamsByCount(single, false)).toEqual(single);
	});
});
