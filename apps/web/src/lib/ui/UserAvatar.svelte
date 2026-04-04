<script lang="ts">
  import { user } from '$lib/stores/auth';
  import { profile, loadProfile, clearProfile } from '$lib/stores/profile';
  import { getInitials } from '$lib/utils/users';
  import { goto } from '$app/navigation';

  let open = $state(false);
  let buttonEl = $state<HTMLButtonElement | null>(null);
  let dropdownEl = $state<HTMLDivElement | null>(null);

  const initials = $derived.by(() =>
    getInitials($profile?.display_name ?? $user?.displayName ?? null, $user?.email ?? null)
  );

  $effect(() => {
    if ($user) {
      loadProfile();
    } else {
      clearProfile();
    }
  });

  $effect(() => {
    if (!open) return;
    function handleClickOutside(e: MouseEvent) {
      if (
        buttonEl && !buttonEl.contains(e.target as Node) &&
        dropdownEl && !dropdownEl.contains(e.target as Node)
      ) {
        open = false;
      }
    }
    function handleKeydown(e: KeyboardEvent) {
      if (e.key === 'Escape') open = false;
    }
    document.addEventListener('click', handleClickOutside);
    document.addEventListener('keydown', handleKeydown);
    return () => {
      document.removeEventListener('click', handleClickOutside);
      document.removeEventListener('keydown', handleKeydown);
    };
  });

  async function handleLogout() {
    open = false;
    const { logout } = await import('$lib/firebase');
    await logout();
    await goto('/');
  }
</script>

<div class="relative">
  <button
    bind:this={buttonEl}
    onclick={() => open = !open}
    aria-label="User menu"
    aria-expanded={open}
    class="w-8 h-8 rounded-full bg-accent/20 text-accent font-semibold text-sm flex items-center justify-center hover:bg-accent/30 transition-colors"
  >
    {initials}
  </button>

  {#if open}
    <div
      bind:this={dropdownEl}
      role="menu"
      class="absolute right-0 mt-2 w-52 rounded-lg border border-border bg-bg-elevated shadow-glow z-50"
    >
      <div class="px-4 py-3 border-b border-border">
        <p class="text-sm font-semibold text-text truncate">
          {$profile?.display_name ?? $user?.displayName ?? ''}
        </p>
        <p class="text-xs text-text-muted truncate">{$user?.email ?? ''}</p>
      </div>
      <div class="py-1">
        <a
          href="/settings/"
          role="menuitem"
          onclick={() => open = false}
          class="block px-4 py-2 text-sm text-text-muted hover:text-text hover:bg-bg-surface transition-colors"
        >
          Minha conta
        </a>
        <button
          role="menuitem"
          onclick={handleLogout}
          class="w-full text-left px-4 py-2 text-sm text-text-muted hover:text-text hover:bg-bg-surface transition-colors"
        >
          Log out
        </button>
      </div>
    </div>
  {/if}
</div>
