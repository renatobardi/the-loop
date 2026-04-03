# Spec-013 — Postmortem Workflow (Tech Guide)

This document records technical patterns and decisions for Spec-013 implementation.

---

## Architecture Overview

### Hexagonal Layers

```
Domain (Pure Python)
├── Postmortem (Pydantic model, frozen)
├── RootCauseCategory (StrEnum)
├── PostmortumSeverity (StrEnum)
├── PostmortumService (orchestrator)
└── Exceptions (typed)

Ports (Interfaces)
└── PostmortumRepository (protocol)

Adapters (Implementation)
├── PostmortumRow (SQLAlchemy ORM)
├── PostgresPostmortumRepository (DB access)
└── PostmortumTemplateProvider (hardcoded)

API (FastAPI)
├── routes/postmortems.py
├── models/postmortems.py
└── deps.py (dependency injection)

Frontend (SvelteKit)
└── components/incidents/PostmortumForm.svelte
```

---

## Key Design Decisions

### 1. Postmortem = 1 per Incident (Unique Constraint)

```python
# Database constraint
UniqueConstraint("incident_id", name="uc_one_postmortem_per_incident")
```

**Why**: Each incident has exactly ONE root cause analysis. If user needs to update, they UPDATE the existing postmortem, not create a new one.

**Implication**: 
- `POST /incidents/{id}/postmortems` fails 409 if postmortem already exists
- `PUT /incidents/{id}/postmortem` used for updates (not POST again)

---

### 2. Read-Only After Resolution (is_locked)

```python
# When incident transitions to status='resolved':
postmortem.is_locked = True

# Frontend: Hide edit buttons
# API: Return 403 if PUT attempted
```

**Why**: Maintain audit trail. Don't allow retroactive changes to root cause analysis.

**Implication**:
- Must fill postmortem BEFORE marking incident resolved
- UI enforces: Can't click "Resolve" without postmortem
- API enforces: Can't PUT to locked postmortem

---

### 3. Hardcoded Templates (Phase 1)

```python
# adapters/postgres/postmortem_templates.py

POSTMORTEM_TEMPLATES = {
    "sql-injection": RootCauseTemplate(
        id="sql-injection",
        category=RootCauseCategory.CODE_PATTERN,
        title="SQL Injection",
        description_template="...",
        pattern_example=r'execute\(".*"\s\+\s\w+\)',
        severity_default=PostmortumSeverity.ERROR,
    ),
    "n-plus-one": RootCauseTemplate(...),
    ... (15 total)
}
```

**Why**: MVP doesn't need dynamic templates. Hardcoding avoids DB queries and complex admin UI.

**Implication**:
- `GET /postmortem/templates` returns static data (no DB call)
- To add template: Edit code, deploy (not ideal, but acceptable for MVP)
- Future (Spec-015): Make dynamic with admin UI

---

### 4. Analytics-Ready (Spec-014 Foundation)

```python
# Postmortem fields designed for aggregation:
- root_cause_category  (GROUP BY for patterns)
- team_responsible     (GROUP BY for team metrics)
- created_at           (GROUP BY date for timeline)
- severity_for_rule    (count ERROR vs WARNING)

# API endpoint for Spec-014 to query:
GET /api/v1/postmortems/summary
GET /api/v1/postmortems/summary?team=backend
```

**Why**: Design postmortem data so Spec-014 analytics queries are simple and fast.

---

## Implementation Patterns

### Domain Model Pattern

```python
# Frozen model = immutable (once created, can't change)
class Postmortem(BaseModel):
    id: UUID
    incident_id: UUID
    root_cause_category: RootCauseCategory  # Use StrEnum, not str
    description: str
    ...
    
    class ConfigDict:
        frozen = True

# In code, treat as immutable:
# postmortem.description = "new"  ← ❌ ERROR
# Instead: service.update_postmortem(id, description="new")
```

**Why**: Immutability prevents accidental state changes. Explicit service methods enforce business logic.

---

### Repository Pattern (CRUD)

```python
class PostmortumRepository(Protocol):
    async def create(self, postmortem: Postmortem) -> Postmortem: ...
    async def get_by_incident_id(self, incident_id: UUID) -> Postmortem | None: ...
    async def update(self, postmortem: Postmortem) -> Postmortem: ...
    async def get_summary(self) -> dict[str, int]: ...

# Implementation
class PostgresPostmortumRepository:
    def _row_to_domain(self, row: PostmortumRow) -> Postmortem:
        """Convert ORM row → domain model."""
        return Postmortem(
            id=row.id,
            incident_id=row.incident_id,
            root_cause_category=RootCauseCategory(row.root_cause_category),
            description=row.description,
            ...
        )
    
    async def create(self, postmortem: Postmortem) -> Postmortem:
        row = PostmortumRow(
            id=postmortem.id,
            incident_id=postmortem.incident_id,
            root_cause_category=postmortem.root_cause_category.value,  # Store as string
            ...
        )
        self.session.add(row)
        await self.session.flush()
        return self._row_to_domain(row)
```

**Why**: Enum values stored as strings (not integers) for readability. Conversion in `_row_to_domain()` keeps domain layer clean.

---

### Service Layer Pattern

```python
class PostmortumService:
    async def create_postmortem(
        self, 
        incident_id: UUID, 
        category: RootCauseCategory,
        description: str,
        team: str,
        severity: PostmortumSeverity,
        pattern: str | None = None,
        rule_id: str | None = None,
        created_by: UUID = None,
    ) -> Postmortem:
        """Create postmortem with validation."""
        
        # Validate incident exists
        incident = await self.incident_service.get(incident_id)
        if not incident:
            raise IncidentNotFoundError(incident_id)
        
        # Validate postmortem doesn't exist
        existing = await self.repo.get_by_incident_id(incident_id)
        if existing:
            raise PostmortumAlreadyExistsError(incident_id)
        
        # Validate description length
        if len(description) < 20 or len(description) > 2000:
            raise ValueError("Description must be 20-2000 chars")
        
        # Create domain model
        postmortem = Postmortem(
            id=uuid4(),
            incident_id=incident_id,
            root_cause_category=category,
            description=description,
            team_responsible=team,
            severity_for_rule=severity,
            suggested_pattern=pattern,
            related_rule_id=rule_id,
            created_by=created_by,
            created_at=datetime.now(UTC),
        )
        
        # Persist
        return await self.repo.create(postmortem)
    
    async def update_postmortem(
        self,
        postmortem_id: UUID,
        **updates
    ) -> Postmortem:
        """Update postmortem (check locked status)."""
        
        postmortem = await self.repo.get(postmortem_id)
        if not postmortem:
            raise PostmortumNotFoundError(postmortem_id)
        
        if postmortem.is_locked:
            raise PostmortumLockedError(postmortem_id)
        
        # Validate updates
        if "description" in updates:
            desc = updates["description"]
            if len(desc) < 20 or len(desc) > 2000:
                raise ValueError("Description must be 20-2000 chars")
        
        # Merge and update
        # (Note: Frozen model means we create new instance)
        updated = postmortem.model_copy(update={**updates, "updated_at": datetime.now(UTC)})
        return await self.repo.update(updated)
```

**Why**: Service handles all validation before DB write. No invalid data reaches DB.

---

### API Route Pattern

```python
@router.post("/incidents/{incident_id}/postmortems", status_code=201)
@limiter.limit("10/minute")
async def create_postmortem(
    incident_id: UUID,
    request: CreatePostmortumRequest,  # Pydantic model
    user: User = Depends(get_authenticated_user),
    service: PostmortumService = Depends(get_postmortem_service),
) -> PostmortumResponse:
    """Create postmortem for incident."""
    
    try:
        postmortem = await service.create_postmortem(
            incident_id=incident_id,
            category=request.root_cause_category,
            description=request.description,
            team=request.team_responsible,
            severity=request.severity_for_rule,
            pattern=request.suggested_pattern,
            rule_id=request.related_rule_id,
            created_by=user.id,
        )
        return PostmortumResponse.from_domain(postmortem)
    
    except IncidentNotFoundError:
        raise HTTPException(status_code=404, detail="Incident not found")
    except PostmortumAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Postmortem already exists for this incident")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.put("/incidents/{incident_id}/postmortem")
@limiter.limit("10/minute")
async def update_postmortem(
    incident_id: UUID,
    request: UpdatePostmortumRequest,
    user: User = Depends(get_authenticated_user),
    service: PostmortumService = Depends(get_postmortem_service),
) -> PostmortumResponse:
    """Update postmortem (fails if locked)."""
    
    try:
        postmortem = await service.repo.get_by_incident_id(incident_id)
        if not postmortem:
            raise HTTPException(status_code=404, detail="Postmortem not found")
        
        updated = await service.update_postmortem(
            postmortem.id,
            **request.model_dump(exclude_unset=True)
        )
        return PostmortumResponse.from_domain(updated)
    
    except PostmortumLockedError:
        raise HTTPException(status_code=403, detail="Postmortem is locked after resolution")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
```

**Why**: Service layer raises typed exceptions; API layer converts to HTTP status codes. Separation of concerns.

---

### Request/Response Models

```python
class CreatePostmortumRequest(BaseModel):
    root_cause_category: RootCauseCategory
    description: str = Field(min_length=20, max_length=2000)
    suggested_pattern: str | None = Field(None, max_length=1000)
    team_responsible: str = Field(min_length=1, max_length=255)
    severity_for_rule: PostmortumSeverity
    related_rule_id: str | None = Field(None, max_length=100)

class PostmortumResponse(BaseModel):
    id: UUID
    incident_id: UUID
    root_cause_category: RootCauseCategory
    description: str
    ...
    created_at: datetime
    is_locked: bool
    
    @classmethod
    def from_domain(cls, postmortem: Postmortem) -> "PostmortumResponse":
        return cls(
            id=postmortem.id,
            incident_id=postmortem.incident_id,
            root_cause_category=postmortem.root_cause_category,
            description=postmortem.description,
            ...
        )
```

**Why**: Separate request/response models from domain. Request validates input; response serializes output.

---

### Frontend Component Pattern

```svelte
<script lang="ts">
  import { onMount } from "svelte";
  
  export let incidentId: string;
  export let existingPostmortem: Postmortem | null = null;
  export let onSubmit: (postmortem: PostmortumCreate) => Promise<void>;
  
  let templates: RootCauseTemplate[] = [];
  let formData = $state({
    category: existingPostmortem?.root_cause_category || "",
    description: existingPostmortem?.description || "",
    pattern: existingPostmortem?.suggested_pattern || "",
    team: existingPostmortem?.team_responsible || "",
    severity: existingPostmortem?.severity_for_rule || "error",
    ruleId: existingPostmortem?.related_rule_id || "",
  });
  
  let errors = $state<Record<string, string>>({});
  let loading = $state(false);
  
  onMount(async () => {
    const response = await fetch("/api/v1/postmortem/templates");
    templates = await response.json();
  });
  
  function applyTemplate(templateId: string) {
    const template = templates.find(t => t.id === templateId);
    if (template) {
      formData.category = template.category;
      formData.description = template.description_template;
      formData.pattern = template.pattern_example || "";
      formData.severity = template.severity_default;
    }
  }
  
  function validate(): boolean {
    errors = {};
    if (formData.description.length < 20) {
      errors.description = "Min 20 chars";
    }
    if (formData.description.length > 2000) {
      errors.description = "Max 2000 chars";
    }
    if (!formData.category) {
      errors.category = "Required";
    }
    if (!formData.team) {
      errors.team = "Required";
    }
    return Object.keys(errors).length === 0;
  }
  
  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!validate()) return;
    
    loading = true;
    try {
      await onSubmit(formData);
    } finally {
      loading = false;
    }
  }
</script>

<form onsubmit={handleSubmit}>
  <!-- Template picker -->
  <label>
    Template (Optional)
    <select onchange={(e) => applyTemplate(e.target.value)}>
      <option value="">-- Choose template --</option>
      {#each templates as t}
        <option value={t.id}>{t.title}</option>
      {/each}
    </select>
  </label>
  
  <!-- Category -->
  <label>
    Root Cause Category *
    <select bind:value={formData.category} required>
      <option value="">Select...</option>
      <option value="code_pattern">Code Pattern</option>
      <option value="infrastructure">Infrastructure</option>
      <option value="process_breakdown">Process Breakdown</option>
      <option value="third_party">Third-Party Service</option>
      <option value="unknown">Unknown/Other</option>
    </select>
    {#if errors.category}
      <span class="error">{errors.category}</span>
    {/if}
  </label>
  
  <!-- Description -->
  <label>
    Description (20-2000 chars) *
    <textarea 
      bind:value={formData.description} 
      placeholder="What happened? What was the pattern?"
      required
    ></textarea>
    <span class="char-count">{formData.description.length}/2000</span>
    {#if errors.description}
      <span class="error">{errors.description}</span>
    {/if}
  </label>
  
  <!-- Team -->
  <label>
    Team Responsible *
    <select bind:value={formData.team} required>
      <option value="">Select team...</option>
      <option value="backend">Backend</option>
      <option value="frontend">Frontend</option>
      <option value="devops">DevOps</option>
      <option value="other">Other</option>
    </select>
    {#if errors.team}
      <span class="error">{errors.team}</span>
    {/if}
  </label>
  
  <!-- Pattern (optional) -->
  <label>
    Code Pattern (optional, regex or semgrep)
    <textarea 
      bind:value={formData.pattern}
      placeholder="e.g., execute(\"...\" + $VAR)"
    ></textarea>
  </label>
  
  <!-- Severity -->
  <label>
    Severity for Prevention Rule *
    <select bind:value={formData.severity} required>
      <option value="error">ERROR (blocks merge)</option>
      <option value="warning">WARNING (advisory)</option>
    </select>
  </label>
  
  <!-- Related Rule ID (optional) -->
  <label>
    Related Rule ID (optional)
    <input 
      type="text" 
      bind:value={formData.ruleId}
      placeholder="e.g., injection-001"
    />
  </label>
  
  <button type="submit" disabled={loading}>
    {loading ? "Saving..." : "Save Postmortem"}
  </button>
</form>

<style>
  .error { 
    color: var(--color-error);
    font-size: 0.875rem;
    display: block;
    margin-top: 0.25rem;
  }
  
  .char-count {
    font-size: 0.75rem;
    color: var(--text-muted);
    float: right;
  }
</style>
```

**Why**: Svelte 5 runes (`$state`) for reactivity, form validation before submit, clear error messages.

---

## Error Handling

### Domain Exceptions (Typed)

```python
class PostmortumNotFoundError(Exception):
    def __init__(self, postmortem_id: UUID):
        self.postmortem_id = postmortem_id
        super().__init__(f"Postmortem {postmortem_id} not found")

class PostmortumAlreadyExistsError(Exception):
    def __init__(self, incident_id: UUID):
        self.incident_id = incident_id
        super().__init__(f"Postmortem already exists for incident {incident_id}")

class PostmortumLockedError(Exception):
    def __init__(self, postmortem_id: UUID):
        self.postmortem_id = postmortem_id
        super().__init__(f"Postmortem {postmortem_id} is locked after resolution")
```

### API Error Mapping

| Exception | HTTP Status | Message |
|-----------|-------------|---------|
| IncidentNotFoundError | 404 | "Incident not found" |
| PostmortumNotFoundError | 404 | "Postmortem not found" |
| PostmortumAlreadyExistsError | 409 | "Postmortem already exists" |
| PostmortumLockedError | 403 | "Postmortem is locked after resolution" |
| ValueError (validation) | 422 | "[Field] error message" |

---

## Testing Patterns

### Unit Test Example (Service)

```python
@pytest.mark.asyncio
async def test_create_postmortem_success(postmortem_service, incident_id):
    """Create postmortem with valid data."""
    pm = await postmortem_service.create_postmortem(
        incident_id=incident_id,
        category=RootCauseCategory.CODE_PATTERN,
        description="SQL concatenation in user query",
        team="backend",
        severity=PostmortumSeverity.ERROR,
    )
    assert pm.incident_id == incident_id
    assert pm.root_cause_category == RootCauseCategory.CODE_PATTERN
    assert not pm.is_locked

@pytest.mark.asyncio
async def test_create_postmortem_duplicate(postmortem_service, incident_id):
    """Cannot create second postmortem for same incident."""
    await postmortem_service.create_postmortem(
        incident_id=incident_id,
        category=RootCauseCategory.CODE_PATTERN,
        description="First postmortem",
        team="backend",
        severity=PostmortumSeverity.ERROR,
    )
    
    with pytest.raises(PostmortumAlreadyExistsError):
        await postmortem_service.create_postmortem(
            incident_id=incident_id,
            category=RootCauseCategory.INFRASTRUCTURE,
            description="Second postmortem",
            team="devops",
            severity=PostmortumSeverity.ERROR,
        )

@pytest.mark.asyncio
async def test_update_locked_postmortem_fails(postmortem_service, postmortem_id):
    """Cannot update locked postmortem."""
    # Lock postmortem manually (simulate resolution)
    postmortem = await postmortem_service.repo.get(postmortem_id)
    postmortem.is_locked = True
    
    with pytest.raises(PostmortumLockedError):
        await postmortem_service.update_postmortem(
            postmortem_id,
            description="Updated description"
        )
```

### API Test Example

```python
async def test_post_postmortem_success(client, incident_id, auth_token):
    """POST /incidents/{id}/postmortems creates postmortem."""
    response = await client.post(
        f"/api/v1/incidents/{incident_id}/postmortems",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "root_cause_category": "code_pattern",
            "description": "SQL injection via concatenation",
            "team_responsible": "backend",
            "severity_for_rule": "error",
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["incident_id"] == str(incident_id)
    assert data["root_cause_category"] == "code_pattern"

async def test_put_locked_postmortem_fails(client, locked_postmortem_id, auth_token):
    """PUT on locked postmortem returns 403."""
    response = await client.put(
        f"/api/v1/incidents/{incident_id}/postmortem",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"description": "Updated"}
    )
    assert response.status_code == 403
    assert "locked" in response.json()["detail"].lower()
```

---

## Deployment & Operations

### Database
- Migration 008 creates `postmortems` table with constraints
- Indexes on `root_cause_category`, `team_responsible`, `created_at` for Spec-014 queries
- Unique constraint on `incident_id` ensures 1:1 relationship

### Environment Variables
- None new; uses existing `DATABASE_URL`

### Monitoring
- Log all postmortem creations (for audit)
- Monitor POST latency (<500ms target)
- Track postmortem fill rate (% of incidents with postmortem)

---

## Common Gotchas

### 1. Unique Constraint on `incident_id`

If user tries to POST twice:
```python
POST /incidents/{id}/postmortems  # First call → 201
POST /incidents/{id}/postmortems  # Second call → 409 Conflict
```

Use PUT for updates, not POST.

### 2. Enum Storage (String, Not Integer)

```python
# ✅ Good (store value)
root_cause_category = row.root_cause_category.value  # "code_pattern"

# ❌ Bad (store enum object)
root_cause_category = str(row.root_cause_category)   # "RootCauseCategory.CODE_PATTERN"
```

### 3. Frozen Model Means No `.save()`

```python
# ❌ This fails (frozen)
postmortem.description = "new"

# ✅ Do this instead
updated = postmortem.model_copy(update={"description": "new"})
await repo.update(updated)
```

### 4. is_locked Check Must Happen in Service

```python
# ✅ Good (check before DB write)
if postmortem.is_locked:
    raise PostmortumLockedError()

# ❌ Bad (trust client)
# Just let client send PUT, hope they check themselves
```

---

## References

- **Spec-001**: Incident CRUD (creates incidents)
- **Spec-012**: Semgrep Phase B (rules triggered by patterns)
- **Spec-014**: Analytics (reads postmortem summaries)
- **Spec-015**: Webhooks (sends postmortem events)
- **CLAUDE.md** (project root): Hexagonal patterns, Pydantic conventions

