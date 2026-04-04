// SSR disabled: requires Firebase Auth client SDK (browser-only).
import { redirect } from '@sveltejs/kit';
import { waitForAuth } from '$lib/firebase';
import { getScansSummary } from '$lib/services/scans';
import type { ScanSummary } from '$lib/types/scans';

export const ssr = false;

export async function load() {
	const user = await waitForAuth();
	if (!user) {
		redirect(303, '/login/');
	}

	const emptySummary: ScanSummary = {
		total_scans: 0,
		total_findings: 0,
		active_repos: 0,
		scans_by_week: [],
		top_rules: []
	};

	try {
		const summary = await getScansSummary();
		return { summary, loadError: null };
	} catch (err) {
		return {
			summary: emptySummary,
			loadError: err instanceof Error ? err.message : 'Failed to load scan data'
		};
	}
}
