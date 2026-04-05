<script lang="ts">
	import type { RuleEffectivenessStats } from '$lib/types/analytics';
	import Badge from '$lib/ui/Badge.svelte';

	let { data }: { data: RuleEffectivenessStats[] } = $props();
</script>

<div class="rounded-lg border border-border bg-bg-surface p-6">
	<h2 class="mb-4 text-lg font-semibold text-text">Rule Effectiveness</h2>

	{#if data.length === 0}
		<p class="text-text-muted">No rules found in this period.</p>
	{:else}
		<div class="overflow-x-auto">
			<table class="w-full text-sm">
				<thead>
					<tr class="border-b border-border">
						<th class="pb-2 text-left font-medium text-text-muted">Rule ID</th>
						<th class="pb-2 text-left font-medium text-text-muted">Incidents</th>
						<th class="pb-2 text-left font-medium text-text-muted">Severity</th>
					</tr>
				</thead>
				<tbody>
					{#each data as rule (rule.rule_id)}
						<tr class="border-b border-border/50">
							<td class="py-2">
								<code class="font-mono text-xs text-text">{rule.rule_id}</code>
							</td>
							<td class="py-2 text-text">{rule.incident_count}</td>
							<td class="py-2">
								{#if rule.avg_severity >= 0.9}
									<Badge variant="error">ERROR</Badge>
								{:else}
									<Badge variant="warning">WARNING</Badge>
								{/if}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
