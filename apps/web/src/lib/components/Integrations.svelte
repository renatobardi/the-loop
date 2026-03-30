<script lang="ts">
  import { Section, Container, Card } from '$lib/ui';
  import {
    integrations_headline,
    integration_github_name,
    integration_github_desc,
    integration_ide_name,
    integration_ide_desc,
    integration_rest_name,
    integration_rest_desc,
  } from '$lib/paraglide/messages.js';

  let integrations = $derived([
    {
      name: integration_github_name(),
      description: integration_github_desc(),
    },
    {
      name: integration_ide_name(),
      description: integration_ide_desc(),
    },
    {
      name: integration_rest_name(),
      description: integration_rest_desc(),
    },
  ]);
</script>

{#snippet githubIcon()}
  <!-- Circle icon representing GitHub -->
  <svg class="w-8 h-8 text-accent" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2">
    <circle cx="16" cy="16" r="14" />
    <circle cx="12" cy="14" r="2" fill="currentColor" stroke="none" />
    <circle cx="20" cy="14" r="2" fill="currentColor" stroke="none" />
    <path d="M11 20 c2 3 8 3 10 0" stroke-linecap="round" />
  </svg>
{/snippet}

{#snippet ideIcon()}
  <!-- Code bracket icon representing IDEs -->
  <svg class="w-8 h-8 text-accent" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="10,8 4,16 10,24" />
    <polyline points="22,8 28,16 22,24" />
    <line x1="18" y1="6" x2="14" y2="26" />
  </svg>
{/snippet}

{#snippet restIcon()}
  <!-- Plug icon representing REST API -->
  <svg class="w-8 h-8 text-accent" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 8 L12 14" />
    <path d="M20 8 L20 14" />
    <rect x="8" y="14" width="16" height="6" rx="2" />
    <path d="M16 20 L16 28" />
  </svg>
{/snippet}

<Section id="integrations">
  <Container>
    <h2 class="text-4xl md:text-5xl font-bold text-center mb-12 lg:mb-16">
      {integrations_headline()}
    </h2>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
      {#each integrations as integration, i (integration.name)}
        <Card class="text-center">
          <div class="flex justify-center mb-4">
            {#if i === 0}
              {@render githubIcon()}
            {:else if i === 1}
              {@render ideIcon()}
            {:else}
              {@render restIcon()}
            {/if}
          </div>
          <h3 class="font-semibold">{integration.name}</h3>
          <p class="text-text-muted mt-2">{integration.description}</p>
        </Card>
      {/each}
    </div>
  </Container>
</Section>
