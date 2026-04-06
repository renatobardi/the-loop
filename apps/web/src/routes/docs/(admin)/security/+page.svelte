<script lang="ts">
	import DocSection from '$lib/components/docs/DocSection.svelte';
	import CodeBlock from '$lib/components/docs/CodeBlock.svelte';

	const securityHeaders = `Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; ...
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Permissions-Policy: camera=(), microphone=(), geolocation=()`;

	const tokenFormats = `# Firebase JWT (authenticated users)
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
# Issued by: Firebase Authentication
# Verified by: firebase-admin SDK on the API server

# API Key (scanner CI workflow)
Authorization: Bearer tlp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Prefix: tlp_
# Verified by: database lookup in api_keys table`;
</script>

<svelte:head>
	<title>Security — The Loop Docs</title>
	<meta
		name="description"
		content="Security architecture: auth tiers, token formats, HTTP security headers, Firebase Security Rules, secrets management, and audit logs."
	/>
</svelte:head>

<h1 class="text-3xl font-bold text-text mb-2">Security</h1>
<p class="text-text-muted mb-8">
	Security architecture and operational controls for The Loop platform.
</p>

<DocSection title="Authentication Tiers" id="auth-tiers">
	<p class="text-text-muted mb-4">
		Every API endpoint operates under one of four authentication tiers:
	</p>
	<div class="overflow-x-auto">
		<table class="w-full text-sm">
			<thead>
				<tr class="border-b border-border text-left">
					<th class="pb-2 pr-4 text-text font-semibold">Tier</th>
					<th class="pb-2 pr-4 text-text font-semibold">Token</th>
					<th class="pb-2 pr-4 text-text font-semibold">Who Uses It</th>
					<th class="pb-2 text-text font-semibold">Access Level</th>
				</tr>
			</thead>
			<tbody class="text-text-muted">
				<tr class="border-b border-border/50">
					<td class="py-2 pr-4 font-semibold text-text">Anonymous</td>
					<td class="py-2 pr-4">None</td>
					<td class="py-2 pr-4">Public browsers</td>
					<td class="py-2">Read-only public endpoints (waitlist, rule browser)</td>
				</tr>
				<tr class="border-b border-border/50">
					<td class="py-2 pr-4 font-semibold text-text">API Key</td>
					<td class="py-2 pr-4 font-mono text-accent">tlp_…</td>
					<td class="py-2 pr-4">CI scanner workflows</td>
					<td class="py-2">Rules API (filtered to project whitelist), scan ingestion</td>
				</tr>
				<tr class="border-b border-border/50">
					<td class="py-2 pr-4 font-semibold text-text">Firebase JWT</td>
					<td class="py-2 pr-4 font-mono text-accent">eyJ…</td>
					<td class="py-2 pr-4">Authenticated web users</td>
					<td class="py-2">Full access to their organization's data</td>
				</tr>
				<tr>
					<td class="py-2 pr-4 font-semibold text-text">Admin</td>
					<td class="py-2 pr-4 font-mono text-accent">eyJ…</td>
					<td class="py-2 pr-4">Firebase users with <code class="text-accent">is_admin: true</code></td>
					<td class="py-2">Admin endpoints (rule publishing, user management)</td>
				</tr>
			</tbody>
		</table>
	</div>
</DocSection>

<DocSection title="Token Formats" id="token-formats">
	<CodeBlock language="text" label="Authorization header formats" code={tokenFormats} />
	<p class="text-text-muted mt-4">
		Firebase JWTs expire after 1 hour. The Firebase client SDK handles automatic refresh
		transparently. API keys do not expire — revoke them manually when no longer needed.
	</p>
</DocSection>

<DocSection title="HTTP Security Headers" id="security-headers">
	<p class="text-text-muted mb-4">
		All responses from the web server include these security headers (set in
		<code class="text-accent">src/hooks.server.ts</code>):
	</p>
	<CodeBlock language="text" label="Response security headers" code={securityHeaders} />
	<p class="text-text-muted mt-4">
		HSTS ensures all future requests use HTTPS even if the user types
		<code class="text-accent">http://</code>. CSP restricts script sources. X-Frame-Options
		prevents clickjacking.
	</p>
</DocSection>

<DocSection title="Firebase Security Rules" id="firebase-rules">
	<p class="text-text-muted">
		Firestore Security Rules restrict direct database access from client SDKs:
	</p>
	<ul class="list-disc list-inside text-text-muted space-y-1 ml-2">
		<li>
			<strong class="text-text">Waitlist collection:</strong> write-only for anonymous users. No
			read access from the client.
		</li>
		<li>
			<strong class="text-text">User profiles:</strong> read/write only by the authenticated user
			who owns the document.
		</li>
		<li>
			<strong class="text-text">All other collections:</strong> no direct client access — all data
			flows through the FastAPI backend with Firebase JWT verification.
		</li>
	</ul>
</DocSection>

<DocSection title="Secrets Management" id="secrets">
	<p class="text-text-muted">
		All secrets are managed via <strong class="text-text">GCP Secret Manager</strong>:
	</p>
	<ul class="list-disc list-inside text-text-muted space-y-1 ml-2">
		<li>
			<code class="text-accent">FIREBASE_SERVICE_ACCOUNT</code> — Firebase Admin SDK credentials
			(used by both web and API services)
		</li>
		<li>
			<code class="text-accent">THELOOP_API_DATABASE_URL</code> — PostgreSQL connection string
		</li>
	</ul>
	<p class="text-text-muted">
		No secrets are stored in environment variables directly in Cloud Run — all are fetched from
		Secret Manager at runtime. GitHub Actions secrets are separate and used only during CI/CD
		(Workload Identity Federation for GCP auth, no service account keys in the repo).
	</p>
</DocSection>

<DocSection title="Cloud Audit Logs" id="audit-logs">
	<p class="text-text-muted">
		GCP Cloud Audit Logs are active for all GCP services used by The Loop:
	</p>
	<ul class="list-disc list-inside text-text-muted space-y-1 ml-2">
		<li>Cloud Run — all service deployments and invocations</li>
		<li>Cloud SQL — all admin operations (not query-level)</li>
		<li>Secret Manager — all secret access events</li>
		<li>IAM — all permission changes</li>
	</ul>
	<p class="text-text-muted">
		Audit logs are retained for 400 days (GCP default for Admin Activity logs). Access logs
		(Data Access) are enabled for Secret Manager only.
	</p>
</DocSection>
