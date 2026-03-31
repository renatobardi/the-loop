<script lang="ts">
	import { Button, Input } from '$lib/ui';
	import { CATEGORIES, SEVERITIES } from '$lib/types/incident';
	import type { IncidentCreate } from '$lib/types/incident';
	import * as m from '$lib/paraglide/messages.js';

	let {
		initial = undefined,
		version = undefined,
		onsubmit
	}: {
		initial?: IncidentCreate;
		version?: number;
		// eslint-disable-next-line no-unused-vars
		onsubmit: (data: IncidentCreate & { version?: number }) => Promise<void>;
	} = $props();

	let title = $state(initial?.title ?? '');
	let incidentDate = $state(initial?.date ?? '');
	let source_url = $state(initial?.source_url ?? '');
	let organization = $state(initial?.organization ?? '');
	let category = $state(initial?.category ?? 'injection');
	let subcategory = $state(initial?.subcategory ?? '');
	let failure_mode = $state(initial?.failure_mode ?? '');
	let severity = $state(initial?.severity ?? 'medium');
	let affected_languages = $state(initial?.affected_languages?.join(', ') ?? '');
	let anti_pattern = $state(initial?.anti_pattern ?? '');
	let code_example = $state(initial?.code_example ?? '');
	let remediation = $state(initial?.remediation ?? '');
	let static_rule_possible = $state(initial?.static_rule_possible ?? false);
	let semgrep_rule_id = $state(initial?.semgrep_rule_id ?? '');
	let tags = $state(initial?.tags?.join(', ') ?? '');

	let status: 'idle' | 'submitting' | 'success' | 'error' = $state('idle');
	let errorMessage = $state('');

	async function handleSubmit(e: Event) {
		e.preventDefault();
		status = 'submitting';
		errorMessage = '';

		const formData: IncidentCreate & { version?: number } = {
			title,
			category: category as IncidentCreate['category'],
			severity: severity as IncidentCreate['severity'],
			anti_pattern,
			remediation,
			date: incidentDate || null,
			source_url: source_url || null,
			organization: organization || null,
			subcategory: subcategory || null,
			failure_mode: failure_mode || null,
			affected_languages: affected_languages
				? affected_languages.split(',').map((s) => s.trim()).filter(Boolean)
				: [],
			code_example: code_example || null,
			static_rule_possible,
			semgrep_rule_id: semgrep_rule_id || null,
			tags: tags ? tags.split(',').map((s) => s.trim()).filter(Boolean) : []
		};
		if (version !== undefined) {
			formData.version = version;
		}

		try {
			await onsubmit(formData);
			status = 'success';
		} catch (err) {
			status = 'error';
			errorMessage = err instanceof Error ? err.message : m.incident_error();
		}
	}
</script>

<form onsubmit={handleSubmit} class="space-y-6">
	<div class="grid gap-4 md:grid-cols-2">
		<div class="md:col-span-2">
			<label for="title" class="block text-sm font-medium text-text">{m.incident_field_title()} *</label>
			<Input id="title" bind:value={title} required maxlength={500} />
		</div>

		<div>
			<label for="category" class="block text-sm font-medium text-text">{m.incident_field_category()} *</label>
			<select id="category" bind:value={category} class="w-full rounded-md border border-border bg-bg-surface px-3 py-2 text-text">
				{#each CATEGORIES as cat (cat)}
					<option value={cat}>{cat}</option>
				{/each}
			</select>
		</div>

		<div>
			<label for="severity" class="block text-sm font-medium text-text">{m.incident_field_severity()} *</label>
			<select id="severity" bind:value={severity} class="w-full rounded-md border border-border bg-bg-surface px-3 py-2 text-text">
				{#each SEVERITIES as sev (sev)}
					<option value={sev}>{sev}</option>
				{/each}
			</select>
		</div>

		<div class="md:col-span-2">
			<label for="anti_pattern" class="block text-sm font-medium text-text">{m.incident_field_anti_pattern()} *</label>
			<textarea id="anti_pattern" bind:value={anti_pattern} required rows={3} class="w-full rounded-md border border-border bg-bg-surface px-3 py-2 text-text"></textarea>
		</div>

		<div class="md:col-span-2">
			<label for="remediation" class="block text-sm font-medium text-text">{m.incident_field_remediation()} *</label>
			<textarea id="remediation" bind:value={remediation} required rows={3} class="w-full rounded-md border border-border bg-bg-surface px-3 py-2 text-text"></textarea>
		</div>

		<div>
			<label for="incidentDate" class="block text-sm font-medium text-text-muted">{m.incident_field_date()}</label>
			<input id="incidentDate" type="date" bind:value={incidentDate} class="w-full rounded-md border border-border bg-bg-surface px-3 py-2 text-text" />
		</div>

		<div>
			<label for="organization" class="block text-sm font-medium text-text-muted">{m.incident_field_organization()}</label>
			<Input id="organization" bind:value={organization} maxlength={255} />
		</div>

		<div class="md:col-span-2">
			<label for="source_url" class="block text-sm font-medium text-text-muted">{m.incident_field_source_url()}</label>
			<input id="source_url" type="url" bind:value={source_url} maxlength={2048} class="w-full rounded-md border border-border bg-bg-surface px-3 py-2 text-text" />
		</div>

		<div>
			<label for="subcategory" class="block text-sm font-medium text-text-muted">{m.incident_field_subcategory()}</label>
			<Input id="subcategory" bind:value={subcategory} maxlength={100} />
		</div>

		<div>
			<label for="semgrep_rule_id" class="block text-sm font-medium text-text-muted">{m.incident_field_semgrep_rule_id()}</label>
			<Input id="semgrep_rule_id" bind:value={semgrep_rule_id} maxlength={50} placeholder="category-NNN" />
		</div>

		<div class="md:col-span-2">
			<label for="failure_mode" class="block text-sm font-medium text-text-muted">{m.incident_field_failure_mode()}</label>
			<textarea id="failure_mode" bind:value={failure_mode} rows={2} class="w-full rounded-md border border-border bg-bg-surface px-3 py-2 text-text"></textarea>
		</div>

		<div class="md:col-span-2">
			<label for="code_example" class="block text-sm font-medium text-text-muted">{m.incident_field_code_example()}</label>
			<textarea id="code_example" bind:value={code_example} rows={4} class="w-full rounded-md border border-border bg-bg-surface px-3 py-2 font-mono text-sm text-text"></textarea>
		</div>

		<div>
			<label for="affected_languages" class="block text-sm font-medium text-text-muted">{m.incident_field_affected_languages()}</label>
			<Input id="affected_languages" bind:value={affected_languages} placeholder="python, javascript" />
		</div>

		<div>
			<label for="tags" class="block text-sm font-medium text-text-muted">{m.incident_field_tags()}</label>
			<Input id="tags" bind:value={tags} placeholder="regex, performance" />
		</div>

		<div class="flex items-center gap-2">
			<input id="static_rule_possible" type="checkbox" bind:checked={static_rule_possible} class="rounded border-border" />
			<label for="static_rule_possible" class="text-sm text-text-muted">{m.incident_field_static_rule_possible()}</label>
		</div>
	</div>

	{#if status === 'error'}
		<p class="text-sm text-error">{errorMessage}</p>
	{/if}
	{#if status === 'success'}
		<p class="text-sm text-success">{m.incident_success()}</p>
	{/if}

	<Button type="submit" disabled={status === 'submitting'}>
		{status === 'submitting' ? m.incident_submitting() : m.incident_submit()}
	</Button>
</form>
