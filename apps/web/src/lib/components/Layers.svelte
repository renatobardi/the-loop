<script lang="ts">
  import { Section, Container, Card, Badge } from '$lib/ui';

  const layers = [
    {
      badge: 'Layer 1 · Blocking',
      badgeVariant: 'accent' as const,
      name: 'Static Rules',
      description:
        'Deterministic Semgrep rules derived from real production incidents. Runs in pre-commit and CI. Every finding links to the original incident. No AI hallucinations — pure pattern matching.',
    },
    {
      badge: 'Layer 2 · Consultive',
      badgeVariant: 'default' as const,
      name: 'RAG Advisory',
      description:
        'AI-powered review that compares your pull request against a knowledge base of past incidents. Posts non-blocking comments with matched incidents, confidence scores, and remediation guidance.',
    },
    {
      badge: 'Layer 3 · Progressive',
      badgeVariant: 'default' as const,
      name: 'Auto Synthesis',
      description:
        'When the same pattern is flagged across multiple PRs, The Loop automatically generates a new static rule and opens a PR for human approval. The system learns and hardens over time.',
    },
  ];
</script>

<Section id="layers">
  <Container>
    <h2 class="text-4xl md:text-5xl font-bold text-center mb-12 lg:mb-16">
      Three layers. Zero blind spots.
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
