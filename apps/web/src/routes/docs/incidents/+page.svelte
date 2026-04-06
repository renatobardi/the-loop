<script lang="ts">
	import DocSection from '$lib/components/docs/DocSection.svelte';
</script>

<svelte:head>
	<title>Incidents — The Loop Docs</title>
	<meta
		name="description"
		content="Learn the incident lifecycle, all fields, status transitions, responders, action items, and the required fields checklist for closing an incident."
	/>
</svelte:head>

<h1 class="text-3xl font-bold text-text mb-2">Incidents</h1>
<p class="text-text-muted mb-8">
	Incidents are the core record in The Loop. They capture what happened, who responded, and what
	actions were taken — from detection to closure.
</p>

<DocSection title="Lifecycle" id="lifecycle">
	<p class="text-text-muted mb-4">
		Every incident moves through a defined set of statuses:
	</p>
	<div class="space-y-3">
		<div class="flex items-start gap-3">
			<span class="mt-0.5 inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-bg-elevated text-accent border border-border shrink-0">open</span>
			<p class="text-text-muted text-sm">Incident created, not yet being actively worked. This is the starting status when the incident is first logged.</p>
		</div>
		<div class="flex items-start gap-3">
			<span class="mt-0.5 inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-bg-elevated text-warning border border-border shrink-0">investigating</span>
			<p class="text-text-muted text-sm">A responder is actively investigating. Root cause is not yet identified. Set this status when you begin looking into the incident.</p>
		</div>
		<div class="flex items-start gap-3">
			<span class="mt-0.5 inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-bg-elevated text-success border border-border shrink-0">resolved</span>
			<p class="text-text-muted text-sm">The immediate impact has been mitigated. The system is back to normal operation but the incident record may still need to be completed.</p>
		</div>
		<div class="flex items-start gap-3">
			<span class="mt-0.5 inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-bg-elevated text-text-muted border border-border shrink-0">closed</span>
			<p class="text-text-muted text-sm">All required fields are filled, the postmortem is written (if applicable), and the incident is finalized. Closed incidents appear in analytics.</p>
		</div>
	</div>
	<p class="text-text-muted mt-4">
		Status transitions are manual — The Loop does not auto-advance statuses. Move the incident
		forward as your team's process dictates.
	</p>
</DocSection>

<DocSection title="Fields" id="fields">
	<div class="space-y-4">
		<div>
			<div class="font-semibold text-text text-sm mb-1">Title <span class="text-error text-xs">required</span></div>
			<p class="text-text-muted text-sm">A short, descriptive summary of what happened. Keep it specific enough to identify the incident at a glance. Maximum 200 characters.</p>
		</div>
		<div>
			<div class="font-semibold text-text text-sm mb-1">Severity <span class="text-error text-xs">required</span></div>
			<p class="text-text-muted text-sm">Impact level: <code class="text-accent">critical</code> (service down), <code class="text-accent">high</code> (major feature impacted), <code class="text-accent">medium</code> (degraded experience), <code class="text-accent">low</code> (minimal user impact).</p>
		</div>
		<div>
			<div class="font-semibold text-text text-sm mb-1">Category <span class="text-error text-xs">required</span></div>
			<p class="text-text-muted text-sm">Root cause category: <code class="text-accent">code_pattern</code>, <code class="text-accent">infrastructure</code>, <code class="text-accent">process_breakdown</code>, <code class="text-accent">third_party</code>, or <code class="text-accent">unknown</code>. Used by analytics and scanner rule correlation.</p>
		</div>
		<div>
			<div class="font-semibold text-text text-sm mb-1">Team <span class="text-error text-xs">required</span></div>
			<p class="text-text-muted text-sm">The team responsible for resolution. Used to filter analytics by team workload and MTTR.</p>
		</div>
		<div>
			<div class="font-semibold text-text text-sm mb-1">Status</div>
			<p class="text-text-muted text-sm">Current lifecycle state (see Lifecycle above). Set manually by your team.</p>
		</div>
		<div>
			<div class="font-semibold text-text text-sm mb-1">Description</div>
			<p class="text-text-muted text-sm">Free-text narrative of the incident — symptoms, impact, and timeline. Supports plain text.</p>
		</div>
		<div>
			<div class="font-semibold text-text text-sm mb-1">Started At / Resolved At</div>
			<p class="text-text-muted text-sm">Optional timestamps. When set, these enable MTTD and MTTR calculation in analytics.</p>
		</div>
	</div>
</DocSection>

<DocSection title="Responders" id="responders">
	<p class="text-text-muted">
		Use the <strong class="text-text">Responders</strong> tab to assign team members to the
		incident. Responders receive notifications and appear in the incident record. You can add or
		remove responders at any point during the incident lifecycle.
	</p>
	<p class="text-text-muted">
		At least one responder should be assigned before moving to
		<code class="text-accent">investigating</code> status to establish clear ownership.
	</p>
</DocSection>

<DocSection title="Action Items" id="action-items">
	<p class="text-text-muted">
		Action items are discrete follow-up tasks created during or after an incident. Each item has a
		description, an optional assignee, and a completion state. Use action items to track:
	</p>
	<ul class="list-disc list-inside text-text-muted space-y-1 ml-2">
		<li>Immediate mitigation steps taken during the incident</li>
		<li>Post-incident remediation tasks (e.g., add monitoring, fix the root cause)</li>
		<li>Postmortem action items that need tracking after the write-up</li>
	</ul>
</DocSection>

<DocSection title="Timeline Events" id="timeline">
	<p class="text-text-muted">
		The Timeline tab shows a chronological log of events during the incident. Add entries manually
		to record key moments: when the alert fired, when a deploy was rolled back, when the root cause
		was identified. The timeline is preserved permanently and is visible in the postmortem.
	</p>
</DocSection>

<DocSection title="Attachments" id="attachments">
	<p class="text-text-muted">
		Attach screenshots, log excerpts, graphs, or runbooks to the incident record. Attachments
		appear in the Attachments tab and are referenced in the postmortem automatically.
	</p>
</DocSection>

<DocSection title="Closing Checklist" id="closing-checklist">
	<p class="text-text-muted mb-4">
		Before moving an incident to <code class="text-accent">closed</code> status, confirm all of
		the following are complete:
	</p>
	<ul class="space-y-2">
		<li class="flex items-start gap-2 text-sm">
			<span class="text-error mt-0.5" aria-hidden="true">●</span>
			<span class="text-text"><strong>Title</strong> accurately describes what happened</span>
		</li>
		<li class="flex items-start gap-2 text-sm">
			<span class="text-error mt-0.5" aria-hidden="true">●</span>
			<span class="text-text"><strong>Severity</strong> reflects the actual impact (not estimated)</span>
		</li>
		<li class="flex items-start gap-2 text-sm">
			<span class="text-error mt-0.5" aria-hidden="true">●</span>
			<span class="text-text"><strong>Category</strong> is set to the confirmed root cause category</span>
		</li>
		<li class="flex items-start gap-2 text-sm">
			<span class="text-error mt-0.5" aria-hidden="true">●</span>
			<span class="text-text"><strong>Team</strong> is set to the responsible team</span>
		</li>
		<li class="flex items-start gap-2 text-sm">
			<span class="text-error mt-0.5" aria-hidden="true">●</span>
			<span class="text-text"><strong>Resolved At</strong> timestamp is set (enables MTTR calculation)</span>
		</li>
		<li class="flex items-start gap-2 text-sm">
			<span class="text-warning mt-0.5" aria-hidden="true">●</span>
			<span class="text-text-muted"><strong>Postmortem</strong> is written for severity critical/high (strongly recommended)</span>
		</li>
		<li class="flex items-start gap-2 text-sm">
			<span class="text-warning mt-0.5" aria-hidden="true">●</span>
			<span class="text-text-muted"><strong>Action items</strong> are created for all follow-up work</span>
		</li>
	</ul>
	<p class="text-text-muted mt-4 text-sm">
		Red items are required. Orange items are strongly recommended for data quality.
	</p>
</DocSection>
