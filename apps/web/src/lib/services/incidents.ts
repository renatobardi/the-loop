/** API client for incident endpoints — handles auth, errors, rate limiting. */

import type {
	Incident,
	IncidentCreate,
	IncidentUpdate,
	ListFilters,
	PaginatedResponse
} from '$lib/types/incident';
import { getFirebaseAuth } from '$lib/firebase';
import { env } from '$env/dynamic/public';

// Production API base; override with PUBLIC_API_BASE_URL in Cloud Run env_vars if needed.
const API_BASE = env.PUBLIC_API_BASE_URL ?? 'https://theloop-api-1090621437043.us-central1.run.app';
const BASE = `${API_BASE}/api/v1/incidents`;

async function getAuthToken(): Promise<string> {
	const auth = getFirebaseAuth();
	const user = auth.currentUser;
	if (!user) {
		window.location.href = '/?auth=required';
		throw new Error('Unauthenticated');
	}
	return user.getIdToken();
}

async function request<T>(path: string, options: globalThis.RequestInit = {}): Promise<T> {
	const token = await getAuthToken();
	const headers: Record<string, string> = {
		'Content-Type': 'application/json',
		Authorization: `Bearer ${token}`,
		...(options.headers as Record<string, string>)
	};

	const response = await fetch(path, { ...options, headers });

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
		const detail = typeof body.detail === 'string' ? body.detail : body.detail?.detail || 'Error';
		throw new Error(detail);
	}

	return response.json() as Promise<T>;
}

export async function createIncident(data: IncidentCreate): Promise<Incident> {
	return request<Incident>(BASE, {
		method: 'POST',
		body: JSON.stringify(data)
	});
}

export async function listIncidents(filters: ListFilters = {}): Promise<PaginatedResponse> {
	const params = new URLSearchParams();
	if (filters.page) params.set('page', String(filters.page));
	if (filters.per_page) params.set('per_page', String(filters.per_page));
	if (filters.category) params.set('category', filters.category);
	if (filters.severity) params.set('severity', filters.severity);
	if (filters.q) params.set('q', filters.q);

	const query = params.toString();
	return request<PaginatedResponse>(`${BASE}${query ? `?${query}` : ''}`);
}

export async function getIncident(id: string): Promise<Incident> {
	return request<Incident>(`${BASE}/${id}`);
}

export async function updateIncident(id: string, data: IncidentUpdate): Promise<Incident> {
	return request<Incident>(`${BASE}/${id}`, {
		method: 'PUT',
		body: JSON.stringify(data)
	});
}

export async function deleteIncident(id: string): Promise<void> {
	await request(`${BASE}/${id}`, { method: 'DELETE' });
}
