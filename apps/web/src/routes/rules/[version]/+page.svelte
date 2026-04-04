<script lang="ts">
	import { Container, Section } from '$lib/ui';
	import RuleCard from '$lib/components/rules/RuleCard.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const errors = $derived(
		data.rules.filter((r: { severity: string }) => r.severity === 'ERROR')
	);
	const warnings = $derived(
		data.rules.filter((r: { severity: string }) => r.severity === 'WARNING')
	);
</script>

<svelte:head>
	<title>The Loop — Rules v{data.version}</title>
	<meta
		name="description"
		content="Security and quality rules for version {data.version} enforced by The Loop."
	/>
</svelte:head>

<main id="main-content">
	<Section>
		<Container>
			<div class="mb-8">
				<a href="/rules/" class="text-sm text-text-muted transition-colors hover:text-text">
					&larr; All versions
				</a>
				<h1 class="mt-2 text-3xl font-bold text-text">Rules v{data.version}</h1>
				<p class="mt-1 text-text-muted">{data.rulesCount} rules</p>
			</div>

			{#if data.rules.length === 0}
				<div class="flex flex-col items-center justify-center py-24 text-center">
					<p class="text-xl font-semibold text-text">No rules in this version.</p>
					<p class="mt-2 text-text-muted">
						<a href="/rules/" class="text-accent hover:underline">Browse latest version &rarr;</a>
					</p>
				</div>
			{:else}
				{#if errors.length > 0}
					<div class="mb-8">
						<h2 class="mb-3 text-lg font-semibold text-error">Critical ({errors.length})</h2>
						<div class="flex flex-col gap-3">
							{#each errors as rule (rule.id)}
								<RuleCard {rule} />
							{/each}
						</div>
					</div>
				{/if}

				{#if warnings.length > 0}
					<div>
						<h2 class="mb-3 text-lg font-semibold text-warning">Warnings ({warnings.length})</h2>
						<div class="flex flex-col gap-3">
							{#each warnings as rule (rule.id)}
								<RuleCard {rule} />
							{/each}
						</div>
					</div>
				{/if}
			{/if}
		</Container>
	</Section>
</main>

<Footer />
