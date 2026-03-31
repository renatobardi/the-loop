<script lang="ts">
  import { languageTag } from '$lib/paraglide/runtime.js';

  let {
    tag = 'nav',
  }: {
    tag?: 'nav' | 'div';
  } = $props();

  const locales = ['en', 'pt', 'es'] as const;
  const labels: Record<string, string> = {
    en: 'EN',
    pt: 'PT',
    es: 'ES'
  };
</script>

<!-- eslint-disable svelte/no-navigation-without-resolve -- ParaglideJS translateHref() handles link resolution via hreflang -->
{#if tag === 'nav'}
  <nav aria-label="Language selector" class="flex items-center gap-1 text-sm">
    {#each locales as locale, idx (locale)}
      {#if idx > 0}
        <span class="text-text-subtle select-none">|</span>
      {/if}
      <a
        href="/"
        hreflang={locale}
        class="inline-flex items-center justify-center min-h-[44px] min-w-[44px] {languageTag() === locale ? 'text-text font-medium' : 'text-text-muted hover:text-text transition-colors'}"
      >
        {labels[locale]}
      </a>
    {/each}
  </nav>
{:else}
  <div role="group" aria-label="Language selector" class="flex items-center gap-1 text-sm">
    {#each locales as locale, idx (locale)}
      {#if idx > 0}
        <span class="text-text-subtle select-none">|</span>
      {/if}
      <a
        href="/"
        hreflang={locale}
        class="inline-flex items-center justify-center min-h-[44px] min-w-[44px] {languageTag() === locale ? 'text-text font-medium' : 'text-text-muted hover:text-text transition-colors'}"
      >
        {labels[locale]}
      </a>
    {/each}
  </div>
{/if}
