import { listIncidents } from '$lib/services/incidents';
import type { ListFilters } from '$lib/types/incident';

export async function load({ url }) {
	const filters: ListFilters = {
		page: Number(url.searchParams.get('page')) || 1,
		per_page: Number(url.searchParams.get('per_page')) || 20,
		category: (url.searchParams.get('category') as ListFilters['category']) || null,
		severity: (url.searchParams.get('severity') as ListFilters['severity']) || null,
		q: url.searchParams.get('q') || null
	};

	const data = await listIncidents(filters);
	return { ...data, filters };
}
