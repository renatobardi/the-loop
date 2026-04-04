<script lang="ts">
	import { Container, Card, Button, Badge } from '$lib/ui';
	import { listVersions, createVersion } from '$lib/services/admin';
	import type { VersionSummary } from '$lib/types/rules';

	let versions = $state<VersionSummary[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let creating = $state(false);
	let newVersion = $state('');
	let createError = $state<string | null>(null);

	$effect(() => {
		loadVersions();
	});

	async function loadVersions() {
		loading = true;
		error = null;
		try {
			const data = await listVersions();
			versions = data.versions;
		} catch (err: unknown) {
			error = err instanceof Error ? err.message : 'Failed to load versions';
		} finally {
			loading = false;
		}
	}

	async function handleCreateVersion() {
		createError = null;
		if (!newVersion.trim()) {
			createError = 'Version is required (e.g. 0.3.0)';
			return;
		}
		creating = true;
		try {
			await createVersion(newVersion.trim());
			newVersion = '';
			await loadVersions();
		} catch (err: unknown) {
			createError = err instanceof Error ? err.message : 'Failed to create version';
		} finally {
			creating = false;
		}
	}

	function badgeVariant(status: string): 'success' | 'error' | 'default' {
		if (status === 'active') return 'success';
		if (status === 'deprecated') return 'error';
		return 'default';
	}
</script>

<Container>
	<div class="py-8">
		<div class="mb-6 flex items-center justify-between">
			<div>
				<h1 class="text-2xl font-bold text-text">Rule Versions</h1>
				<p class="mt-1 text-sm text-text-muted">Manage published Semgrep rule versions</p>
			</div>
		</div>

		<!-- New version form -->
		<Card>
			<div class="p-4">
				<p class="text-sm font-medium text-text mb-2">Create New Version</p>
				<div class="flex gap-2 items-start">
					<input
						type="text"
						bind:value={newVersion}
						placeholder="e.g. 0.3.0"
						class="flex-1 rounded-md border border-border bg-bg-elevated px-3 py-2 text-sm text-text placeholder:text-text-muted focus:border-accent focus:outline-none"
					/>
					<Button onclick={handleCreateVersion} disabled={creating}>
						{creating ? 'Creating…' : 'Create draft'}
					</Button>
				</div>
				{#if createError}
					<p class="text-sm text-error mt-1" role="alert">{createError}</p>
				{/if}
			</div>
		</Card>

		<div class="mt-6 space-y-2">
			{#if loading}
				<p class="text-sm text-text-muted">Loading versions…</p>
			{:else if error}
				<p class="text-sm text-error" role="alert">{error}</p>
			{:else if versions.length === 0}
				<p class="text-sm text-text-muted">No versions published yet.</p>
			{:else}
				{#each versions as v (v.version)}
					<Card>
						<div class="p-4 flex items-center justify-between">
							<div class="flex items-center gap-3">
								<span class="font-mono font-semibold text-text">{v.version}</span>
								<Badge variant={badgeVariant(v.status)}>{v.status}</Badge>
								<span class="text-xs text-text-muted">{v.rules_count} rules</span>
							</div>
							<a
								href="/admin/rules/{v.version}/"
								class="text-sm text-accent hover:underline"
							>
								View rules
							</a>
						</div>
					</Card>
				{/each}
			{/if}
		</div>
	</div>
</Container>
