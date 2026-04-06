# Data Model: Product Docs (Spec-021)

**Note**: The docs are static content — no new database tables or Firestore collections. The entities below describe the content model used to structure and render pages consistently.

---

## Entities

### DocSection

A named documentation topic rendered as a standalone page at `/docs/{slug}/`.

| Field | Type | Constraints |
|-------|------|-------------|
| `slug` | string | Unique, URL-safe, kebab-case. Maps to route path (e.g., `incidents` → `/docs/incidents/`). Immutable once published. |
| `label` | string | Display name shown in sidebar and `<h1>`. Max 40 chars. |
| `description` | string | One-sentence summary for feature index cards and `<meta name="description">`. Max 120 chars. |
| `icon` | string | Single emoji used in feature index card. |
| `visibility` | `'all' \| 'admin'` | `'all'` = visible to all authenticated users. `'admin'` = visible only to users with admin role. |
| `content` | Svelte component | Prose content composed of `DocSection` components and `CodeBlock` embeds. Not a DB field — static `+page.svelte`. |

**Uniqueness rule**: `slug` is globally unique.  
**Lifecycle**: Static — added/updated via code changes. Old content archived via redirect, not deleted.  
**Relationships**: Referenced by `Persona.primarySections[]` (user sections only — admin sections have no persona mapping).

---

### Persona

A named user role used to highlight relevant sections on the `/docs/` home page.

| Field | Type | Constraints |
|-------|------|-------------|
| `key` | string | Unique kebab-case identifier. Values: `developer`, `it-manager`, `operator`, `support`, `qa`, `security`. |
| `label` | string | Display name. Max 20 chars. |
| `description` | string | One-line role description. Max 80 chars. |
| `primarySections` | `DocSection.slug[]` | Ordered list of most relevant section slugs. All must have `visibility: 'all'`. Min 2, max 6. |

**Note**: Personas apply only to user-facing sections. Admin sections are not associated with any persona — admins see all admin sections unconditionally.

| Persona key | Primary sections |
|-------------|-----------------|
| `developer` | semgrep, api-keys, rules |
| `it-manager` | getting-started, analytics |
| `operator` | incidents, postmortems, getting-started |
| `support` | incidents, postmortems |
| `qa` | semgrep, rules |
| `security` | semgrep, api-keys, rules |

---

### CodeExample

A copy-able code or configuration block embedded within a DocSection.

| Field | Type | Constraints |
|-------|------|-------------|
| `code` | string | Raw code/config content. Whitespace preserved. |
| `language` | string? | Optional language hint for label (e.g., `yaml`, `bash`, `typescript`). Not used for syntax highlighting. |
| `label` | string? | Optional caption above the block (e.g., `"GitHub Actions workflow"`). |

**Validation rule (FR-014 + SC-006)**: Every CodeExample must reflect current production behavior. Outdated examples must be updated in the same PR as the platform change they reference.

---

## Content Invariants

1. Every `DocSection` with `visibility: 'all'` must have a route at `/docs/{slug}/` rendered with SSR.
2. Every `DocSection` with `visibility: 'admin'` must live inside the `routes/docs/(admin)/` route group (CSR, `ssr = false`, admin redirect).
3. Every `DocSection` must appear in either `USER_SECTIONS` or `ADMIN_SECTIONS` in `nav.ts` — never both.
4. Every `Persona.primarySections` entry must reference a `DocSection` with `visibility: 'all'`.
5. No `DocSection` may reference platform features not live in the current production environment (FR-014).
