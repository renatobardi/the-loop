<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    children,
    variant = 'default',
    class: className = '',
    ...restProps
  }: {
    children: Snippet;
    variant?: 'default' | 'accent';
    class?: string;
    [key: string]: unknown;
  } = $props();

  const baseClasses = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium';

  const variantClasses: Record<string, string> = {
    default: 'bg-bg-elevated text-text-muted border border-border',
    accent: 'bg-accent-light text-accent border border-accent/20',
  };
</script>

<span class="{baseClasses} {variantClasses[variant]} {className}" {...restProps}>
  {@render children()}
</span>
