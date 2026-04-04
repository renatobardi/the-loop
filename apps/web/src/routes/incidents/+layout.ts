// SSR disabled: incident routes require Firebase Auth client SDK (browser-only).
// All data fetching happens client-side via incidents.ts service.
import { redirect } from '@sveltejs/kit';
import { waitForAuth } from '$lib/firebase';

export const ssr = false;

export async function load() {
	const user = await waitForAuth();
	if (!user) {
		redirect(303, '/login/');
	}
}
