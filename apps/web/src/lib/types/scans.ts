/** TypeScript types for scans/violations dashboard — Spec-016. */

export interface WeeklyBucket {
	week: string; // "2026-W14"
	count: number;
	findings: number;
}

export interface TopRule {
	rule_id: string;
	count: number;
}

export interface ScanSummary {
	total_scans: number;
	total_findings: number;
	active_repos: number;
	scans_by_week: WeeklyBucket[];
	top_rules: TopRule[];
}

export interface ScanEntry {
	id: string;
	repository: string;
	branch: string;
	pr_number: number | null;
	rules_version: string;
	findings_count: number;
	errors_count: number;
	warnings_count: number;
	duration_ms: number;
	created_at: string;
}
