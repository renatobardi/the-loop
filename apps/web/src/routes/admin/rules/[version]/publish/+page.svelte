<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { Container, Card, Button } from '$lib/ui';
	import { publishVersion } from '$lib/services/admin';
	import type { RuleData } from '$lib/types/rules';

	const API_BASE = 'https://api.loop.oute.pro';

	let version = $derived(page.params.version ?? '');
	let rules = $state<RuleData[]>([]);
	let loading = $state(true);
	let loadError = $state<string | null>(null);
	let publishing = $state(false);
	let publishError = $state<string | null>(null);
	let publishSuccess = $state(false);

	$effect(() => {
		const v = version;
		fetch(`${API_BASE}/api/v1/rules/${v}`)
			.then((r) => {
				if (!r.ok) throw new Error(`HTTP ${r.status}`);
				return r.json();
			})
			.then((data: { rules: RuleData[] }) => {
				rules = data.rules ?? [];
			})
			.catch((err: unknown) => {
				loadError = err instanceof Error ? err.message : 'Failed to load version';
			})
			.finally(() => {
				loading = false;
			});
	});

	async function handlePublish() {
		publishError = null;
		publishing = true;
		try {
			await publishVersion(version, rules, `Published version ${version}`);
			publishSuccess = true;
			setTimeout(() => goto('/admin/rules/'), 800);
		} catch (err: unknown) {
			publishError = err instanceof Error ? err.message : 'Failed to publish.';
		} finally {
			publishing = false;
		}
	}
</script>

<Container>
	<div class="py-8">
		<div class="mb-6">
			<a href="/admin/rules/{version}/" class="text-sm text-accent hover:underline">
				← Version {version}
			</a>
			<h1 class="text-2xl font-bold text-text mt-1">Publish Version {version}</h1>
			<p class="mt-1 text-sm text-text-muted">
				This will activate this version and make it available to all users.
			</p>
		</div>

		{#if loading}
			<p class="text-sm text-text-muted">Loading…</p>
		{:else if loadError}
			<p class="text-sm text-error" role="alert">{loadError}</p>
		{:else}
			<Card>
				<div class="p-6 space-y-4">
					<div class="flex items-center gap-3">
						<span class="text-4xl font-bold text-accent">{rules.length}</span>
						<span class="text-text-muted">rules will be published</span>
					</div>

					{#if publishError}
						<p class="text-sm text-error" role="alert">{publishError}</p>
					{/if}
					{#if publishSuccess}
						<p class="text-sm text-success">Published! Redirecting…</p>
					{/if}

					<div class="flex gap-3">
						<Button onclick={handlePublish} disabled={publishing || publishSuccess}>
							{publishing ? 'Publishing…' : `Publish version ${version}`}
						</Button>
						<a
							href="/admin/rules/{version}/"
							class="rounded-md border border-border px-4 py-2 text-sm font-semibold text-text hover:border-border-hover transition-colors"
						>
							Cancel
						</a>
					</div>
				</div>
			</Card>
		{/if}
	</div>
</Container>
