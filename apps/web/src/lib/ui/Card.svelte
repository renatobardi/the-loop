<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    children,
    class: className = '',
    ...restProps
  }: {
    children: Snippet;
    class?: string;
    [key: string]: unknown;
  } = $props();
</script>

<div class="bg-bg-surface border border-border rounded-xl p-6 {className}" {...restProps}>
  {@render children()}
</div>
