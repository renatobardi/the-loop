<script lang="ts">
  import { languageTag } from '$lib/paraglide/runtime.js';

  const locales = ['en', 'pt', 'es'] as const;
  const labels: Record<string, string> = {
    en: 'EN',
    pt: 'PT',
    es: 'ES'
  };
</script>

<nav aria-label="Language selector" class="flex items-center gap-1 text-sm">
  {#each locales as locale, idx (locale)}
    {#if idx > 0}
      <span class="text-text-subtle select-none">|</span>
    {/if}
    <a
      href="https://loop.oute.pro/{locale}/"
      hreflang={locale}
      class={languageTag() === locale ? 'text-text font-medium' : 'text-text-muted hover:text-text transition-colors'}
    >
      {labels[locale]}
    </a>
  {/each}
</nav>
