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
	<title>The Loop — Active Security Rules</title>
	<meta
		name="description"
		content="Browse all active security and quality rules enforced by The Loop at merge time."
	/>
</svelte:head>

<main id="main-content">
	<Section>
		<Container>
			<div class="mb-8">
				<h1 class="text-3xl font-bold text-text">Active Rules</h1>
				{#if data.version}
					<p class="mt-1 text-text-muted">
						Version <code class="font-mono text-sm text-accent">{data.version}</code>
						· {data.rulesCount} rules
					</p>
				{/if}
			</div>

			{#if data.rules.length === 0}
				<div class="flex flex-col items-center justify-center py-24 text-center">
					<p class="text-xl font-semibold text-text">No rules published yet.</p>
					<p class="mt-2 text-text-muted">Check back soon — rules are published periodically.</p>
				</div>
			{:else}
				{#if errors.length > 0}
					<div class="mb-8">
						<h2 class="mb-3 text-lg font-semibold text-error">
							Critical ({errors.length})
						</h2>
						<div class="flex flex-col gap-3">
							{#each errors as rule (rule.id)}
								<RuleCard {rule} />
							{/each}
						</div>
					</div>
				{/if}

				{#if warnings.length > 0}
					<div>
						<h2 class="mb-3 text-lg font-semibold text-warning">
							Warnings ({warnings.length})
						</h2>
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
