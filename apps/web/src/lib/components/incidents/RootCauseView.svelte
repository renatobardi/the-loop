<script lang="ts">
	import type { Postmortem } from '$lib/types/postmortem';

	let { postmortem }: { postmortem: Postmortem } = $props();

	const categoryLabels: Record<string, string> = {
		code_pattern: 'Code Pattern',
		infrastructure: 'Infrastructure',
		process_breakdown: 'Process Breakdown',
		third_party: 'Third Party',
		unknown: 'Unknown'
	};

	const categoryColors: Record<string, string> = {
		code_pattern: 'bg-accent/10 text-accent',
		infrastructure: 'bg-warning/10 text-warning',
		process_breakdown: 'bg-info/10 text-info',
		third_party: 'bg-secondary/10 text-secondary',
		unknown: 'bg-muted/10 text-muted'
	};

	const severityColors: Record<string, string> = {
		error: 'bg-error/10 text-error',
		warning: 'bg-warning/10 text-warning'
	};

	function formatDate(dateStr: string): string {
		return new Date(dateStr).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<div class="space-y-6">
	<div class="rounded border border-border bg-bg-elevated p-4">
		<div class="mb-4 flex items-center gap-2">
			<span class="rounded bg-success/20 px-2 py-1 text-xs font-medium text-success">
				✓ Locked
			</span>
			<span class="text-xs text-text-muted">This postmortem cannot be edited after incident closure.</span>
		</div>

		<div class="space-y-4">
			<div>
				<span class="text-xs text-text-muted">Root Cause Category</span>
				<div class="mt-1">
					<span
						class={`inline-block rounded px-2 py-1 text-xs font-medium ${categoryColors[postmortem.root_cause_category] || 'bg-bg text-text-muted'}`}
					>
						{categoryLabels[postmortem.root_cause_category] || postmortem.root_cause_category}
					</span>
				</div>
			</div>

			<div>
				<span class="text-xs text-text-muted">Team Responsible</span>
				<p class="mt-1 text-sm font-medium text-text">{postmortem.team_responsible}</p>
			</div>

			<div>
				<span class="text-xs text-text-muted">Prevention Rule Severity</span>
				<div class="mt-1">
					<span
						class={`inline-block rounded px-2 py-1 text-xs font-medium ${severityColors[postmortem.severity_for_rule] || 'bg-bg text-text-muted'}`}
					>
						{postmortem.severity_for_rule}
					</span>
				</div>
			</div>
		</div>
	</div>

	<div>
		<h3 class="mb-2 text-sm font-medium text-text">Root Cause Analysis</h3>
		<div class="rounded border border-border bg-bg-elevated p-4">
			<p class="whitespace-pre-wrap text-sm text-text">{postmortem.description}</p>
		</div>
	</div>

	{#if postmortem.suggested_pattern}
		<div>
			<h3 class="mb-2 text-sm font-medium text-text">Detection Pattern</h3>
			<div class="rounded border border-border bg-bg-elevated p-3">
				<code class="text-xs text-text-muted">{postmortem.suggested_pattern}</code>
			</div>
		</div>
	{/if}

	{#if postmortem.related_rule_id}
		<div>
			<h3 class="mb-2 text-sm font-medium text-text">Related Rule</h3>
			<p class="rounded border border-border bg-bg-elevated p-3 text-xs font-mono text-accent">
				{postmortem.related_rule_id}
			</p>
		</div>
	{/if}

	<div class="border-t border-border pt-4">
		<div class="grid gap-4 text-xs text-text-muted sm:grid-cols-2">
			<div>
				<span class="block">Created by</span>
				<p class="mt-1 font-mono text-text">{postmortem.created_by.substring(0, 8)}...</p>
			</div>
			<div>
				<span class="block">Created at</span>
				<p class="mt-1 text-text">{formatDate(postmortem.created_at)}</p>
			</div>
			{#if postmortem.updated_by && postmortem.updated_at}
				<div>
					<span class="block">Last updated by</span>
					<p class="mt-1 font-mono text-text">{postmortem.updated_by.substring(0, 8)}...</p>
				</div>
				<div>
					<span class="block">Last updated at</span>
					<p class="mt-1 text-text">{formatDate(postmortem.updated_at)}</p>
				</div>
			{/if}
		</div>
	</div>
</div>
