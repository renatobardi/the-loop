import {
	getAnalyticsSummary,
	getAnalyticsByCategory,
	getAnalyticsByTeam,
	getAnalyticsTimeline,
	getAnalyticsSeverityTrend,
	getAnalyticsTopRules
} from '$lib/services/analytics';
import type { AnalyticsFilter, Period, StatusFilter, RootCauseCategory } from '$lib/types/analytics';

export async function load({ url, parent }) {
	// Wait for the layout's waitForAuth() to complete before making any API calls.
	// Layout and page loads run concurrently in SvelteKit — without this, auth.currentUser
	// may be null when analytics.ts runs, even if the user is authenticated.
	await parent();
	const period = (url.searchParams.get('period') || 'month') as Period;
	const teams = url.searchParams.getAll('team'); // multi-select: ?team=a&team=b
	const category = (url.searchParams.get('category') || null) as RootCauseCategory | null;
	const status = (url.searchParams.get('status') || 'all') as StatusFilter;
	const start_date = url.searchParams.get('start_date') || null;
	const end_date = url.searchParams.get('end_date') || null;

	const filters: AnalyticsFilter = { period, teams, category, status, start_date, end_date };

	// byTeamAll fetches all teams (no filter) for dropdown population
	const teamAllFilters: AnalyticsFilter = { ...filters, teams: [] };

	const empty = {
		summary: { total: 0, resolved: 0, unresolved: 0, avg_resolution_days: null },
		byCategory: [],
		byTeam: [],
		byTeamAll: [],
		timeline: [],
		severityTrend: [],
		topRules: [],
		filters,
		loadError: null as string | null
	};

	try {
		const [summary, byCategory, byTeam, byTeamAll, timeline, severityTrend, topRules] =
			await Promise.all([
				getAnalyticsSummary(filters),
				getAnalyticsByCategory(filters),
				getAnalyticsByTeam(filters),
				getAnalyticsByTeam(teamAllFilters),
				getAnalyticsTimeline(filters),
				getAnalyticsSeverityTrend(filters),
				getAnalyticsTopRules(filters)
			]);
		return {
			summary,
			byCategory,
			byTeam,
			byTeamAll,
			timeline,
			severityTrend,
			topRules,
			filters,
			loadError: null
		};
	} catch (err) {
		return {
			...empty,
			loadError: err instanceof Error ? err.message : 'Unable to load analytics data'
		};
	}
}
