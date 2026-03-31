import { getIncident } from '$lib/services/incidents';
import { error } from '@sveltejs/kit';

export async function load({ params }) {
	try {
		const incident = await getIncident(params.id);
		return { incident };
	} catch {
		error(404, 'Incident not found');
	}
}
