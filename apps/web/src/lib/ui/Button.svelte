<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    children,
    variant = 'primary',
    type = 'button',
    disabled = false,
    class: className = '',
    ...restProps
  }: {
    children: Snippet;
    variant?: 'primary' | 'secondary' | 'ghost';
    type?: 'button' | 'submit';
    disabled?: boolean;
    class?: string;
    [key: string]: unknown;
  } = $props();

  const baseClasses = 'rounded-lg px-6 py-3 font-semibold transition-colors';

  const variantClasses: Record<string, string> = {
    primary: 'bg-accent text-white hover:bg-accent-hover',
    secondary: 'bg-bg-surface border border-border text-text hover:border-border-hover',
    ghost: 'bg-transparent text-text-muted hover:text-text hover:bg-bg-surface',
  };
</script>

<button
  {type}
  {disabled}
  class="{baseClasses} {variantClasses[variant]} {className}"
  {...restProps}
>
  {@render children()}
</button>
