import { env } from '$env/dynamic/public';
import { error } from '@sveltejs/kit';

const API_BASE = env.PUBLIC_API_BASE_URL ?? 'https://api.loop.oute.pro';

export const load = async ({ params }) => {
	const { version } = params;
	try {
		const response = await fetch(`${API_BASE}/api/v1/rules/${version}`);
		if (response.status === 404) {
			throw error(404, `Version ${version} not found`);
		}
		if (!response.ok) {
			return { rules: [], version, rulesCount: 0, error: null };
		}
		const data = await response.json();
		return {
			rules: data.rules ?? [],
			version: data.version ?? version,
			rulesCount: data.rules_count ?? 0,
			error: null
		};
	} catch (err) {
		if ((err as { status?: number }).status === 404) throw err;
		return { rules: [], version, rulesCount: 0, error: null };
	}
};
