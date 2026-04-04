import { describe, it, expect } from 'vitest';
// buildQueryString is the function AnalyticsFilters drives indirectly via the page.
// Testing it directly verifies the URL param update logic (T112).
import { buildQueryString } from '$lib/services/analytics';
import type { AnalyticsFilter } from '$lib/types/analytics';

const base: AnalyticsFilter = { period: 'month', team: null, category: null, status: 'all' };

describe('buildQueryString — URL param update logic (T112)', () => {
	it('always includes period and status', () => {
		const qs = buildQueryString(base);
		expect(qs).toContain('period=month');
		expect(qs).toContain('status=all');
	});

	it('omits team when null', () => {
		const qs = buildQueryString({ ...base, team: null });
		expect(qs).not.toContain('team=');
	});

	it('includes team when set', () => {
		const qs = buildQueryString({ ...base, team: 'backend' });
		expect(qs).toContain('team=backend');
	});

	it('omits category when null', () => {
		const qs = buildQueryString({ ...base, category: null });
		expect(qs).not.toContain('category=');
	});

	it('includes category when set', () => {
		const qs = buildQueryString({ ...base, category: 'infrastructure' });
		expect(qs).toContain('category=infrastructure');
	});

	it('includes custom date range only when period=custom', () => {
		const custom: AnalyticsFilter = {
			period: 'custom',
			team: null,
			category: null,
			status: 'all',
			start_date: '2026-01-01',
			end_date: '2026-01-31'
		};
		const qs = buildQueryString(custom);
		expect(qs).toContain('start_date=2026-01-01');
		expect(qs).toContain('end_date=2026-01-31');
	});

	it('omits custom dates for non-custom periods even if provided', () => {
		const qs = buildQueryString({
			...base,
			period: 'week',
			start_date: '2026-01-01',
			end_date: '2026-01-07'
		});
		expect(qs).not.toContain('start_date=');
		expect(qs).not.toContain('end_date=');
	});

	it('builds correct string for all active filters', () => {
		const full: AnalyticsFilter = {
			period: 'quarter',
			team: 'platform',
			category: 'code_pattern',
			status: 'resolved'
		};
		const qs = buildQueryString(full);
		expect(qs).toContain('period=quarter');
		expect(qs).toContain('team=platform');
		expect(qs).toContain('category=code_pattern');
		expect(qs).toContain('status=resolved');
	});
});
