<script lang="ts">
  import { Container } from '$lib/ui';
  import LanguageSelector from './LanguageSelector.svelte';
  import { hero_branding, footer_copyright, footer_constitution, footer_contact } from '$lib/paraglide/messages.js';
</script>

<footer class="bg-bg-surface border-t border-border py-12">
  <Container class="flex flex-col md:flex-row items-center md:items-start justify-between gap-8">
    <div class="text-center md:text-left">
      <p class="text-lg font-bold text-text">The Loop</p>
      <p class="text-sm text-text-subtle">{hero_branding()}</p>
    </div>

    <nav class="flex flex-col md:flex-row items-center gap-4 md:gap-6 text-sm text-text-muted">
      <!-- eslint-disable svelte/no-navigation-without-resolve -- external/mailto links -->
      <a href="https://github.com/renatobardi/the-loop" target="_blank" rel="noopener noreferrer" class="hover:text-text transition-colors">
        GitHub
      </a>
      <a href="/constitution" class="hover:text-text transition-colors">
        {footer_constitution()}
      </a>
      <a href="mailto:loop@oute.pro" class="hover:text-text transition-colors">
        {footer_contact()}
      </a>
      <!-- eslint-enable svelte/no-navigation-without-resolve -->
      <LanguageSelector />
    </nav>

    <p class="text-sm text-text-subtle text-center md:text-right">
      {footer_copyright()}
    </p>
  </Container>
</footer>
