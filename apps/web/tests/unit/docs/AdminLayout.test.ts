import { describe, it, expect } from 'vitest';

// AdminLayout redirect logic tests (T027).
// The actual Svelte component uses $effect() and goto() which require browser context.
// We test the underlying decision logic as pure functions here — consistent with
// the project's existing test pattern (logic contracts, not component rendering).

type ProfileState = { is_admin: boolean } | null;

/**
 * Pure function mirroring the $effect logic in (admin)/+layout.svelte:
 * - profile !== null && !profile.is_admin → redirect to /docs/
 * - profile === null → loading (unauthenticated or profile not yet loaded)
 * - profile !== null && profile.is_admin → render children
 *
 * Note: $user is NOT checked directly — the auth store starts at null before
 * onAuthStateChanged fires, so checking $user === null would redirect authenticated
 * users on every page load (race condition). $profile is null for unauthenticated
 * users (loadProfile is only called once $user becomes truthy in UserAvatar),
 * so a null profile is a safe proxy for "not ready to render".
 */
function resolveAdminRoute(profile: ProfileState): 'docs' | 'loading' | 'render' {
	if (profile !== null && !profile.is_admin) return 'docs';
	if (profile === null) return 'loading';
	return 'render';
}

describe('AdminLayout — redirect logic (T027)', () => {
	it('unauthenticated (profile never loads) → loading state, no redirect', () => {
		// $profile stays null for unauthenticated users — show loading, never redirect to /login/
		const result = resolveAdminRoute(null);
		expect(result).toBe('loading');
	});

	it('authenticated non-admin → redirect to /docs/', () => {
		const result = resolveAdminRoute({ is_admin: false });
		expect(result).toBe('docs');
	});

	it('authenticated user with profile not yet loaded → loading state (no redirect)', () => {
		const result = resolveAdminRoute(null);
		expect(result).toBe('loading');
	});

	it('authenticated admin → render children', () => {
		const result = resolveAdminRoute({ is_admin: true });
		expect(result).toBe('render');
	});

	// Edge case: admin loses role mid-session
	// The $effect re-evaluates when $profile changes, so is_admin: false triggers redirect
	it('admin loses role mid-session (is_admin changes to false) → redirect to /docs/', () => {
		// Initial state: admin
		expect(resolveAdminRoute({ is_admin: true })).toBe('render');

		// Role revoked: profile updates
		expect(resolveAdminRoute({ is_admin: false })).toBe('docs');
	});

	it('admin with is_admin explicitly true → render', () => {
		const result = resolveAdminRoute({ is_admin: true });
		expect(result).toBe('render');
	});
});
