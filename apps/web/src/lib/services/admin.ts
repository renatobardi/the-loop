/** Admin-only API client for rule management and metrics. */

import { waitForAuth } from '$lib/firebase';
import { env } from '$env/dynamic/public';
import type { AdminMetrics, EditRuleData, RuleData, VersionSummary } from '$lib/types/rules';

const API_BASE = env.PUBLIC_API_BASE_URL ?? 'https://api.loop.oute.pro';

async function getAuthToken(): Promise<string> {
	const user = await waitForAuth();
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

export async function getAdminMetrics(): Promise<AdminMetrics> {
	return request<AdminMetrics>(`${API_BASE}/api/v1/admin/metrics`);
}

export async function createVersion(
	version: string
): Promise<{ version: string; status: string }> {
	return request<{ version: string; status: string }>(`${API_BASE}/api/v1/rules/versions`, {
		method: 'POST',
		body: JSON.stringify({ version })
	});
}

export async function publishVersion(
	version: string,
	rules: RuleData[],
	notes?: string
): Promise<void> {
	await request(`${API_BASE}/api/v1/rules/publish`, {
		method: 'POST',
		body: JSON.stringify({ version, rules, notes })
	});
}

export async function editRule(
	version: string,
	ruleId: string,
	data: EditRuleData
): Promise<void> {
	await request(`${API_BASE}/api/v1/rules/${version}/rules/${ruleId}`, {
		method: 'PUT',
		body: JSON.stringify(data)
	});
}

export async function listVersions(): Promise<{ versions: VersionSummary[] }> {
	return request<{ versions: VersionSummary[] }>(`${API_BASE}/api/v1/rules/versions`);
}
