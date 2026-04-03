<script lang="ts">
	import type { Incident } from '$lib/types/incident';
	import type { Postmortem, RootCauseTemplate, PostmortumCreateRequest } from '$lib/types/postmortem';
	import {
		createPostmortem,
		updatePostmortem,
		listPostmortumTemplates,
		getPostmortemByIncident
	} from '$lib/services/incidents';
	import TemplateSelector from './TemplateSelector.svelte';
	import Button from '$lib/ui/Button.svelte';
	import { user } from '$lib/stores/auth';

	let { incident, postmortem }: { incident: Incident; postmortem?: Postmortem } = $props();

	let templates: RootCauseTemplate[] = $state([]);
	let selectedTemplate: RootCauseTemplate | null = $state(null);
	let templatesLoaded = $state(false);

	let formData = $state<PostmortumCreateRequest>({
		root_cause_category: postmortem?.root_cause_category || 'code_pattern',
		description: postmortem?.description || '',
		team_responsible: postmortem?.team_responsible || '',
		severity_for_rule: postmortem?.severity_for_rule || 'warning',
		suggested_pattern: postmortem?.suggested_pattern,
		related_rule_id: postmortem?.related_rule_id
	});

	let loading = $state(false);
	let submitting = $state(false);
	let error = $state<string | null>(null);
	let success = $state(false);

	// Load templates on mount
	$effect(() => {
		loadTemplates();
	});

	async function loadTemplates() {
		if (templatesLoaded) return;
		try {
			const response = await listPostmortumTemplates();
			templates = response.templates;
			templatesLoaded = true;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load templates';
		}
	}

	function selectTemplate(template: RootCauseTemplate) {
		selectedTemplate = template;
		formData.root_cause_category = template.category;
		formData.description = template.description_template;
		formData.severity_for_rule = template.severity_default;
	}

	async function handleSubmit() {
		if (!formData.description.trim()) {
			error = 'Description is required';
			return;
		}

		if (formData.description.length < 20) {
			error = 'Description must be at least 20 characters';
			return;
		}

		if (formData.description.length > 2000) {
			error = 'Description must not exceed 2000 characters';
			return;
		}

		submitting = true;
		error = null;
		success = false;

		try {
			if (postmortem) {
				await updatePostmortem(postmortem.id, formData);
			} else {
				await createPostmortem(incident.id, formData);
			}
			success = true;
			// Reset form after success
			setTimeout(() => {
				success = false;
			}, 3000);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to save postmortem';
		} finally {
			submitting = false;
		}
	}

	$derived.by(() => {
		const charCount = formData.description.length;
		const minChars = 20;
		const maxChars = 2000;

		if (charCount < minChars) {
			return `${minChars - charCount} more characters required`;
		}
		if (charCount > maxChars) {
			return `${charCount - maxChars} characters over limit`;
		}
		return `${charCount}/${maxChars}`;
	});
</script>

<div class="space-y-6">
	{#if !postmortem}
		<TemplateSelector {templates} onSelect={selectTemplate} />
	{/if}

	<form class="space-y-6" onsubmit|preventDefault={handleSubmit}>
		{#if error}
			<div class="rounded bg-error/10 p-4 text-sm text-error">
				<p class="font-medium">Error</p>
				<p class="mt-1">{error}</p>
			</div>
		{/if}

		{#if success}
			<div class="rounded bg-success/10 p-4 text-sm text-success">
				<p class="font-medium">✓ Postmortem saved successfully</p>
			</div>
		{/if}

		<div>
			<label for="category" class="mb-2 block text-sm font-medium text-text">
				Root Cause Category
			</label>
			<select
				id="category"
				bind:value={formData.root_cause_category}
				class="w-full rounded border border-border bg-bg px-3 py-2 text-sm text-text transition hover:border-accent focus:border-accent focus:outline-none"
			>
				<option value="code_pattern">Code Pattern</option>
				<option value="infrastructure">Infrastructure</option>
				<option value="process_breakdown">Process Breakdown</option>
				<option value="third_party">Third Party</option>
				<option value="unknown">Unknown</option>
			</select>
		</div>

		<div>
			<label for="description" class="mb-2 block text-sm font-medium text-text">
				Root Cause Analysis
			</label>
			<textarea
				id="description"
				bind:value={formData.description}
				placeholder="Describe what caused this incident and why..."
				rows="8"
				class="w-full rounded border border-border bg-bg px-3 py-2 text-sm text-text transition hover:border-accent focus:border-accent focus:outline-none"
			/>
			<div class="mt-1 flex justify-between text-xs text-text-muted">
				<span />
				<span id="charCount">
					{formData.description.length}/2000 characters
				</span>
			</div>
		</div>

		<div class="grid gap-4 md:grid-cols-2">
			<div>
				<label for="team" class="mb-2 block text-sm font-medium text-text">
					Team Responsible
				</label>
				<input
					id="team"
					type="text"
					bind:value={formData.team_responsible}
					placeholder="e.g., backend, frontend, devops"
					class="w-full rounded border border-border bg-bg px-3 py-2 text-sm text-text transition hover:border-accent focus:border-accent focus:outline-none"
				/>
			</div>

			<div>
				<label for="severity" class="mb-2 block text-sm font-medium text-text">
					Prevention Rule Severity
				</label>
				<select
					id="severity"
					bind:value={formData.severity_for_rule}
					class="w-full rounded border border-border bg-bg px-3 py-2 text-sm text-text transition hover:border-accent focus:border-accent focus:outline-none"
				>
					<option value="error">Error (blocks merge)</option>
					<option value="warning">Warning (advisory)</option>
				</select>
			</div>
		</div>

		<div>
			<label for="pattern" class="mb-2 block text-sm font-medium text-text">
				Suggested Detection Pattern (optional)
			</label>
			<input
				id="pattern"
				type="text"
				bind:value={formData.suggested_pattern}
				placeholder="e.g., regex or semgrep pattern to detect this issue"
				class="w-full rounded border border-border bg-bg px-3 py-2 text-sm text-text transition hover:border-accent focus:border-accent focus:outline-none"
			/>
		</div>

		<div>
			<label for="rule-id" class="mb-2 block text-sm font-medium text-text">
				Related Rule ID (optional)
			</label>
			<input
				id="rule-id"
				type="text"
				bind:value={formData.related_rule_id}
				placeholder="e.g., injection-001"
				class="w-full rounded border border-border bg-bg px-3 py-2 text-sm text-text transition hover:border-accent focus:border-accent focus:outline-none"
			/>
		</div>

		<div class="flex gap-2">
			<Button
				type="submit"
				disabled={submitting || loading || formData.description.length < 20 || formData.description.length > 2000}
			>
				{submitting ? 'Saving...' : postmortem ? 'Update Postmortem' : 'Create Postmortem'}
			</Button>
		</div>
	</form>
</div>
