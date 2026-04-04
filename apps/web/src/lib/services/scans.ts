/** API client for scans endpoints — Firebase auth required. */

import { getFirebaseAuth } from '$lib/firebase';
import { env } from '$env/dynamic/public';
import type { ScanEntry, ScanSummary } from '$lib/types/scans';

const API_BASE = env.PUBLIC_API_BASE_URL ?? 'https://api.loop.oute.pro';
const BASE = `${API_BASE}/api/v1/scans`;

async function getAuthToken(): Promise<string> {
	const user = getFirebaseAuth().currentUser;
	if (!user) {
		window.location.href = '/?auth=required';
		throw new Error('Unauthenticated');
	}
	return await user.getIdToken();
}

async function request<T>(path: string): Promise<T> {
	const token = await getAuthToken();
	const response = await fetch(path, {
		headers: { Authorization: `Bearer ${token}` }
	});
	if (response.status === 401) {
		window.location.href = '/?auth=required';
		throw new Error('Unauthenticated');
	}
	if (!response.ok) {
		throw new Error(`Request failed: ${response.status}`);
	}
	return response.json() as Promise<T>;
}

export async function getScansSummary(): Promise<ScanSummary> {
	return request<ScanSummary>(`${BASE}/summary`);
}

export async function getScans(): Promise<{ items: ScanEntry[]; total: number }> {
	return request<{ items: ScanEntry[]; total: number }>(BASE);
}
