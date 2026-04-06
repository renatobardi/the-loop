<script lang="ts">
	import { PERSONAS } from './nav';
	import type { PersonaKey } from './nav';

	let { onselect }: { onselect?: (_: PersonaKey | null) => void } = $props(); // eslint-disable-line no-unused-vars

	let selected = $state<PersonaKey | null>(null);

	function select(key: PersonaKey) {
		if (selected === key) {
			selected = null;
			onselect?.(null);
		} else {
			selected = key;
			onselect?.(key);
		}
	}
</script>

<div class="mb-8">
	<p class="text-text-muted text-sm mb-4">
		Select your role to highlight the most relevant sections for you.
	</p>
	<div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
		{#each PERSONAS as persona (persona.key)}
			<button
				onclick={() => select(persona.key)}
				aria-pressed={selected === persona.key}
				class="text-left p-4 rounded-xl border transition-all
					{selected === persona.key
					? 'border-accent bg-accent/10 text-text'
					: 'border-border bg-bg-surface text-text-muted hover:border-border-hover hover:text-text'}"
			>
				<div class="font-medium text-sm mb-1">
					{persona.label}
				</div>
				<div class="text-xs text-text-subtle leading-snug">
					{persona.description}
				</div>
			</button>
		{/each}
	</div>
</div>
