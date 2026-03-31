<script lang="ts">
  import { Section, Container } from '$lib/ui';
  import { constitution_headline, constitution_subheadline } from '$lib/paraglide/messages.js';
</script>

<Section hero>
  <Container class="text-center">
    <h1 class="text-5xl md:text-6xl lg:text-7xl font-bold text-text">
      {constitution_headline()}
    </h1>

    <p class="mt-6 text-lg md:text-xl text-text-muted max-w-3xl mx-auto">
      {constitution_subheadline()}
    </p>
  </Container>
</Section>
