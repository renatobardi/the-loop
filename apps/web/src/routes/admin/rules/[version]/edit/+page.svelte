<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { Container, Card, Input, Button } from '$lib/ui';
	import { editRule } from '$lib/services/admin';

	let version = $derived(page.params.version ?? '');
	let ruleId = $derived(page.url.searchParams.get('rule_id') ?? '');

	let message = $state('');
	let severity = $state('ERROR');
	let pattern = $state('');
	let languages = $state('python');
	let saving = $state(false);
	let saveError = $state<string | null>(null);
	let saveSuccess = $state(false);

	async function handleSave() {
		saveError = null;
		saveSuccess = false;
		if (!message.trim() || !pattern.trim()) {
			saveError = 'Message and pattern are required.';
			return;
		}
		saving = true;
		try {
			await editRule(version, ruleId, {
				message: message.trim(),
				severity,
				pattern: pattern.trim(),
				languages: languages
					.split(',')
					.map((l) => l.trim())
					.filter(Boolean)
			});
			saveSuccess = true;
			setTimeout(() => goto(`/admin/rules/${version}/`), 800);
		} catch (err: unknown) {
			saveError = err instanceof Error ? err.message : 'Failed to save rule.';
		} finally {
			saving = false;
		}
	}
</script>

<Container>
	<div class="py-8">
		<div class="mb-6">
			<a href="/admin/rules/{version}/" class="text-sm text-accent hover:underline">
				← Version {version}
			</a>
			<h1 class="text-2xl font-bold text-text mt-1">Edit Rule</h1>
			<p class="mt-1 font-mono text-sm text-text-muted">{ruleId}</p>
		</div>

		<Card>
			<div class="p-4 max-w-lg space-y-4">
				<div>
					<label for="rule-id" class="mb-1 block text-sm font-medium text-text">Rule ID</label>
					<p id="rule-id" class="font-mono text-sm text-text-muted">{ruleId}</p>
				</div>

				<div>
					<label for="message" class="mb-1 block text-sm font-medium text-text">Message</label>
					<Input id="message" bind:value={message} placeholder="Human-readable finding message" />
				</div>

				<div>
					<label for="severity" class="mb-1 block text-sm font-medium text-text">Severity</label>
					<select
						id="severity"
						bind:value={severity}
						class="w-full rounded-md border border-border bg-bg-elevated px-3 py-2 text-sm text-text focus:border-accent focus:outline-none"
					>
						<option value="ERROR">ERROR (blocks merge)</option>
						<option value="WARNING">WARNING (advisory)</option>
					</select>
				</div>

				<div>
					<label for="pattern" class="mb-1 block text-sm font-medium text-text">Pattern</label>
					<textarea
						id="pattern"
						bind:value={pattern}
						rows={4}
						placeholder="Semgrep pattern or regex"
						class="w-full rounded-md border border-border bg-bg-elevated px-3 py-2 text-sm font-mono text-text placeholder:text-text-muted focus:border-accent focus:outline-none resize-y"
					></textarea>
				</div>

				<div>
					<label for="languages" class="mb-1 block text-sm font-medium text-text">
						Languages (comma-separated)
					</label>
					<Input
						id="languages"
						bind:value={languages}
						placeholder="python, javascript"
					/>
				</div>

				{#if saveError}
					<p class="text-sm text-error" role="alert">{saveError}</p>
				{/if}
				{#if saveSuccess}
					<p class="text-sm text-success">Rule saved. Redirecting…</p>
				{/if}

				<Button onclick={handleSave} disabled={saving}>
					{saving ? 'Saving…' : 'Save rule'}
				</Button>
			</div>
		</Card>
	</div>
</Container>
