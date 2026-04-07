/**
 * Auth helper service for getting Firebase tokens
 */

import { getFirebaseAuth } from '$lib/firebase';

export async function getAuthToken(): Promise<string | null> {
	const auth = getFirebaseAuth();
	const user = auth.currentUser;
	if (!user) {
		return null;
	}
	return user.getIdToken();
}

export function getCurrentUser() {
	const auth = getFirebaseAuth();
	return auth.currentUser;
}
