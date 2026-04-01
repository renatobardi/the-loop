// SSR disabled: incident routes require Firebase Auth client SDK (browser-only).
// All data fetching happens client-side via incidents.ts service.
import { redirect } from '@sveltejs/kit';
import { getFirebaseAuth } from '$lib/firebase';

export const ssr = false;

export function load() {
	const auth = getFirebaseAuth();
	if (!auth.currentUser) {
		redirect(303, '/login/');
	}
}
