export interface RuleData {
	id: string;
	languages: string[];
	message: string;
	severity: string;
	metadata: Record<string, unknown>;
	patterns: Array<Record<string, unknown>>;
}

export interface VersionSummary {
	version: string;
	status: string;
	created_at: string;
	rules_count: number;
	deprecated_at: string | null;
}

export interface AdminMetrics {
	active_repos: number;
	scans_by_week: Array<{ week: string; count: number; findings: number }>;
	top_languages: Array<{ language: string; count: number }>;
}

export interface EditRuleData {
	message: string;
	severity: string;
	pattern: string;
	languages: string[];
}
