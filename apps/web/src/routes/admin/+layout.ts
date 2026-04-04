// SSR disabled: requires Firebase Auth client SDK (browser-only).
import { redirect } from '@sveltejs/kit';
import { waitForAuth } from '$lib/firebase';

export const ssr = false;

export async function load() {
	const user = await waitForAuth();
	if (!user) {
		redirect(303, '/login/');
	}
}
