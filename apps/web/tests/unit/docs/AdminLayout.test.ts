import { describe, it, expect } from 'vitest';

// AdminLayout redirect logic tests (T027).
// The actual Svelte component uses $effect() and goto() which require browser context.
// We test the underlying decision logic as pure functions here — consistent with
// the project's existing test pattern (logic contracts, not component rendering).

type AuthState = {
	user: { uid: string } | null;
	profile: { is_admin: boolean } | null;
};

/**
 * Pure function mirroring the $effect logic in (admin)/+layout.svelte:
 * - user === null → redirect to /login/
 * - profile !== null && !profile.is_admin → redirect to /docs/
 * - profile === null && user !== null → loading (no redirect)
 * - profile !== null && profile.is_admin → render children (no redirect)
 */
function resolveAdminRoute(state: AuthState): 'login' | 'docs' | 'loading' | 'render' {
	if (state.user === null) return 'login';
	if (state.profile !== null && !state.profile.is_admin) return 'docs';
	if (state.profile === null) return 'loading';
	return 'render';
}

describe('AdminLayout — redirect logic (T027)', () => {
	it('unauthenticated user → redirect to /login/', () => {
		const result = resolveAdminRoute({ user: null, profile: null });
		expect(result).toBe('login');
	});

	it('unauthenticated user ignores profile state → still redirects to /login/', () => {
		// Even if profile is somehow set, missing user takes priority
		const result = resolveAdminRoute({ user: null, profile: { is_admin: true } });
		expect(result).toBe('login');
	});

	it('authenticated non-admin → redirect to /docs/', () => {
		const result = resolveAdminRoute({
			user: { uid: 'user-123' },
			profile: { is_admin: false }
		});
		expect(result).toBe('docs');
	});

	it('authenticated user with profile not yet loaded → loading state (no redirect)', () => {
		const result = resolveAdminRoute({ user: { uid: 'user-123' }, profile: null });
		expect(result).toBe('loading');
	});

	it('authenticated admin → render children', () => {
		const result = resolveAdminRoute({
			user: { uid: 'admin-456' },
			profile: { is_admin: true }
		});
		expect(result).toBe('render');
	});

	// Edge case from spec: admin loses role mid-session
	// The $effect re-evaluates when $profile changes, so is_admin: false triggers redirect
	it('admin loses role mid-session (is_admin changes to false) → redirect to /docs/', () => {
		// Initial state: admin
		let state: AuthState = { user: { uid: 'admin-456' }, profile: { is_admin: true } };
		expect(resolveAdminRoute(state)).toBe('render');

		// Role revoked: profile updates
		state = { user: { uid: 'admin-456' }, profile: { is_admin: false } };
		expect(resolveAdminRoute(state)).toBe('docs');
	});

	it('admin with is_admin explicitly true → render', () => {
		const result = resolveAdminRoute({
			user: { uid: 'admin-789' },
			profile: { is_admin: true }
		});
		expect(result).toBe('render');
	});
});
