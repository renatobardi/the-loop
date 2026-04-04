<script lang="ts">
  import { user } from '$lib/stores/auth';
  import UserAvatar from './UserAvatar.svelte';

  let open = $state(false);

  const publicLinks = [
    { label: 'Features', href: '#features' },
    { label: 'Pricing', href: '#pricing' },
    { label: 'Waitlist', href: '#waitlist' },
    { label: 'Log in', href: '/login/' },
  ];

  const authLinks = [
    { label: 'Dashboard', href: '/dashboard/' },
    { label: 'Incidents', href: '/incidents/' },
    { label: 'Analytics', href: '/analytics/' },
    { label: 'Docs', href: '/docs/' },
  ];

  function closeOnResize() {
    if (window.innerWidth >= 768) {
      open = false;
    }
  }
</script>

<svelte:window onresize={closeOnResize} />

<nav class="fixed top-0 w-full z-50 bg-bg/80 backdrop-blur-md border-b border-border/50">
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex items-center justify-between h-14">
    <a href="/" class="text-lg font-bold text-text">The Loop</a>

    <!-- Desktop links -->
    <div class="hidden md:flex items-center gap-6">
      {#if $user}
        {#each authLinks as link (link.href)}
          <a href={link.href} class="text-sm text-text-muted hover:text-text transition-colors">
            {link.label}
          </a>
        {/each}
        <!-- Action icons -->
        <button
          class="rounded border border-accent px-3 py-1 text-xs font-medium text-accent hover:bg-accent/10 transition-colors"
        >
          <svg class="inline w-3.5 h-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
          Upgrade
        </button>
        <button aria-label="Search" class="p-1.5 text-text-muted hover:text-text transition-colors">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <circle cx="11" cy="11" r="8" /><path stroke-linecap="round" d="M21 21l-4.35-4.35" />
          </svg>
        </button>
        <button aria-label="Product News" class="p-1.5 text-text-muted hover:text-text transition-colors">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 10-12 0v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        </button>
        <button aria-label="Help" class="p-1.5 text-text-muted hover:text-text transition-colors">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <circle cx="12" cy="12" r="10" /><path stroke-linecap="round" stroke-linejoin="round" d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3M12 17h.01" />
          </svg>
        </button>
        <UserAvatar />
      {:else}
        {#each publicLinks as link (link.href)}
          <a href={link.href} class="text-sm text-text-muted hover:text-text transition-colors">
            {link.label}
          </a>
        {/each}
      {/if}
    </div>

    <!-- Mobile hamburger -->
    <button
      onclick={() => open = !open}
      aria-label={open ? 'Close menu' : 'Open menu'}
      class="md:hidden p-2 text-text-muted hover:text-text transition-colors"
    >
      {#if open}
        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      {:else}
        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      {/if}
    </button>
  </div>

  <!-- Mobile dropdown -->
  {#if open}
    <div class="md:hidden bg-bg/95 backdrop-blur-md border-t border-border/50 px-4 py-4 flex flex-col gap-4">
      {#if $user}
        <div class="flex items-center gap-3 pb-2 border-b border-border/50">
          <UserAvatar />
        </div>
        {#each authLinks as link (link.href)}
          <a
            href={link.href}
            onclick={() => open = false}
            class="text-sm text-text-muted hover:text-text transition-colors py-2"
          >
            {link.label}
          </a>
        {/each}
        <div class="flex items-center gap-4 pt-2 border-t border-border/50">
          <button aria-label="Search" class="p-1.5 text-text-muted hover:text-text transition-colors">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <circle cx="11" cy="11" r="8" /><path stroke-linecap="round" d="M21 21l-4.35-4.35" />
            </svg>
          </button>
          <button aria-label="Product News" class="p-1.5 text-text-muted hover:text-text transition-colors">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 10-12 0v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </button>
          <button aria-label="Help" class="p-1.5 text-text-muted hover:text-text transition-colors">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <circle cx="12" cy="12" r="10" /><path stroke-linecap="round" stroke-linejoin="round" d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3M12 17h.01" />
            </svg>
          </button>
        </div>
      {:else}
        {#each publicLinks as link (link.href)}
          <a
            href={link.href}
            onclick={() => open = false}
            class="text-sm text-text-muted hover:text-text transition-colors py-2"
          >
            {link.label}
          </a>
        {/each}
      {/if}
    </div>
  {/if}
</nav>
