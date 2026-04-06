<script lang="ts">
	import { profile } from '$lib/stores/profile';
	import {
		USER_SECTIONS,
		ADMIN_SECTIONS,
		PERSONAS,
		type PersonaKey
	} from '$lib/components/docs/nav';
	import PersonaPicker from '$lib/components/docs/PersonaPicker.svelte';

	let selectedPersona = $state<PersonaKey | null>(null);

	let primarySlugs = $derived(
		selectedPersona ? (PERSONAS.find((p) => p.key === selectedPersona)?.primarySections ?? []) : []
	);

	function isHighlighted(slug: string): boolean {
		return primarySlugs.length > 0 && primarySlugs.includes(slug);
	}

	function isDimmed(slug: string): boolean {
		return primarySlugs.length > 0 && !primarySlugs.includes(slug);
	}
</script>

<svelte:head>
	<title>The Loop Docs</title>
	<meta
		name="description"
		content="Everything you need to use The Loop — from onboarding to API reference."
	/>
</svelte:head>

<div class="mb-8">
	<h1 class="text-3xl font-bold text-text mb-2">The Loop Docs</h1>
	<p class="text-text-muted">
		The Loop turns post-mortem lessons into prevention rules enforced at merge time. This
		documentation covers everything from creating your first incident to configuring CI/CD scanner
		integration.
	</p>
</div>

<PersonaPicker onselect={(key) => (selectedPersona = key)} />

<!-- User sections (SSR — always visible) -->
<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
	{#each USER_SECTIONS as section (section.slug)}
		<a
			href="/docs/{section.slug}/"
			class="block p-5 rounded-xl border transition-all
				{isHighlighted(section.slug)
				? 'border-accent bg-accent/10 ring-2 ring-accent/30'
				: isDimmed(section.slug)
					? 'border-border bg-bg-surface opacity-40 hover:opacity-100'
					: 'border-border bg-bg-surface hover:border-border-hover'}"
		>
			<div class="text-2xl mb-2" aria-hidden="true">{section.icon}</div>
			<div class="font-semibold text-text text-sm mb-1">{section.label}</div>
		</a>
	{/each}
</div>

<!-- Admin sections (CSR — silently added after auth resolves, no loading state) -->
{#if $profile?.is_admin}
	<div class="mb-2">
		<span class="text-xs font-semibold uppercase tracking-widest text-text-subtle px-1">
			Administration
		</span>
	</div>
	<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
		{#each ADMIN_SECTIONS as section (section.slug)}
			<a
				href="/docs/{section.slug}/"
				class="block p-5 rounded-xl border border-border/50 bg-bg-surface hover:border-border-hover transition-all"
			>
				<div class="text-2xl mb-2" aria-hidden="true">{section.icon}</div>
				<div class="font-semibold text-text text-sm mb-1">{section.label}</div>
			</a>
		{/each}
	</div>
{/if}
