<script lang="ts">
	import DocSection from '$lib/components/docs/DocSection.svelte';
</script>

<svelte:head>
	<title>Getting Started — The Loop Docs</title>
	<meta
		name="description"
		content="Start using The Loop: create your account, open your first incident, navigate the dashboard, and invite your team."
	/>
</svelte:head>

<h1 class="text-3xl font-bold text-text mb-2">Getting Started</h1>
<p class="text-text-muted mb-8">
	Follow these steps to go from a new account to your first incident in under 10 minutes.
</p>

<DocSection title="1. Account Setup" id="account-setup">
	<p class="text-text-muted">
		Sign in at <a href="/login/" class="text-accent hover:underline">loop.oute.pro/login</a>. If
		your organization already uses The Loop, ask your administrator to invite you — invitations
		arrive by email and include a direct login link.
	</p>
	<p class="text-text-muted">
		After signing in, complete your profile: set your display name and job title. These fields
		appear on incidents you create and resolve, so keep them accurate.
	</p>
</DocSection>

<DocSection title="2. Create Your First Incident" id="first-incident">
	<p class="text-text-muted">
		Navigate to <a href="/incidents/" class="text-accent hover:underline">Incidents</a> and click
		<strong class="text-text">New Incident</strong>.
	</p>
	<p class="text-text-muted">Fill in the required fields:</p>
	<ul class="list-disc list-inside text-text-muted space-y-1 ml-2">
		<li><strong class="text-text">Title</strong> — a short, descriptive summary of what happened</li>
		<li>
			<strong class="text-text">Severity</strong> — <code class="text-accent">critical</code>,
			<code class="text-accent">high</code>, <code class="text-accent">medium</code>, or
			<code class="text-accent">low</code>
		</li>
		<li>
			<strong class="text-text">Category</strong> — the type of failure (code pattern, infrastructure,
			process, third-party, or unknown)
		</li>
		<li><strong class="text-text">Team</strong> — the team responsible for resolution</li>
	</ul>
	<p class="text-text-muted">
		Click <strong class="text-text">Create</strong>. The incident opens in
		<code class="text-accent">investigating</code> status automatically.
	</p>
</DocSection>

<DocSection title="3. Navigate the Dashboard" id="navigate-dashboard">
	<p class="text-text-muted">
		The top navigation bar gives you access to all sections of The Loop:
	</p>
	<ul class="list-disc list-inside text-text-muted space-y-1 ml-2">
		<li>
			<strong class="text-text">Incidents</strong> — list of all open and closed incidents, with
			filtering by severity, status, and team
		</li>
		<li>
			<strong class="text-text">Analytics</strong> — KPI cards (MTTR, MTTD, and more) and trend
			charts for your organization
		</li>
		<li>
			<strong class="text-text">Docs</strong> — this documentation area (you are here)
		</li>
	</ul>
	<p class="text-text-muted">
		Click any incident in the list to open its detail view. The detail view has tabs for Timeline,
		Responders, Action Items, and Attachments.
	</p>
</DocSection>

<DocSection title="4. Invite Your Team" id="invite-team">
	<p class="text-text-muted">
		Ask your administrator to invite teammates from the Administration panel. Invitations are sent
		by email. Each new user gets access to all user-facing sections of The Loop immediately upon
		signing in.
	</p>
	<p class="text-text-muted">
		Once your team is onboarded, assign responders to incidents using the
		<strong class="text-text">Responders</strong> tab on any incident detail page. This ensures
		clear ownership during on-call situations.
	</p>
</DocSection>

<DocSection title="Next Steps" id="next-steps">
	<p class="text-text-muted">Now that you have your first incident, explore these sections:</p>
	<ul class="list-disc list-inside text-text-muted space-y-1 ml-2">
		<li>
			<a href="/docs/incidents/" class="text-accent hover:underline">Incidents</a> — learn all
			fields, status transitions, and the closing checklist
		</li>
		<li>
			<a href="/docs/semgrep/" class="text-accent hover:underline">Semgrep Integration</a> — connect
			your CI pipeline to detect incident patterns at code review time
		</li>
		<li>
			<a href="/docs/analytics/" class="text-accent hover:underline">Analytics</a> — understand
			MTTR, MTTD, and team workload metrics
		</li>
	</ul>
</DocSection>
