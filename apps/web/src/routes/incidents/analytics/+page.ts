import {
	getAnalyticsSummary,
	getAnalyticsByCategory,
	getAnalyticsByTeam,
	getAnalyticsTimeline
} from '$lib/services/analytics';
import type { AnalyticsFilter, Period, StatusFilter, RootCauseCategory } from '$lib/types/analytics';

export async function load({ url }) {
	const period = (url.searchParams.get('period') || 'month') as Period;
	const team = url.searchParams.get('team') || null;
	const category = (url.searchParams.get('category') || null) as RootCauseCategory | null;
	const status = (url.searchParams.get('status') || 'all') as StatusFilter;
	const start_date = url.searchParams.get('start_date') || null;
	const end_date = url.searchParams.get('end_date') || null;

	const filters: AnalyticsFilter = { period, team, category, status, start_date, end_date };

	// byTeamAll fetches all teams (no team filter) for dropdown population
	const teamAllFilters: AnalyticsFilter = { ...filters, team: null };

	const empty = {
		summary: { total: 0, resolved: 0, unresolved: 0, avg_resolution_days: null },
		byCategory: [],
		byTeam: [],
		byTeamAll: [],
		timeline: [],
		filters,
		loadError: null as string | null
	};

	try {
		const [summary, byCategory, byTeam, byTeamAll, timeline] = await Promise.all([
			getAnalyticsSummary(filters),
			getAnalyticsByCategory(filters),
			getAnalyticsByTeam(filters),
			getAnalyticsByTeam(teamAllFilters),
			getAnalyticsTimeline(filters)
		]);
		return { summary, byCategory, byTeam, byTeamAll, timeline, filters, loadError: null };
	} catch (err) {
		return {
			...empty,
			loadError: err instanceof Error ? err.message : 'Unable to load analytics data'
		};
	}
}
