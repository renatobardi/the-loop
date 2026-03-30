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

<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 {className}" {...restProps}>
  {@render children()}
</div>
