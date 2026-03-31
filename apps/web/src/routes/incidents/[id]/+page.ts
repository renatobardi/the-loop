import { getIncident } from '$lib/services/incidents';
import { error } from '@sveltejs/kit';

export async function load({ params }) {
	try {
		const incident = await getIncident(params.id);
		return { incident };
	} catch (err) {
		const message = err instanceof Error ? err.message : '';
		if (message === 'Not Found' || message.includes('not found') || message.includes('404')) {
			error(404, 'Incident not found');
		}
		error(503, 'Unable to connect to the server');
	}
}
