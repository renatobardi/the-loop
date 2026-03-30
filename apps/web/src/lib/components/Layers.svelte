<script lang="ts">
  import { Section, Container, Card, Badge } from '$lib/ui';
  import {
    layers_headline,
    layer1_label,
    layer1_name,
    layer1_description,
    layer2_label,
    layer2_name,
    layer2_description,
    layer3_label,
    layer3_name,
    layer3_description,
  } from '$lib/paraglide/messages.js';

  let layers = $derived([
    {
      badge: layer1_label(),
      badgeVariant: 'accent' as const,
      name: layer1_name(),
      description: layer1_description(),
    },
    {
      badge: layer2_label(),
      badgeVariant: 'default' as const,
      name: layer2_name(),
      description: layer2_description(),
    },
    {
      badge: layer3_label(),
      badgeVariant: 'default' as const,
      name: layer3_name(),
      description: layer3_description(),
    },
  ]);
</script>

<Section id="layers">
  <Container>
    <h2 class="text-4xl md:text-5xl font-bold text-center mb-12 lg:mb-16">
      {layers_headline()}
    </h2>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
      {#each layers as layer (layer.name)}
        <Card>
          <Badge variant={layer.badgeVariant}>{layer.badge}</Badge>
          <h3 class="text-xl font-semibold mt-4">{layer.name}</h3>
          <p class="text-text-muted mt-2">{layer.description}</p>
        </Card>
      {/each}
    </div>
  </Container>
</Section>
