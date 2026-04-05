import {
	getAnalyticsSummary,
	getAnalyticsByCategory,
	getAnalyticsByTeam,
	getAnalyticsTimeline,
	getAnalyticsSeverityTrend,
	getAnalyticsTopRules
} from '$lib/services/analytics';
import type { AnalyticsFilter, Period, StatusFilter, RootCauseCategory } from '$lib/types/analytics';

export async function load({ url }) {
	// Parse URL filters — API calls happen client-side only (Firebase Auth required)
	const period = (url.searchParams.get('period') || 'month') as Period;
	const teams = url.searchParams.getAll('team');
	const category = (url.searchParams.get('category') || null) as RootCauseCategory | null;
	const status = (url.searchParams.get('status') || 'all') as StatusFilter;
	const start_date = url.searchParams.get('start_date') || null;
	const end_date = url.searchParams.get('end_date') || null;

	const filters: AnalyticsFilter = { period, teams, category, status, start_date, end_date };

	return {
		summary: null,
		byCategory: null,
		byTeam: null,
		byTeamAll: null,
		timeline: null,
		severityTrend: null,
		topRules: null,
		filters,
		loadError: null as string | null
	};
}
