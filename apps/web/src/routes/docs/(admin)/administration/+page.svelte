<script lang="ts">
	import DocSection from '$lib/components/docs/DocSection.svelte';
	import CodeBlock from '$lib/components/docs/CodeBlock.svelte';

	const apiBaseUrl = `https://api.loop.oute.pro`;

	const rateLimits = `# Analytics endpoints: 60 requests per minute per API key
GET /api/v1/incidents/analytics/*  → 60 req/min

# Waitlist endpoint: 5 requests per minute per IP
POST /api/v1/waitlist              → 5 req/min`;
</script>

<svelte:head>
	<title>Administration — The Loop Docs</title>
	<meta
		name="description"
		content="Platform administration: team management, rate limits, API base URL, and infrastructure overview."
	/>
</svelte:head>

<h1 class="text-3xl font-bold text-text mb-2">Administration</h1>
<p class="text-text-muted mb-8">
	Platform configuration and operational reference for administrators.
</p>

<DocSection title="Team Management" id="team-management">
	<p class="text-text-muted">
		Users are managed via Firebase Authentication. Administrators can invite new users and revoke
		access from the Administration panel. There is no self-service account deletion — contact the
		platform administrator to remove a user.
	</p>
	<p class="text-text-muted">
		<strong class="text-text">Admin role:</strong> the admin flag is set directly on the user's
		Firestore profile document (<code class="text-accent">is_admin: true</code>). Admins see
		additional documentation sections and can access admin-only API endpoints. Currently there is
		no role hierarchy beyond user/admin.
	</p>
	<p class="text-text-muted">
		To grant admin access: update the user's Firestore profile document in the Firebase console
		under the <code class="text-accent">theloopoute</code> project. Changes take effect on the
		user's next page load.
	</p>
</DocSection>

<DocSection title="Rate Limits" id="rate-limits">
	<p class="text-text-muted mb-4">The API enforces the following rate limits:</p>
	<CodeBlock language="text" label="Rate limit configuration" code={rateLimits} />
	<p class="text-text-muted mt-4">
		Rate limits are enforced per API key for authenticated endpoints and per IP address for public
		endpoints. Clients that exceed the limit receive a
		<code class="text-accent">429 Too Many Requests</code> response with a
		<code class="text-accent">Retry-After</code> header.
	</p>
</DocSection>

<DocSection title="API Base URL" id="api-base-url">
	<CodeBlock language="text" label="Production API base URL" code={apiBaseUrl} />
	<p class="text-text-muted mt-4">
		All API endpoints are relative to this base URL. The API is deployed to Cloud Run and served
		over HTTPS exclusively. There is no HTTP fallback — all traffic is TLS-enforced via HSTS.
	</p>
</DocSection>

<DocSection title="Single-Environment Model" id="environment">
	<p class="text-text-muted">
		The Loop runs in a single environment: production. There is no staging or development
		environment. Every change merged to <code class="text-accent">main</code> is automatically
		deployed to production via GitHub Actions.
	</p>
	<p class="text-text-muted">
		This model requires strict CI gates (lint, type-check, tests, build, vulnerability scan) to
		pass before any merge. If a gate fails, the merge is blocked.
	</p>
</DocSection>

<DocSection title="Firebase Project" id="firebase">
	<p class="text-text-muted">
		The platform uses Firebase project <code class="text-accent">theloopoute</code>:
	</p>
	<ul class="list-disc list-inside text-text-muted space-y-1 ml-2">
		<li>
			<strong class="text-text">Authentication:</strong> Firebase Auth (email/password)
		</li>
		<li>
			<strong class="text-text">Firestore:</strong> user profiles, waitlist, rate limiting — region
			<code class="text-accent">southamerica-east1</code>
		</li>
		<li>
			<strong class="text-text">Cloud SQL:</strong>
			<code class="text-accent">theloopoute:southamerica-east1:theloop-db</code> — PostgreSQL 16 +
			pgvector (incidents, postmortems, analytics, scans, API keys)
		</li>
	</ul>
</DocSection>
