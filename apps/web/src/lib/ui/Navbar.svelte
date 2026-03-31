<script lang="ts">
  import LanguageSelector from '$lib/components/LanguageSelector.svelte';
  import { nav_features, nav_pricing, nav_waitlist, nav_menu_open, nav_menu_close } from '$lib/paraglide/messages.js';

  let open = $state(false);

  const links = $derived([
    { label: nav_features(), href: '#features' },
    { label: nav_pricing(), href: '#pricing' },
    { label: nav_waitlist(), href: '#waitlist' },
  ]);

  function closeOnResize() {
    if (window.innerWidth >= 768) {
      open = false;
    }
  }
</script>

<svelte:window onresize={closeOnResize} />

<!-- eslint-disable svelte/no-navigation-without-resolve -- anchor links for same-page scroll -->
<nav class="fixed top-0 w-full z-50 bg-bg/80 backdrop-blur-md border-b border-border/50">
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex items-center justify-between h-14">
    <a href="#hero" class="text-lg font-bold text-text">The Loop</a>

    <!-- Desktop links -->
    <div class="hidden md:flex items-center gap-6">
      {#each links as link (link.href)}
        <a href={link.href} class="text-sm text-text-muted hover:text-text transition-colors">
          {link.label}
        </a>
      {/each}
      <LanguageSelector />
    </div>

    <!-- Mobile hamburger -->
    <button
      onclick={() => open = !open}
      aria-label={open ? nav_menu_close() : nav_menu_open()}
      class="md:hidden p-2 text-text-muted hover:text-text transition-colors"
    >
      {#if open}
        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      {:else}
        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      {/if}
    </button>
  </div>

  <!-- Mobile dropdown -->
  {#if open}
    <div class="md:hidden bg-bg/95 backdrop-blur-md border-t border-border/50 px-4 py-4 flex flex-col gap-4">
      {#each links as link (link.href)}
        <a
          href={link.href}
          onclick={() => open = false}
          class="text-sm text-text-muted hover:text-text transition-colors py-2"
        >
          {link.label}
        </a>
      {/each}
      <LanguageSelector />
    </div>
  {/if}
</nav>
