<script lang="ts">
  import { Section, Container } from '$lib/ui';
  import MandateCard from './MandateCard.svelte';
  import {
    constitution_mandate_1_title,
    constitution_mandate_1_desc,
    constitution_mandate_2_title,
    constitution_mandate_2_desc,
    constitution_mandate_3_title,
    constitution_mandate_3_desc,
    constitution_mandate_4_title,
    constitution_mandate_4_desc,
    constitution_mandate_5_title,
    constitution_mandate_5_desc,
    constitution_mandate_6_title,
    constitution_mandate_6_desc,
    constitution_mandate_7_title,
    constitution_mandate_7_desc,
    constitution_mandate_8_title,
    constitution_mandate_8_desc,
    constitution_mandate_9_title,
    constitution_mandate_9_desc,
    constitution_mandate_10_title,
    constitution_mandate_10_desc,
    constitution_mandate_11_title,
    constitution_mandate_11_desc,
    constitution_mandate_12_title,
    constitution_mandate_12_desc
  } from '$lib/paraglide/messages.js';

  const mandates = [
    { number: 'I', title: constitution_mandate_1_title, desc: constitution_mandate_1_desc },
    { number: 'II', title: constitution_mandate_2_title, desc: constitution_mandate_2_desc },
    { number: 'III', title: constitution_mandate_3_title, desc: constitution_mandate_3_desc },
    { number: 'IV', title: constitution_mandate_4_title, desc: constitution_mandate_4_desc },
    { number: 'V', title: constitution_mandate_5_title, desc: constitution_mandate_5_desc },
    { number: 'VI', title: constitution_mandate_6_title, desc: constitution_mandate_6_desc },
    { number: 'VII', title: constitution_mandate_7_title, desc: constitution_mandate_7_desc },
    { number: 'VIII', title: constitution_mandate_8_title, desc: constitution_mandate_8_desc },
    { number: 'IX', title: constitution_mandate_9_title, desc: constitution_mandate_9_desc },
    { number: 'X', title: constitution_mandate_10_title, desc: constitution_mandate_10_desc },
    { number: 'XI', title: constitution_mandate_11_title, desc: constitution_mandate_11_desc },
    { number: 'XII', title: constitution_mandate_12_title, desc: constitution_mandate_12_desc }
  ];
</script>

<Section>
  <Container>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each mandates as mandate (mandate.number)}
        <MandateCard
          number={mandate.number}
          title={mandate.title()}
          description={mandate.desc()}
        />
      {/each}
    </div>
  </Container>
</Section>
