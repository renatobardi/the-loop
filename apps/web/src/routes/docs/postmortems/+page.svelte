<script lang="ts">
	import DocSection from '$lib/components/docs/DocSection.svelte';
</script>

<svelte:head>
	<title>Postmortems — The Loop Docs</title>
	<meta
		name="description"
		content="Learn when to write a postmortem, which template to choose, how fields work, and what locking means."
	/>
</svelte:head>

<h1 class="text-3xl font-bold text-text mb-2">Postmortems</h1>
<p class="text-text-muted mb-8">
	A postmortem captures the full story of an incident: what happened, why it happened, and what
	changes will prevent recurrence. The Loop links each postmortem to its incident automatically.
</p>

<DocSection title="When to Write a Postmortem" id="when">
	<p class="text-text-muted">
		Write a postmortem for every <code class="text-accent">critical</code> or
		<code class="text-accent">high</code> severity incident. For
		<code class="text-accent">medium</code> incidents, use judgment — write one if there are
		systemic lessons worth capturing. <code class="text-accent">low</code> severity incidents
		typically do not require a postmortem.
	</p>
	<p class="text-text-muted">
		The postmortem should be started within 24–48 hours of resolution while details are fresh. It
		does not need to be complete immediately — use the draft state to capture initial notes.
	</p>
</DocSection>

<DocSection title="Template Catalog" id="templates">
	<p class="text-text-muted mb-4">
		Choose the template that best matches your incident type:
	</p>
	<div class="space-y-4">
		<div class="p-4 rounded-lg bg-bg-surface border border-border">
			<div class="font-semibold text-text mb-1">5 Whys</div>
			<p class="text-text-muted text-sm">
				Ask "why?" five times to drill from symptom to root cause. Best for operational incidents
				with a clear causal chain (deployment failure, config change, dependency outage).
			</p>
		</div>
		<div class="p-4 rounded-lg bg-bg-surface border border-border">
			<div class="font-semibold text-text mb-1">Fishbone (Ishikawa)</div>
			<p class="text-text-muted text-sm">
				Organizes contributing factors into categories (People, Process, Tools, Environment). Best
				for complex incidents with multiple concurrent contributing factors.
			</p>
		</div>
		<div class="p-4 rounded-lg bg-bg-surface border border-border">
			<div class="font-semibold text-text mb-1">Timeline</div>
			<p class="text-text-muted text-sm">
				A chronological narrative of the incident. Best for long-running or multi-team incidents
				where the sequence of events is the primary analysis vehicle.
			</p>
		</div>
		<div class="p-4 rounded-lg bg-bg-surface border border-border">
			<div class="font-semibold text-text mb-1">Pre/Mortem</div>
			<p class="text-text-muted text-sm">
				Analyzes what you would have needed to know <em>before</em> the incident to prevent it. Best
				when the incident reveals a systemic gap in your processes or monitoring.
			</p>
		</div>
		<div class="p-4 rounded-lg bg-bg-surface border border-border">
			<div class="font-semibold text-text mb-1">OODA Loop</div>
			<p class="text-text-muted text-sm">
				Structures analysis around Observe, Orient, Decide, Act cycles. Best for incidents that
				exposed gaps in how your team detects, assesses, and responds to signals.
			</p>
		</div>
		<div class="p-4 rounded-lg bg-bg-surface border border-border">
			<div class="font-semibold text-text mb-1">PDCA (Plan-Do-Check-Act)</div>
			<p class="text-text-muted text-sm">
				Focuses on continuous improvement cycles. Best when the incident is a recurrence of a
				previously addressed issue, indicating a fix that did not hold.
			</p>
		</div>
	</div>
</DocSection>

<DocSection title="Fields" id="fields">
	<div class="space-y-3 text-sm">
		<div>
			<span class="font-semibold text-text">Title</span>
			<span class="text-text-muted"> — short name for the postmortem, often the same as the incident title.</span>
		</div>
		<div>
			<span class="font-semibold text-text">Template</span>
			<span class="text-text-muted"> — selected from the catalog above. Determines the section structure of the postmortem document.</span>
		</div>
		<div>
			<span class="font-semibold text-text">Root Cause Category</span>
			<span class="text-text-muted"> — confirmed root cause category. Pre-filled from the incident if set.</span>
		</div>
		<div>
			<span class="font-semibold text-text">Summary</span>
			<span class="text-text-muted"> — a concise paragraph describing what happened, the impact, and the resolution. This is the executive summary of the postmortem.</span>
		</div>
		<div>
			<span class="font-semibold text-text">Content</span>
			<span class="text-text-muted"> — the full postmortem body, structured by the chosen template. Use this section for the deep analysis.</span>
		</div>
		<div>
			<span class="font-semibold text-text">Action Items</span>
			<span class="text-text-muted"> — follow-up tasks referenced from the incident. Action items created in the incident appear here automatically.</span>
		</div>
	</div>
</DocSection>

<DocSection title="Locking" id="locking">
	<div class="p-4 rounded-lg bg-error/10 border border-error/30 mb-4">
		<p class="text-sm text-text font-semibold mb-1">⚠️ Locking is irreversible</p>
		<p class="text-sm text-text-muted">
			Once a postmortem is locked, it cannot be edited. This action cannot be undone — not by you,
			not by an administrator.
		</p>
	</div>
	<p class="text-text-muted">
		Locking a postmortem freezes it as the official record of the incident. Use locking when:
	</p>
	<ul class="list-disc list-inside text-text-muted space-y-1 ml-2">
		<li>The postmortem has been reviewed and approved by the team</li>
		<li>Action items have been recorded and assigned</li>
		<li>The document is ready to be shared with stakeholders</li>
	</ul>
	<p class="text-text-muted">
		Do not lock a postmortem while action items are still being defined. Lock only after the
		retrospective meeting is complete and the document reflects the final agreed-upon analysis.
	</p>
</DocSection>

<DocSection title="AI Summary" id="ai-summary">
	<p class="text-text-muted">
		The <strong class="text-text">Summary</strong> field can be populated automatically using AI
		analysis of the incident timeline, responder notes, and template content. The AI summary is a
		starting point — review and edit it before locking the postmortem.
	</p>
	<p class="text-text-muted">
		AI summaries are generated on demand. They do not replace human review of the root cause and
		action items.
	</p>
</DocSection>
