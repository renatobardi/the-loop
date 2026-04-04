# Spec-013: Postmortem Workflow

**Objetivo**: Capturar root cause de incidentes e extrair padrões para prevenir repetição.

**Fase**: Phase C.1 — Incident Knowledge Capture  
**Timeline**: 1-2 semanas  
**Status**: Planning

---

## Contexto

### Problema

Hoje (após Spec-012), The Loop é **reativo**:
```
Incidente de produção
  → User cria incident no sistema
  → 20 Semgrep rules rodam em CI
  → Padrão é bloqueado em PRs futuras

Mas faltam 2 passos críticos:
1. ❌ Ninguém documenta POR QUE o incidente aconteceu
2. ❌ Ninguém relaciona o incidente ao padrão de código

Resultado: Conhecimento se perde. Próximo developer entra no mesmo padrão.
```

### Solução

Criar um **Postmortem Workflow** que force captura de root cause:
```
Incident criado
  ↓
  [Form: Por quê? Qual padrão? Qual team?]
  ↓
Sistema relaciona ao pattern → root cause category
  ↓
Dashboard mostra: "SQL injection é 40% dos incidents"
  ↓
Product prioriza: "Adicionar 3 mais rules de injection"
  ↓
Próximas PRs bloqueadas automaticamente
```

**Diferença**:
- **Antes (Spec-012)**: "Regras rodam." (Reativo)
- **Depois (Spec-013)**: "Incidentes informam regras." (Proativo)

---

## Requisitos Funcionais

### FR-001: Postmortem Form (Required Field)

Quando incident é criado, user **obrigatoriamente** deve preencher postmortem antes de "fechar" ou marcar como "resolved".

**Form fields**:
```
1. Root Cause Category (dropdown, obrigatório)
   - Code Pattern (padrão perigoso no código)
   - Infrastructure Issue (infra, config)
   - Process Breakdown (procedure, communication)
   - Third-Party Service (library, API externo)
   - Unknown/Other

2. Description (textarea, 200+ chars, obrigatório)
   - O que exatamente aconteceu?
   - Qual foi o padrão perigoso?

3. Suggested Code Pattern (textarea, opcional)
   - Regex ou semgrep pattern que detects isso
   - Exemplo: '(\w+).execute\(".*"\s\+\s(\w+)\)'

4. Team Responsible (dropdown, obrigatório)
   - Qual team causou isso? (para analytics)

5. Severity for Prevention Rule (dropdown, obrigatório)
   - ERROR (critical, bloqueia merge)
   - WARNING (advisory, não bloqueia)

6. Related Rule ID (text, opcional)
   - Se já existe rule, referenciar: "injection-001"
```

**Validation**:
- Description: min 20 chars, max 2000
- Pattern: valid regex or semgrep syntax (optional, validated if provided)
- Category: must be one of enum values
- No whitespace-only content

---

### FR-002: Root Cause Templates (Hardcoded)

Provide **15 hardcoded root cause templates** that auto-populate form fields:

```
User selects template → form pre-fills:
  - Category
  - Description template (with blanks)
  - Suggested pattern (common vulnerable code)
  - Severity

Templates included:
1. SQL Injection
   - Category: Code Pattern
   - Pattern: String concat in SQL queries
   - Example: "SELECT * FROM users WHERE id = '" + user_input + "'"
   
2. N+1 Query
   - Category: Code Pattern
   - Pattern: Loop with DB query inside
   - Example: "for user in users: user.profile.bio (query per user)"

3. Hardcoded Secret
   - Category: Code Pattern
   - Pattern: Credential in code
   - Example: "API_KEY = 'sk-prod-abc123xyz'"

... (12 more templates)
```

**Hardcoded in app initially** (no DB, not user-editable in Spec-013).

---

### FR-003: Postmortem Status Transitions

Incident lifecycle **with postmortem requirement**:

```
Created
  ↓
[user must fill postmortem to advance]
  ↓
Investigating (postmortem submitted)
  ↓
[analysis, fix, PR testing]
  ↓
Resolved (if postmortem complete)
  ↓ (optional)
Archived
```

**Enforcement**: Cannot mark `status=resolved` unless postmortem exists and is valid.

---

### FR-004: Postmortem Read-Only After Resolution

Once incident moves to "Resolved", postmortem becomes **read-only** with edit history:

```
Postmortem (Resolved):
  Created by: @renatobardi
  Created at: 2026-04-10 14:30 UTC
  Last edited: 2026-04-10 14:45 UTC
  
  [All fields locked - no edit button]
  
  [If needed to update: Create new incident linked to this one]
```

**Why**: Maintain audit trail. Don't allow retroactive changes to root cause analysis.

---

### FR-005: Analytics Foundation (Read from Postmortem)

Expose postmortem data for Spec-014 analytics:

**API endpoint (for Spec-014 to query)**:
```
GET /api/v1/incidents/postmortems/summary
  → Returns:
  {
    "total": 47,
    "by_category": {
      "code_pattern": 28,
      "infrastructure": 12,
      "process_breakdown": 5,
      "third_party": 2
    },
    "by_team": {
      "backend": 24,
      "frontend": 15,
      "devops": 8
    }
  }
```

---

## Non-Functional Requirements

### NFR-001: Postmortem Required Before Resolution
- Cannot resolve incident without postmortem
- UI prevents clicking "Resolve" button if postmortem missing
- API returns 400 if `PATCH /incidents/{id}` with `status=resolved` and no postmortem

### NFR-002: Read-Only After Resolution
- Postmortem edit disabled once incident is resolved
- All changes logged (created_at, updated_at, updated_by)

### NFR-003: Form Performance
- Template dropdown loads in <100ms (hardcoded data)
- Form submission <500ms (single DB write)

### NFR-004: Audit Trail
- Every postmortem change logged: who, what, when
- Immutable once incident resolved

### NFR-005: Validation
- All fields server-side validated
- Description length, pattern syntax (if provided), category enum
- Error messages user-friendly

---

## User Stories

### US-1: Incident Creator Fills Postmortem (Blocking)
**As a** backend engineer  
**I want to** fill postmortem form when closing incident  
**So that** root cause is captured and prevents future incidents  

**Acceptance Criteria**:
- [ ] Form appears when incident created
- [ ] Cannot mark incident as "Resolved" without postmortem
- [ ] Form validates all required fields
- [ ] Description must be >20 chars
- [ ] Template picker auto-populates fields
- [ ] Pattern field validates regex syntax (if provided)

**Test case**:
- Click "Create Incident" → Incident created
- Click "Resolve" without postmortem → Error: "Postmortem required"
- Fill form with template "SQL Injection" → Pattern auto-filled
- Submit → Postmortem saved
- Click "Resolve" → Status changes to "Resolved"
- Try to edit postmortem → Read-only state

---

### US-2: Team Visibility in Analytics
**As a** team lead (future, Spec-014)  
**I want to** see which patterns my team encounters most  
**So that** I can coach engineers on them  

**Acceptance Criteria** (Spec-013 foundation):
- [ ] Postmortem captures team_responsible field
- [ ] Team field stored and indexed
- [ ] API endpoint returns postmortems grouped by team (for Spec-014)

**Test case**:
- Create incident with team="backend"
- Create incident with team="frontend"
- Query `GET /api/v1/incidents/postmortems/summary?team=backend`
- Response shows 1 incident for backend

---

### US-3: Root Cause Templates Accelerate Postmortem
**As a** any engineer  
**I want to** pick template instead of typing everything  
**So that** filling postmortem is <2 minutes  

**Acceptance Criteria**:
- [ ] 15 templates available in dropdown
- [ ] Clicking template pre-fills description, category, pattern
- [ ] User can customize after picking template
- [ ] Templates stored in code (hardcoded, no DB)

**Test case**:
- Click "Incident Form"
- Dropdown shows 15 templates
- Click "SQL Injection" → form auto-fills with SQL concat pattern
- Edit description → custom text saved
- Submit → postmortem created with custom description

---

### US-4: Postmortem Audit Trail
**As a** compliance/audit team (future)  
**I want to** see who created/edited postmortem and when  
**So that** we have accountability record  

**Acceptance Criteria**:
- [ ] created_by, created_at stored
- [ ] updated_by, updated_at tracked on every change
- [ ] API returns full audit trail (created/updated timestamps + users)
- [ ] Once resolved, edit locked (UI + API)

**Test case**:
- Create postmortem (user=alice, time=2026-04-10 14:30)
- Edit postmortem (user=alice, time=2026-04-10 14:45)
- Resolve incident
- Try to edit postmortem → API 403 (locked)
- Query history → shows 2 versions with timestamps

---

## Success Criteria

| Criterion | Acceptance | How to Verify |
|-----------|-----------|--------------|
| **Postmortem required** | Cannot resolve incident without filling form | Try to mark resolved without postmortem → error |
| **15 templates** | All templates load, auto-populate fields | Dropdown shows all 15, clicking each pre-fills form |
| **Validation** | All fields validated server-side | Submit invalid data → 400 with error message |
| **Read-only** | Once resolved, postmortem locked | Resolve incident, try to edit → UI disabled + API 403 |
| **Audit trail** | Every change tracked (user, timestamp) | Check DB: created_by, updated_by, created_at, updated_at |
| **Analytics ready** | Data exposed for Spec-014 queries | `GET /api/v1/incidents/postmortems/summary` returns aggregates |
| **Performance** | Form <100ms, submission <500ms | Monitor response times in tests |
| **Tests** | ≥80% coverage | Run pytest --cov |
| **Docs** | API documented, UI flows clear | Spec-013 CLAUDE.md + API.md |

---

## Edge Cases & Error Handling

### E-1: User tries to resolve without postmortem
**Handling**: API 400 "Postmortem required before resolution"  
**UI**: Disable "Resolve" button if postmortem missing

### E-2: User provides invalid regex pattern
**Handling**: API 400 "Invalid regex pattern. Check syntax."  
**Suggestion**: Link to regex validator tool

### E-3: User leaves description <20 chars
**Handling**: API 422 "Description must be at least 20 characters"  
**UI**: Real-time character counter

### E-4: User tries to edit postmortem after resolution
**Handling**: API 403 "Postmortem is locked after resolution. Create new incident if needed."  
**UI**: Form fields disabled, "Locked" badge shown

### E-5: Template dropdown fails to load
**Handling**: Fallback to blank form (graceful degradation)  
**UI**: Show error: "Templates unavailable. Please fill form manually."

---

## Out of Scope (for Spec-014, 015)

- ❌ Custom template editor (Spec-015: C.X Webhooks)
- ❌ Auto-generate rule from pattern (Spec-014+ maybe)
- ❌ Slack notifications on postmortem (Spec-015: Webhooks)
- ❌ Analytics dashboard (Spec-014)
- ❌ Webhook delivery (Spec-015)
- ❌ Multi-language postmortems (Phase C.X)

---

## References

- **Spec-001**: Incident CRUD (foundation, creates incidents)
- **Spec-012**: Semgrep Phase B (rules to prevent patterns)
- **Spec-014**: Incident Analytics (reads postmortem data)
- **Spec-015**: Webhooks (propagates postmortem events)

---

**Created**: 2026-04-03  
**Status**: Ready for planning phase
