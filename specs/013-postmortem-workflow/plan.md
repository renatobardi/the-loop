# Plan: Spec-013 — Postmortem Workflow

---

## Context

**Dependency**: Spec-001 (Incident CRUD) ✅  
**Feeds into**: Spec-014 (Analytics), Spec-015 (Webhooks)  
**Decision**: Postmortem obrigatório; templates hardcoded; analytics globais + por-team; async ready

---

## Architecture

### Domain Model (New Entities)

```python
# domain/models.py (new additions)

class RootCauseCategory(StrEnum):
    CODE_PATTERN = "code_pattern"
    INFRASTRUCTURE = "infrastructure"
    PROCESS_BREAKDOWN = "process_breakdown"
    THIRD_PARTY = "third_party"
    UNKNOWN = "unknown"

class PostmortumSeverity(StrEnum):
    ERROR = "error"      # Blocks merge
    WARNING = "warning"  # Advisory

class Postmortem(BaseModel):
    """Incident root cause analysis."""
    id: UUID
    incident_id: UUID                          # Foreign key
    root_cause_category: RootCauseCategory
    description: str                            # 20-2000 chars
    suggested_pattern: str | None               # Regex or semgrep pattern (optional)
    team_responsible: str                       # "backend", "frontend", etc
    severity_for_rule: PostmortumSeverity
    related_rule_id: str | None                # "injection-001" if exists
    
    created_by: UUID                            # Who filled form
    created_at: datetime
    updated_by: UUID | None
    updated_at: datetime | None
    is_locked: bool = False                     # Read-only after incident resolved
    
    class ConfigDict:
        frozen = True

class RootCauseTemplate(BaseModel):
    """Pre-filled template for postmortem."""
    id: str                                     # "sql-injection", "n-plus-one", etc
    category: RootCauseCategory
    title: str
    description_template: str                   # With placeholders or hints
    pattern_example: str | None                 # Example regex/semgrep
    severity_default: PostmortumSeverity
    
    class ConfigDict:
        frozen = True
```

### Database (ORM)

```python
# adapters/postgres/models.py (new additions)

class PostmortumRow(Base):
    __tablename__ = "postmortems"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=gen_random_uuid)
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.id"))
    root_cause_category: Mapped[str]
    description: Mapped[str]
    suggested_pattern: Mapped[str | None]
    team_responsible: Mapped[str]
    severity_for_rule: Mapped[str]
    related_rule_id: Mapped[str | None]
    
    created_by: Mapped[UUID]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_by: Mapped[UUID | None]
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_locked: Mapped[bool] = mapped_column(default=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("LENGTH(description) >= 20", name="ck_description_min_length"),
        CheckConstraint("LENGTH(description) <= 2000", name="ck_description_max_length"),
        CheckConstraint(
            f"root_cause_category IN ({', '.join(repr(c.value) for c in RootCauseCategory)})",
            name="ck_valid_category"
        ),
        UniqueConstraint("incident_id", name="uc_one_postmortem_per_incident"),
    )

# Static data: templates stored in code, not DB
POSTMORTEM_TEMPLATES = {
    "sql-injection": RootCauseTemplate(...),
    "n-plus-one": RootCauseTemplate(...),
    ... (15 total)
}
```

### Alembic Migration

```python
# alembic/versions/008_create_postmortems_table.py

def upgrade():
    op.create_table(
        'postmortems',
        sa.Column('id', sa.UUID(), nullable=False, default=genrandom_uuid),
        sa.Column('incident_id', sa.UUID(), nullable=False),
        sa.Column('root_cause_category', sa.String(50), nullable=False),
        sa.Column('description', sa.String(2000), nullable=False),
        sa.Column('suggested_pattern', sa.String(1000), nullable=True),
        sa.Column('team_responsible', sa.String(255), nullable=False),
        sa.Column('severity_for_rule', sa.String(50), nullable=False),
        sa.Column('related_rule_id', sa.String(100), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=now()),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_locked', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('incident_id', name='uc_one_postmortem_per_incident'),
    )
    
    op.create_index('idx_postmortems_category', 'postmortems', ['root_cause_category'])
    op.create_index('idx_postmortems_team', 'postmortems', ['team_responsible'])
    op.create_index('idx_postmortems_created_at', 'postmortems', ['created_at'])

def downgrade():
    op.drop_table('postmortems')
```

### Hexagonal Layers

```
Domain Layer:
  ├── Postmortem (model)
  ├── RootCauseCategory (enum)
  ├── PostmortumSeverity (enum)
  ├── RootCauseTemplate (model)
  └── PostmortumService (orchestrator)

Ports Layer:
  └── PostmortumRepository (protocol)

Adapters Layer:
  ├── PostmortumRow (ORM)
  ├── PostgresPostmortumRepository (implementation)
  └── PostmortumTemplateProvider (hardcoded templates)

API Layer:
  ├── routes/postmortems.py
  ├── deps.py (injection)
  └── models/postmortems.py (request/response)

Frontend Layer:
  └── lib/components/incidents/PostmortumForm.svelte
```

---

## Tech Stack Decisions

### Backend (Python/FastAPI)

| Component | Choice | Why |
|-----------|--------|-----|
| ORM | SQLAlchemy 2.0 async | Matches Phase 1-2 |
| Models | Pydantic v2 | Validation, serialization |
| Enums | StrEnum | Storage-friendly, type-safe |
| Migration | Alembic | Already in use |
| Testing | pytest + async fixtures | Standard |

### Frontend (SvelteKit)

| Component | Choice | Why |
|-----------|--------|-----|
| Framework | Svelte 5 runes | Matches Phase 1-2 |
| Form state | $state() | Reactive fields |
| Template picker | <select> dropdown | Simple, accessible |
| Validation | Zod + SvelteKit form | Real-time feedback |
| Styling | Tailwind + design tokens | Matches design system |

### Storage (PostgreSQL)

| Feature | Implementation | Notes |
|---------|----------------|-------|
| Templates | Hardcoded dict in code | No DB, just Python constants |
| Postmortems | table `postmortems` | 1 per incident (unique constraint) |
| Audit trail | created_by, updated_by timestamps | Immutable after resolution |
| Indexing | category, team, created_at | Fast aggregations for Spec-014 |

---

## API Endpoints

### Public (Authenticated Users)

```
POST /api/v1/incidents/{id}/postmortems
  Request: {
    "root_cause_category": "code_pattern",
    "description": "SQL concat in user table query...",
    "suggested_pattern": "execute(\"...\" + $VAR)",
    "team_responsible": "backend",
    "severity_for_rule": "error",
    "related_rule_id": "injection-001"
  }
  Response: 201 {
    "id": "uuid",
    "incident_id": "uuid",
    "root_cause_category": "code_pattern",
    ...
    "created_at": "2026-04-10T14:30:00Z"
  }

GET /api/v1/incidents/{id}/postmortem
  Response: 200 {
    "id": "uuid",
    "incident_id": "uuid",
    ...
    "is_locked": false
  }

PUT /api/v1/incidents/{id}/postmortem
  Request: { "description": "...", ... }
  Response: 200 { ... }
  Error 403: If incident is resolved (is_locked=true)

GET /api/v1/postmortem/templates
  Response: 200 {
    "templates": [
      {
        "id": "sql-injection",
        "title": "SQL Injection",
        "category": "code_pattern",
        "description_template": "...",
        "pattern_example": "...",
        "severity_default": "error"
      },
      ...
    ]
  }
```

### Analytics (Spec-014 will use)

```
GET /api/v1/postmortems/summary
  Response: 200 {
    "total": 47,
    "by_category": {
      "code_pattern": 28,
      "infrastructure": 12,
      ...
    },
    "by_team": {
      "backend": 24,
      "frontend": 15,
      ...
    }
  }

GET /api/v1/postmortems/summary?team=backend
  Response: 200 { "total": 24, "by_category": { ... } }
```

---

## Frontend Components

### `/incidents/{id}/postmortem/` (New Route)

```svelte
<script lang="ts">
  import PostmortumForm from "$lib/components/incidents/PostmortumForm.svelte";
  import { incident } from "$lib/stores/incidents";

  // If incident already resolved, show read-only view
  // Else show form
</script>

{#if $incident.status === 'resolved'}
  <PostmortumReadOnly postmortem={incident.postmortem} />
{:else}
  <PostmortumForm 
    incidentId={incident.id}
    existingPostmortem={incident.postmortem}
    onSubmit={handleSubmit}
  />
{/if}
```

### `PostmortumForm.svelte` (Component)

```svelte
<script lang="ts">
  let category = $state<RootCauseCategory>('');
  let description = $state('');
  let pattern = $state('');
  let team = $state('');
  let severity = $state<PostmortumSeverity>('error');
  let ruleId = $state('');
  
  let templates = $state([]);
  let errors = $state<Record<string, string>>({});

  onMount(async () => {
    templates = await fetch('/api/v1/postmortem/templates').then(r => r.json());
  });

  function applyTemplate(templateId: string) {
    const template = templates.find(t => t.id === templateId);
    if (template) {
      category = template.category;
      description = template.description_template;
      pattern = template.pattern_example || '';
      severity = template.severity_default;
    }
  }

  function validate() {
    errors = {};
    if (description.length < 20) errors.description = 'Min 20 chars';
    if (description.length > 2000) errors.description = 'Max 2000 chars';
    if (!category) errors.category = 'Required';
    if (!team) errors.team = 'Required';
    return Object.keys(errors).length === 0;
  }

  async function submit() {
    if (!validate()) return;
    await fetch(`/api/v1/incidents/${incidentId}/postmortems`, {
      method: 'POST',
      body: JSON.stringify({ category, description, pattern, team, severity, ruleId })
    });
  }
</script>

<form onsubmit|preventDefault={submit}>
  <label>
    Template (optional)
    <select onchange={(e) => applyTemplate(e.target.value)}>
      <option value="">Choose template...</option>
      {#each templates as t}
        <option value={t.id}>{t.title}</option>
      {/each}
    </select>
  </label>

  <label>
    Root Cause Category *
    <select bind:value={category} required>
      <option value="">Select...</option>
      <option value="code_pattern">Code Pattern</option>
      <option value="infrastructure">Infrastructure</option>
      ...
    </select>
    {#if errors.category}<span class="error">{errors.category}</span>{/if}
  </label>

  <label>
    Description (20-2000 chars) *
    <textarea bind:value={description} required></textarea>
    <span class="text-sm">{description.length}/2000</span>
    {#if errors.description}<span class="error">{errors.description}</span>{/if}
  </label>

  <label>
    Code Pattern (optional, regex/semgrep)
    <textarea bind:value={pattern} placeholder="e.g., execute(\"...\" + $VAR)"></textarea>
  </label>

  <label>
    Team Responsible *
    <select bind:value={team} required>
      <option value="">Select team...</option>
      <option value="backend">Backend</option>
      <option value="frontend">Frontend</option>
      ...
    </select>
  </label>

  <label>
    Severity for Rule *
    <select bind:value={severity} required>
      <option value="error">ERROR (blocks merge)</option>
      <option value="warning">WARNING (advisory)</option>
    </select>
  </label>

  <label>
    Related Rule ID (optional)
    <input type="text" bind:value={ruleId} placeholder="injection-001" />
  </label>

  <button type="submit">Save Postmortem</button>
</form>

<style>
  .error { color: var(--color-error); font-size: 0.875rem; }
</style>
```

---

## Incident Status Enforcement

### Incident Update Logic

When user tries to `PATCH /api/v1/incidents/{id}` with `status=resolved`:

```python
async def update_incident(...):
    # If transitioning to 'resolved', check postmortem
    if new_status == 'resolved' and old_status != 'resolved':
        postmortem = await repo.get_postmortem(incident_id)
        if not postmortem:
            raise HTTPException(
                status_code=400,
                detail="Postmortem required before closing incident"
            )
        
        # Lock postmortem
        await repo.lock_postmortem(postmortem.id)
    
    # Update incident
    incident = await service.update_status(incident_id, new_status)
    return incident
```

---

## Implementation Phases

### Phase 1: Domain + Database (Days 1-2)
- [ ] Create Postmortem, RootCauseCategory models
- [ ] Create Alembic migration 008
- [ ] Run migration locally
- [ ] Seed hardcoded templates

### Phase 2: Repository + Service (Day 3)
- [ ] PostgresPostmortumRepository (CRUD)
- [ ] PostmortumService (validation, locking)
- [ ] Unit tests

### Phase 3: API Routes (Days 4-5)
- [ ] POST /incidents/{id}/postmortems
- [ ] GET /incidents/{id}/postmortem
- [ ] PUT /incidents/{id}/postmortem
- [ ] GET /postmortem/templates
- [ ] GET /postmortems/summary
- [ ] Error handling + tests

### Phase 4: Incident Integration (Day 5)
- [ ] Update incident.update() to enforce postmortem
- [ ] Add is_locked check to PUT endpoint
- [ ] Tests for lock behavior

### Phase 5: Frontend (Days 6-7)
- [ ] PostmortumForm.svelte component
- [ ] Template picker UI
- [ ] Form validation + error messages
- [ ] Read-only view after resolution

### Phase 6: Testing & Docs (Days 8-9)
- [ ] E2E tests (create incident → fill postmortem → resolve)
- [ ] Coverage ≥80%
- [ ] CLAUDE.md documentation
- [ ] API documentation

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Test coverage | ≥80% (domain, API, service) |
| API latency | <500ms POST, <100ms GET |
| Form completion time | <2 min (with templates) |
| Ruff/mypy | 0 errors |
| E2E tests passing | 100% |

---

## Known Limitations & Future (Spec-015+)

| Item | Phase |
|------|-------|
| Custom template editor | Spec-015 |
| Auto-generate rule from pattern | Spec-014+ |
| Webhook notifications | Spec-015 |
| Multi-language postmortems | Phase C.X |
| Historical postmortem versions | Phase C.X |
| Markdown editing + preview | Phase C.X |

---

## References

- **Spec-001**: Incident CRUD module
- **Spec-012**: Semgrep Phase B (rules)
- **Spec-014**: Analytics (reads postmortem summaries)
- **Spec-015**: Webhooks (sends postmortem events)

