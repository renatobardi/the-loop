/** TypeScript types for incident analytics dashboard — Spec-014. */

export type Period = 'week' | 'month' | 'quarter' | 'custom';
export type StatusFilter = 'resolved' | 'unresolved' | 'all';
export type RootCauseCategory =
	| 'code_pattern'
	| 'infrastructure'
	| 'process_breakdown'
	| 'third_party'
	| 'unknown';

export interface AnalyticsFilter {
	period: Period;
	teams?: string[]; // Multi-select: ?team=a&team=b; empty = no filter
	category?: RootCauseCategory | null;
	status: StatusFilter;
	start_date?: string | null; // YYYY-MM-DD (required if period=custom)
	end_date?: string | null; // YYYY-MM-DD (required if period=custom)
}

export interface AnalyticsSummary {
	total: number;
	resolved: number;
	unresolved: number;
	avg_resolution_days: number | null;
}

export interface CategoryStats {
	category: RootCauseCategory;
	count: number;
	percentage: number; // 0–100
	avg_severity: number; // 0.5 (warning) or 1.0 (error)
	avg_resolution_days: number | null;
}

export interface TeamStats {
	team: string;
	count: number;
	top_categories: RootCauseCategory[];
	avg_resolution_days: number | null;
}

export interface TimelinePoint {
	week: string; // ISO date string YYYY-MM-DD
	count: number;
	by_category: Record<RootCauseCategory, number>; // Always all 5 keys
}

export interface SeverityTrendPoint {
	week: string; // ISO date string YYYY-MM-DD
	error_count: number;
	warning_count: number;
}

export interface RuleEffectivenessStats {
	rule_id: string;
	incident_count: number;
	avg_severity: number; // 0.5 (warning) or 1.0 (error)
}
