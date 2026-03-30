<script lang="ts">
  import { Container } from '$lib/ui';
  import LanguageSelector from './LanguageSelector.svelte';
</script>

<footer class="bg-bg-surface border-t border-border py-12">
  <Container class="flex flex-col md:flex-row items-center md:items-start justify-between gap-8">
    <div class="text-center md:text-left">
      <p class="text-lg font-bold text-text">The Loop</p>
      <p class="text-sm text-text-subtle">by Oute</p>
    </div>

    <nav class="flex flex-col md:flex-row items-center gap-4 md:gap-6 text-sm text-text-muted">
      <a href="https://github.com/renatobardi/the-loop" target="_blank" rel="noopener noreferrer" class="hover:text-text transition-colors">
        GitHub
      </a>
      <a href="/constitution" class="hover:text-text transition-colors">
        Constitution
      </a>
      <a href="mailto:loop@oute.pro" class="hover:text-text transition-colors">
        Contact
      </a>
      <LanguageSelector />
    </nav>

    <p class="text-sm text-text-subtle text-center md:text-right">
      &copy; 2026 Oute. All rights reserved.
    </p>
  </Container>
</footer>
