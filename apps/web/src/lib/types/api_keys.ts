export interface ApiKey {
	id: string;
	name: string;
	prefix: string;
	last_used_at: string | null;
	revoked_at: string | null;
	created_at: string;
}

export interface CreateApiKeyResponse {
	id: string;
	name: string;
	prefix: string;
	token: string;
	created_at: string;
}
