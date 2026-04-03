<script lang="ts">
	import type { RootCauseTemplate } from '$lib/types/postmortem';

	let { templates, onSelect }: { templates: RootCauseTemplate[]; onSelect: (template: RootCauseTemplate) => void } =
		$props();

	let selectedId = $state<string | null>(null);
	let showDetails = $state(false);
	let selectedTemplate = $state<RootCauseTemplate | null>(null);

	function handleSelect(template: RootCauseTemplate) {
		selectedId = template.id;
		selectedTemplate = template;
		showDetails = true;
	}

	function confirmSelection() {
		if (selectedTemplate) {
			onSelect(selectedTemplate);
			// Reset after selection
			setTimeout(() => {
				selectedId = null;
				showDetails = false;
				selectedTemplate = null;
			}, 500);
		}
	}

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
</script>

<div class="space-y-4">
	<div>
		<h3 class="mb-3 text-sm font-medium text-text">Select a Root Cause Template</h3>
		<p class="mb-4 text-xs text-text-muted">
			Choose a template to guide your postmortem analysis. You can customize it after selection.
		</p>
	</div>

	{#if showDetails && selectedTemplate}
		<div class="space-y-4 rounded border border-accent bg-accent/5 p-4">
			<div>
				<h4 class="text-sm font-medium text-text">{selectedTemplate.title}</h4>
				<p class="mt-2 text-xs text-text-muted">{selectedTemplate.description_template}</p>
			</div>

			<div class="flex gap-2">
				<span class={`rounded px-2 py-1 text-xs font-medium ${categoryColors[selectedTemplate.category] || 'bg-bg text-text-muted'}`}>
					{selectedTemplate.category.replace(/_/g, ' ')}
				</span>
				<span class={`rounded px-2 py-1 text-xs font-medium ${severityColors[selectedTemplate.severity_default] || 'bg-bg text-text-muted'}`}>
					{selectedTemplate.severity_default}
				</span>
			</div>

			<div class="flex gap-2 pt-2">
				<button
					onclick={confirmSelection}
					class="rounded bg-accent px-3 py-2 text-xs font-medium text-white transition hover:bg-accent/90"
				>
					Use This Template
				</button>
				<button
					onclick={() => {
						showDetails = false;
						selectedId = null;
						selectedTemplate = null;
					}}
					class="rounded border border-border bg-bg px-3 py-2 text-xs font-medium text-text transition hover:bg-bg-elevated"
				>
					Cancel
				</button>
			</div>
		</div>
	{:else}
		<div class="grid gap-3">
			{#each templates as template (template.id)}
				<button
					onclick={() => handleSelect(template)}
					class={`rounded border-2 p-3 text-left transition ${
						selectedId === template.id
							? 'border-accent bg-accent/5'
							: 'border-border bg-bg hover:border-accent/50 hover:bg-bg-elevated'
					}`}
				>
					<div class="flex items-start justify-between">
						<div class="flex-1">
							<h4 class="text-sm font-medium text-text">{template.title}</h4>
							<p class="mt-1 line-clamp-2 text-xs text-text-muted">{template.description_template}</p>
						</div>
						<div class="ml-2 flex gap-1">
							<span class={`rounded px-2 py-0.5 text-xs font-medium ${categoryColors[template.category] || 'bg-bg text-text-muted'}`}>
								{template.category.replace(/_/g, ' ')}
							</span>
							<span class={`rounded px-2 py-0.5 text-xs font-medium ${severityColors[template.severity_default] || 'bg-bg text-text-muted'}`}>
								{template.severity_default}
							</span>
						</div>
					</div>
				</button>
			{/each}
		</div>
	{/if}

	<div class="border-t border-border pt-4">
		<button
			onclick={() => {
				showDetails = false;
				selectedId = null;
				selectedTemplate = null;
			}}
			class="text-xs text-accent hover:underline"
		>
			Skip template and create custom postmortem
		</button>
	</div>
</div>
