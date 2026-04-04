import { writable } from 'svelte/store';
import type { UserProfile } from '$lib/types/users';

export const profile = writable<UserProfile | null>(null);

export async function loadProfile(): Promise<void> {
	const { getMe } = await import('$lib/services/users');
	const data = await getMe();
	profile.set(data);
}

export function clearProfile(): void {
	profile.set(null);
}
