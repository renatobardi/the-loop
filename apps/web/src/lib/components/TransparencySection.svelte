<script lang="ts">
  import { Section, Container } from '$lib/ui';
  import {
    constitution_transparency_text,
    constitution_transparency_link
  } from '$lib/paraglide/messages.js';
</script>

<Section>
  <Container class="text-center">
    <p class="text-lg text-text-muted">
      {constitution_transparency_text()}
    </p>
    <!-- eslint-disable svelte/no-navigation-without-resolve -- external link -->
    <a
      href="https://github.com/renatobardi/the-loop/blob/main/CONSTITUTION.md"
      target="_blank"
      rel="noopener noreferrer"
      class="mt-4 inline-block text-accent hover:underline font-medium"
    >
      {constitution_transparency_link()}
    </a>
    <!-- eslint-enable svelte/no-navigation-without-resolve -->
  </Container>
</Section>
