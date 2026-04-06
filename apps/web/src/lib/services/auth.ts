/**
 * Auth helper service for getting Firebase tokens
 */

import { auth } from '$lib/firebase';

export async function getAuthToken(): Promise<string | null> {
	const user = auth.currentUser;
	if (!user) {
		return null;
	}
	return user.getIdToken();
}

export function getCurrentUser() {
	return auth.currentUser;
}
