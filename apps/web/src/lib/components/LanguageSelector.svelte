<script lang="ts">
  import { page } from '$app/stores';

  const locales = ['en', 'pt', 'es'] as const;
  const labels: Record<string, string> = {
    en: 'EN',
    pt: 'PT',
    es: 'ES'
  };

  let currentLang = $derived($page.params.lang ?? 'en');
</script>

<nav aria-label="Language selector" class="flex items-center gap-1 text-sm">
  {#each locales as locale, i (locale)}
    {#if i > 0}
      <span class="text-text-subtle select-none">|</span>
    {/if}
    <!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- locale switch requires full reload -->
    <a
      href="/{locale}/"
      data-sveltekit-reload
      class={currentLang === locale ? 'text-text font-medium' : 'text-text-muted hover:text-text transition-colors'}
    >
      {labels[locale]}
    </a>
  {/each}
</nav>
