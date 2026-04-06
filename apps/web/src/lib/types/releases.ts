/**
 * Type definitions for Product Releases Notification feature
 */

export interface Release {
	id: string;
	title: string;
	version: string;
	published_date: string;
	summary: string | null;
	changelog_html: string | null;
	breaking_changes_flag: boolean;
	documentation_url: string | null;
}

export interface ReleaseNotificationStatus {
	id: string;
	release_id: string;
	user_id: string;
	is_read: boolean;
	read_at: string | null;
}

export interface ReleaseWithStatus extends Release {
	isRead: boolean;
	readAt: string | null;
}

export interface ReleasesListResponse {
	items: Array<{
		release: Release;
		is_read: boolean;
		read_at: string | null;
	}>;
	total: number;
}

export interface UnreadCountResponse {
	unread_count: number;
}
