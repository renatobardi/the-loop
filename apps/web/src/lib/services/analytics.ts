/** API client for analytics endpoints — handles auth, errors. */

import type {
	AnalyticsFilter,
	AnalyticsSummary,
	CategoryStats,
	TeamStats,
	TimelinePoint
} from '$lib/types/analytics';
import { waitForAuth } from '$lib/firebase';
import { env } from '$env/dynamic/public';

const API_BASE = env.PUBLIC_API_BASE_URL ?? 'https://api.loop.oute.pro';
const BASE = `${API_BASE}/api/v1/incidents/analytics`;

async function getAuthToken(): Promise<string> {
	const user = await waitForAuth();
	if (!user) {
		window.location.href = '/?auth=required';
		throw new Error('Unauthenticated');
	}
	return user.getIdToken();
}

async function request<T>(path: string): Promise<T> {
	const token = await getAuthToken();
	const response = await fetch(path, {
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});

	if (response.status === 401) {
		window.location.href = '/?auth=required';
		throw new Error('Unauthenticated');
	}

	if (response.status === 429) {
		const retryAfter = response.headers.get('Retry-After') || '60';
		throw new Error(`Rate limited. Try again in ${retryAfter}s`);
	}

	if (!response.ok) {
		const body = await response.json().catch(() => ({ detail: 'Unknown error' }));
		const detail = typeof body.detail === 'string' ? body.detail : 'Error';
		throw new Error(detail);
	}

	return response.json() as Promise<T>;
}

export function buildQueryString(filters: AnalyticsFilter): string {
	const params = new URLSearchParams();
	params.set('period', filters.period);
	if (filters.team) params.set('team', filters.team);
	if (filters.category) params.set('category', filters.category);
	params.set('status', filters.status);
	if (filters.period === 'custom') {
		if (filters.start_date) params.set('start_date', filters.start_date);
		if (filters.end_date) params.set('end_date', filters.end_date);
	}
	return params.toString();
}

export async function getAnalyticsSummary(filters: AnalyticsFilter): Promise<AnalyticsSummary> {
	return request<AnalyticsSummary>(`${BASE}/summary?${buildQueryString(filters)}`);
}

export async function getAnalyticsByCategory(filters: AnalyticsFilter): Promise<CategoryStats[]> {
	return request<CategoryStats[]>(`${BASE}/by-category?${buildQueryString(filters)}`);
}

export async function getAnalyticsByTeam(filters: AnalyticsFilter): Promise<TeamStats[]> {
	return request<TeamStats[]>(`${BASE}/by-team?${buildQueryString(filters)}`);
}

export async function getAnalyticsTimeline(filters: AnalyticsFilter): Promise<TimelinePoint[]> {
	return request<TimelinePoint[]>(`${BASE}/timeline?${buildQueryString(filters)}`);
}
