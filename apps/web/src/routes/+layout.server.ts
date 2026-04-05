/** Server-side layout data — runs before page load, ensures auth context is available. */

export const load = async ({ parent }) => {
	// Invoke parent hooks (ensures security headers, etc. are applied)
	await parent();
	return {};
};
