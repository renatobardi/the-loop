<script lang="ts">
  import { user } from '$lib/stores/auth';
  import { logout } from '$lib/firebase';
  import { goto } from '$app/navigation';

  let open = $state(false);

  const links = [
    { label: 'Features', href: '#features' },
    { label: 'Pricing', href: '#pricing' },
    { label: 'Waitlist', href: '#waitlist' },
    { label: 'Incidents', href: '/incidents/' },
  ];

  function closeOnResize() {
    if (window.innerWidth >= 768) {
      open = false;
    }
  }

  async function handleLogout() {
    await logout();
    await goto('/');
  }
</script>

<svelte:window onresize={closeOnResize} />

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
      {#if $user}
        <button
          onclick={handleLogout}
          class="text-sm text-text-muted hover:text-text transition-colors"
        >
          Logout
        </button>
      {/if}
    </div>

    <!-- Mobile hamburger -->
    <button
      onclick={() => open = !open}
      aria-label={open ? 'Close menu' : 'Open menu'}
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
      {#if $user}
        <button
          onclick={async () => {
            open = false;
            await handleLogout();
          }}
          class="text-left text-sm text-text-muted hover:text-text transition-colors py-2"
        >
          Logout
        </button>
      {/if}
    </div>
  {/if}
</nav>
