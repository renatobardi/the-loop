# Quickstart: Contributing to the Product Docs

This guide is for developers adding or updating documentation pages in `/docs/`.

## Adding a new user section (visible to all)

1. Create `apps/web/src/routes/docs/{slug}/+page.svelte`
2. Add to `USER_SECTIONS` in `apps/web/src/lib/components/docs/nav.ts`
3. Add to `PERSONA_SECTIONS` for any relevant personas in the same file
4. Write content using `DocSection` and `CodeBlock` components:

```svelte
<script lang="ts">
  import DocSection from '$lib/components/docs/DocSection.svelte';
  import CodeBlock from '$lib/components/docs/CodeBlock.svelte';
</script>

<svelte:head>
  <title>My Topic — The Loop Docs</title>
  <meta name="description" content="One-sentence description." />
</svelte:head>

<DocSection title="Overview" id="overview">
  <p class="text-text">Prose content here.</p>
</DocSection>

<DocSection title="Example" id="example">
  <CodeBlock language="bash" label="Run locally" code={`npm run dev`} />
</DocSection>
```

## Adding a new admin-only section

1. Create `apps/web/src/routes/docs/(admin)/{slug}/+page.svelte`
2. Add to `ADMIN_SECTIONS` in `nav.ts`
3. **Do NOT** add a `+page.ts` — the group `+layout.ts` already sets `ssr = false`
4. **Do NOT** add auth checks — the group `+layout.svelte` handles the admin redirect

```svelte
<!-- (admin)/my-section/+page.svelte — content only, no auth boilerplate -->
<script lang="ts">
  import DocSection from '$lib/components/docs/DocSection.svelte';
</script>

<svelte:head>
  <title>Admin: My Section — The Loop Docs</title>
  <meta name="description" content="Admin-only documentation." />
</svelte:head>

<DocSection title="Overview" id="overview">
  <p class="text-text">Admin content here.</p>
</DocSection>
```

## Updating an existing page

- Edit the corresponding `+page.svelte` directly.
- If the change reflects a platform feature change, update the page **in the same PR** (Mandamento XII).
- Verify every `CodeBlock` still produces a working result (SC-006).

## PR checklist

- [ ] `npm run check` passes (zero type errors)
- [ ] `npm run lint` passes
- [ ] `npm run build` passes
- [ ] New section added to `USER_SECTIONS` or `ADMIN_SECTIONS` in `nav.ts`
- [ ] User section: added to relevant `PERSONA_SECTIONS` entries
- [ ] Admin section: placed inside `routes/docs/(admin)/`, no per-page auth boilerplate
- [ ] Every `CodeBlock` tested against current production API/CLI
- [ ] `<svelte:head>` with unique title + description on every new page
- [ ] CLAUDE.md updated if new routes or components were added
