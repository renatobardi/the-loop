export interface UserProfile {
	id: string;
	email: string;
	display_name: string | null;
	job_title: string | null;
	plan: string;
	is_admin?: boolean;
	created_at: string;
}

export interface UserPatch {
	display_name?: string;
	job_title?: string | null;
}
