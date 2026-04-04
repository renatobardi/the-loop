/**
 * Pure utility functions for analytics — shared across components and testable
 * without a DOM/Svelte environment.
 */

import type { TeamStats } from '$lib/types/analytics';

/** Convert snake_case category key to display label: "code_pattern" → "Code Pattern" */
export function formatCategory(cat: string): string {
	return cat.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Format avg_resolution_days for display. Null → "N/A", number → "3.1d". */
export function formatDays(days: number | null): string {
	if (days === null) return 'N/A';
	return `${days.toFixed(1)}d`;
}

/**
 * Map avg_severity score to a bar fill color.
 * 1.0 = error severity (red), 0.5 = warning severity (amber).
 */
export function barColor(avgSeverity: number): string {
	return avgSeverity >= 0.9 ? 'var(--color-error, #ef4444)' : 'var(--color-warning, #f59e0b)';
}

/** Sort TeamStats by count. Pass asc=true for ascending, false for descending. */
export function sortTeamsByCount(teams: TeamStats[], asc: boolean): TeamStats[] {
	return [...teams].sort((a, b) => (asc ? a.count - b.count : b.count - a.count));
}
