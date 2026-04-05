import type {
	AnalyticsFilter,
	Period,
	StatusFilter,
	RootCauseCategory
} from '$lib/types/analytics';

// Firebase Auth is client-side only — disable SSR to avoid hydration race conditions
// where $effect runs with undefined data.filters before the client-side load completes.
// Same approach used by /login/ and /signup/.
export const ssr = false;

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
