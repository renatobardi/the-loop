<script lang="ts">
  let {
    type = 'text',
    placeholder = '',
    name = '',
    value = $bindable(''),
    error = '',
    required = false,
    class: className = '',
    ...restProps
  }: {
    type?: 'text' | 'email';
    placeholder?: string;
    name?: string;
    value?: string;
    error?: string;
    required?: boolean;
    class?: string;
    [key: string]: unknown;
  } = $props();

  const baseClasses =
    'w-full bg-bg-surface border rounded-lg px-4 py-3 text-text placeholder:text-text-subtle outline-none transition-colors';

  const normalClasses = 'border-border focus:border-accent focus:ring-1 focus:ring-accent';
  const errorClasses = 'border-error focus:border-error focus:ring-1 focus:ring-error';
</script>

<div class="flex flex-col gap-1">
  <input
    {type}
    {placeholder}
    {name}
    bind:value
    {required}
    class="{baseClasses} {error ? errorClasses : normalClasses} {className}"
    {...restProps}
  />
  {#if error}
    <span class="text-error text-sm">{error}</span>
  {/if}
</div>
