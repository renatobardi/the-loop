/**
 * Compute avatar initials from display name or email fallback.
 * - "Renato Bardi" → "RB"
 * - null + "renato@example.com" → "RE"
 */
export function getInitials(displayName: string | null | undefined, email: string | null | undefined): string {
	if (displayName) {
		const parts = displayName.trim().split(/\s+/);
		const first = parts[0]?.[0] ?? '';
		const second = parts[1]?.[0] ?? '';
		const result = (first + second).toUpperCase();
		return result || displayName[0].toUpperCase();
	}
	return (email ?? '').slice(0, 2).toUpperCase();
}
