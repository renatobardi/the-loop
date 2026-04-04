import { env } from '$env/dynamic/public';

const API_BASE = env.PUBLIC_API_BASE_URL ?? 'https://api.loop.oute.pro';

export const load = async () => {
	try {
		const response = await fetch(`${API_BASE}/api/v1/rules/latest`);
		if (!response.ok) {
			return { rules: [], version: null, rulesCount: 0, error: null };
		}
		const data = await response.json();
		return {
			rules: data.rules ?? [],
			version: data.version ?? null,
			rulesCount: data.rules_count ?? 0,
			error: null
		};
	} catch {
		return { rules: [], version: null, rulesCount: 0, error: null };
	}
};
