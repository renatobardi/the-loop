<script lang="ts">
  import { Section, Container } from '$lib/ui';
  import MandateCard from './MandateCard.svelte';

  const mandates = [
    { number: 'I', title: 'Trunk-Based Development', description: 'One branch. Always production-ready. Every change goes through review and automated verification before reaching users.' },
    { number: 'II', title: 'Immutable Design System', description: 'Every visual element follows a centralized design system. No ad-hoc styles. Consistency is enforced, not hoped for.' },
    { number: 'III', title: 'Branch Taxonomy', description: 'Every branch follows a strict naming convention. Features, fixes, hotfixes, chores — each has its place. No ambiguity.' },
    { number: 'IV', title: 'Protected Main', description: 'The main branch is sacred. No force pushes. No skipping checks. Every merge requires approval and passing automated gates.' },
    { number: 'V', title: 'Mandatory Approval', description: 'Every pull request requires explicit human approval. No exceptions — not for bots, not for automation, not for anyone.' },
    { number: 'VI', title: 'No Dev Environment', description: 'One environment: production. There is no staging, no preview. If it\'s merged, it\'s live. This forces rigor at every step.' },
    { number: 'VII', title: 'Rigorous CI', description: 'Lint. Type-check. Test. Build. Security scan. Documentation check. All gates must pass. If any fails, the merge is blocked.' },
    { number: 'VIII', title: 'Mandated Security', description: 'Security at four layers: repository, CI/CD pipeline, application runtime, and cloud infrastructure. HTTPS only. No hardcoded secrets. Least privilege everywhere.' },
    { number: 'IX', title: 'Clean Code', description: 'Small functions. Descriptive names. Zero dead code. No magic numbers. Tests as documentation. Violations are enough to reject a change.' },
    { number: 'X', title: 'Hexagonal Architecture', description: 'Domain logic has zero external dependencies. Ports define contracts. Adapters connect to the real world. Clean boundaries, testable by design.' },
    { number: 'XI', title: 'Project History', description: 'Every spec, every decision, every phase is documented and preserved. Nothing is deleted — obsolete docs are archived. The project\'s history is sacred.' },
    { number: 'XII', title: 'Documentation is Code', description: 'Docs are treated with the same rigor as code. Structural changes require doc updates in the same PR. A CI gate enforces it.' },
  ];
</script>

<Section>
  <Container>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each mandates as mandate (mandate.number)}
        <MandateCard
          number={mandate.number}
          title={mandate.title}
          description={mandate.description}
        />
      {/each}
    </div>
  </Container>
</Section>
