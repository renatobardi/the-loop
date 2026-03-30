<script lang="ts">
  import { Section, Container } from '$lib/ui';
  import { problem_headline, problem_body } from '$lib/paraglide/messages.js';
</script>

<Section id="problem">
  <Container>
    <h2 class="text-4xl md:text-5xl font-bold text-text">
      {problem_headline()}
    </h2>

    <p class="mt-6 text-lg text-text-muted max-w-3xl">
      {problem_body()}
    </p>
  </Container>
</Section>
