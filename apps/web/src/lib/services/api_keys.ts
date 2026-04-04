/** API client for API key management. */

import { getFirebaseAuth } from '$lib/firebase';
import { env } from '$env/dynamic/public';
import type { ApiKey, CreateApiKeyResponse } from '$lib/types/api_keys';

const API_BASE = env.PUBLIC_API_BASE_URL ?? 'https://api.loop.oute.pro';
const BASE = `${API_BASE}/api/v1/api-keys`;

async function getAuthToken(): Promise<string> {
	const user = getFirebaseAuth().currentUser;
	if (!user) throw new Error('Unauthenticated');
	return user.getIdToken();
}

async function request<T>(path: string, options?: Parameters<typeof fetch>[1]): Promise<T> {
	const token = await getAuthToken();
	const response = await fetch(path, {
		...options,
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`,
			...(options?.headers ?? {})
		}
	});
	if (!response.ok) {
		const text = await response.text().catch(() => response.statusText);
		throw new Error(text || `HTTP ${response.status}`);
	}
	return response.json() as Promise<T>;
}

export async function listApiKeys(): Promise<ApiKey[]> {
	return request<ApiKey[]>(BASE);
}

export async function createApiKey(name: string): Promise<CreateApiKeyResponse> {
	return request<CreateApiKeyResponse>(BASE, {
		method: 'POST',
		body: JSON.stringify({ name })
	});
}

export async function revokeApiKey(id: string): Promise<void> {
	const token = await getAuthToken();
	const response = await fetch(`${BASE}/${id}`, {
		method: 'DELETE',
		headers: { Authorization: `Bearer ${token}` }
	});
	if (!response.ok && response.status !== 204) {
		const text = await response.text().catch(() => response.statusText);
		throw new Error(text || `HTTP ${response.status}`);
	}
}

export async function getWhitelist(keyId: string): Promise<{ rule_ids: string[] }> {
	return request<{ rule_ids: string[] }>(`${BASE}/${keyId}/whitelist`);
}

export async function addToWhitelist(keyId: string, ruleId: string): Promise<void> {
	await request(`${BASE}/${keyId}/whitelist`, {
		method: 'POST',
		body: JSON.stringify({ rule_id: ruleId })
	});
}

export async function removeFromWhitelist(keyId: string, ruleId: string): Promise<void> {
	await request(`${BASE}/${keyId}/whitelist/${ruleId}`, { method: 'DELETE' });
}
