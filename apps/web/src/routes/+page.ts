import { redirect } from '@sveltejs/kit';

export function load({ url }) {
	if (url.searchParams.has('auth')) {
		redirect(303, '/login/');
	}
}
