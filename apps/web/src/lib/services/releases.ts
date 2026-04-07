/**
 * API service client for releases endpoints
 * Handles: fetchReleases(), markAsRead(), auth token attachment
 */

import { env } from '$env/dynamic/public';
import type { ReleasesListResponse, UnreadCountResponse, ReleaseNotificationStatus, Release } from '$lib/types/releases';
import { getAuthToken } from './auth';

const API_BASE = `${env.PUBLIC_API_BASE_URL ?? 'https://api.loop.oute.pro'}/api/v1/releases`;

async function getAuthHeader(): Promise<string> {
	const token = await getAuthToken();
	if (!token) {
		throw new Error('User not authenticated');
	}
	return `Bearer ${token}`;
}

async function handleResponse<T>(response: Response): Promise<T> {
	if (!response.ok) {
		if (response.status === 429) {
			throw new Error('Rate limited. Please try again later.');
		}
		if (response.status === 401) {
			throw new Error('Unauthorized. Please log in.');
		}
		const error = await response.text();
		throw new Error(`API error (${response.status}): ${error}`);
	}
	return response.json();
}

export async function fetchReleases(): Promise<ReleasesListResponse> {
	const authHeader = await getAuthHeader();
	const response = await fetch(API_BASE, {
		headers: {
			Authorization: authHeader,
			'Content-Type': 'application/json'
		},
		signal: AbortSignal.timeout(5000) // 5 second timeout per request
	});
	return handleResponse<ReleasesListResponse>(response);
}

export async function fetchUnreadCount(): Promise<number> {
	const authHeader = await getAuthHeader();
	const response = await fetch(`${API_BASE}/unread-count`, {
		headers: {
			Authorization: authHeader,
			'Content-Type': 'application/json'
		},
		signal: AbortSignal.timeout(5000)
	});
	const data = await handleResponse<UnreadCountResponse>(response);
	return data.unread_count;
}

export async function markAsRead(releaseId: string): Promise<ReleaseNotificationStatus> {
	const authHeader = await getAuthHeader();
	const response = await fetch(`${API_BASE}/${releaseId}/status`, {
		method: 'PATCH',
		headers: {
			Authorization: authHeader,
			'Content-Type': 'application/json'
		},
		signal: AbortSignal.timeout(5000)
	});
	return handleResponse<ReleaseNotificationStatus>(response);
}

export async function fetchReleaseDetail(releaseId: string): Promise<Release> {
	const authHeader = await getAuthHeader();
	const response = await fetch(`${API_BASE}/${releaseId}`, {
		headers: {
			Authorization: authHeader,
			'Content-Type': 'application/json'
		},
		signal: AbortSignal.timeout(5000)
	});
	return handleResponse<Release>(response);
}
