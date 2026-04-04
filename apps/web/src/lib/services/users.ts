/** API client for user profile endpoints — handles auth, errors. */

import type { UserProfile, UserPatch } from '$lib/types/users';
import { getFirebaseAuth } from '$lib/firebase';
import { env } from '$env/dynamic/public';

const API_BASE = env.PUBLIC_API_BASE_URL ?? 'https://api.loop.oute.pro';
const BASE = `${API_BASE}/api/v1/users`;

async function getAuthToken(): Promise<string> {
	const user = getFirebaseAuth().currentUser;
	if (!user) {
		window.location.href = '/?auth=required';
		throw new Error('Unauthenticated');
	}
	return await user.getIdToken();
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
		throw new Error(`${response.status}: ${text}`);
	}
	return response.json() as Promise<T>;
}

export async function getMe(): Promise<UserProfile> {
	return request<UserProfile>(`${BASE}/me`);
}

export async function updateMe(patch: UserPatch): Promise<UserProfile> {
	return request<UserProfile>(`${BASE}/me`, {
		method: 'PATCH',
		body: JSON.stringify(patch)
	});
}
