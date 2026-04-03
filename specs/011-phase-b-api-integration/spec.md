# Spec-011: Phase B — API Integration + Versionamento

**Criado:** 2026-04-03  
**Branch:** `feat/phase-b-api-integration`  
**Fase:** B — Dinâmica (pós-MVP)  
**Timeline:** Q2 2026 (mai-jun, 3-4 semanas)  
**Objetivo:** Mover regras Semgrep de arquivo estático para API com suporte a versionamento

---

## Contexto

### Problema

Phase A (Spec-010) entregou regras estáticas em arquivo YAML. Funciona, mas tem limitações:

- ❌ Sem versionamento — alterar rules = alterar em todos os projetos
- ❌ Sem rollback — erro em regra nova = todos quebram
- ❌ Sem controle centralizado — rules "vivas" no repo, hard de iterar
- ❌ Sem analytics — não rastreia quais rules mais acionam

### Solução

**Mover regras para API versionsda:**

```
Phase A:                      Phase B:
.semgrep/rules.yml    →      GET /api/v1/rules/latest
(estático, hardcoded)         (dinâmico, versionado)
```

**Benefícios:**

- ✅ Semver control (v0.1.0 → v0.2.0 → v0.3.0)
- ✅ Rollback instantâneo (switch para v0.1.0 se v0.2.0 quebra)
- ✅ Novos rules sem quebrar (publish v0.2.0, projects migram gradualmente)
- ✅ Analytics (rastreia qual versão usada, hits por rule)
- ✅ Centralized governance (admin publica versões, code-reviewed)

---

## Requisitos Funcionais

### FR-001: API GET /api/v1/rules/latest
Retorna versão **mais recente ativa** de regras.

```
GET /api/v1/rules/latest
Response 200:
{
  "version": "0.2.0",
  "created_at": "2026-05-15T10:00:00Z",
  "status": "active",
  "rules_count": 20,
  "rules": [
    {
      "id": "injection-001",
      "message": "...",
      "severity": "ERROR",
      ...
    },
    ...
  ]
}
```

**Constraints:**
- Sempre retorna status="active" (ignora draft/deprecated)
- Payload máximo: 100KB (20 rules ~80KB)
- Latência: <50ms (deve ser cacheado)

---

### FR-002: API GET /api/v1/rules/{version}
Retorna versão **específica** de regras (mesmo se deprecated).

```
GET /api/v1/rules/v0.1.0
Response 200: Same format as FR-001

GET /api/v1/rules/v999.0.0 (não existe)
Response 404:
{
  "error": "RuleVersionNotFound",
  "detail": "Version v999.0.0 not found"
}
```

**Constraints:**
- Suporta qualquer versão (ativa, draft, deprecated)
- Projetos podem "pinnar" version se necessário (vide FR-010)

---

### FR-003: API GET /api/v1/rules/versions
Lista **todas as versões** com status.

```
GET /api/v1/rules/versions
Response 200:
{
  "versions": [
    {
      "version": "0.1.0",
      "status": "deprecated",
      "created_at": "2026-04-03T16:00:00Z",
      "rules_count": 6,
      "deprecated_at": "2026-05-15T10:00:00Z"
    },
    {
      "version": "0.2.0",
      "status": "active",
      "created_at": "2026-05-15T10:00:00Z",
      "rules_count": 20,
      "deprecated_at": null
    }
  ]
}
```

---

### FR-004: API POST /api/v1/rules/publish
Publica **nova versão** de regras (admin only).

```
POST /api/v1/rules/publish
Header: Authorization: Bearer {admin_token}
Body:
{
  "version": "0.3.0",
  "rules": [
    { "id": "injection-001", "message": "...", ... },
    ...
  ],
  "notes": "Add path-traversal rules, fix ReDoS pattern"
}

Response 201:
{
  "version": "0.3.0",
  "message": "Published v0.3.0 with 22 rules",
  "created_at": "2026-05-20T14:00:00Z"
}
```

**Constraints:**
- Requer autenticação (Firebase token + admin role)
- Não pode publicar versão existente (conflict)
- Valida semver format (rejeita "latest", "main", etc)

---

### FR-005: Versionamento Semver
Suporta versioning semântico: MAJOR.MINOR.PATCH

```
0.1.0 (first)
0.2.0 (add 14 rules)
0.3.0 (fix ReDoS pattern)
1.0.0 (breaking change — Phase D)
```

**Constraints:**
- Formato validado: `^0\.[0-9]\.[0-9]$` para Phase B
- Phase B = 0.x.y (MVP, não breaking changes)
- Phase E = 1.x.y+ (full SemVer post-GA)

---

### FR-006: Deprecation & Rollback
Versões antigas podem ser deprecadas, mas ainda queryáveis.

```
Workflow (2026-06-01):
  GET /api/v1/rules/v0.1.0  ✅ Still works (deprecated)
  
Admin endpoint (future):
  POST /api/v1/rules/v0.1.0/deprecate
  Response: "Marked v0.1.0 as deprecated"
```

**Constraints:**
- Deprecation é soft (não remove dados)
- Projetos com v0.1.0 pinned continuam funcionando
- Workflow pode avisar: "Using deprecated rule version"

---

### FR-007: Workflow Fallback
Se API estiver **down**, workflow usa rules **cached** (Phase A).

```
Workflow execution:
1. Try: curl https://theloop-api.run.app/api/v1/rules/latest
2. If timeout/500:
   - Log warning: "API unavailable, using cached rules v0.1.0"
   - Use .semgrep/theloop-rules.yml (local copy from Phase A)
3. Scan runs with fallback rules
```

**Constraints:**
- Timeout máximo: 5 segundos
- Fallback sempre disponível (no .semgrep/)

---

### FR-008: Rate Limiting
API suporta rate limiting padrão.

```
GET /api/v1/rules/latest (60 req/min por IP)
GET /api/v1/rules/versions (60 req/min)
POST /api/v1/rules/publish (10 req/min — admin only)
```

**Constraints:**
- Via slowapi (mesmo que outros endpoints The Loop)
- Returns 429 if exceeded

---

### FR-009: Caching
GET /api/v1/rules/latest é **cacheado** (TTL 5 min).

```
Request 1: 100ms (hits DB)
Request 2-60: 5ms (hits cache)
@ T+5min cache expires
Request 61: 100ms (hits DB, refresh)
```

**Constraints:**
- Cache invalidated on POST /publish
- TTL = 5 minutos (balance freshness vs. load)
- In-memory (Redis optional in Phase C)

---

### FR-010: Version Pinning (Opcional)
Projetos podem usar versão específica em vez de latest.

```
Workflow environment variable:
  THELOOP_RULES_VERSION=v0.1.0

Workflow script:
  curl https://theloop-api.run.app/api/v1/rules/v0.1.0
  # Instead of /latest
```

**Constraints:**
- Opcional (default = latest)
- Permite migration strategy (gradual upgrade)

---

### FR-011: Rules Storage (Database)
Nova tabela PostgreSQL armazena **versões de rules**.

```sql
CREATE TABLE rule_versions (
  id UUID PRIMARY KEY,
  version VARCHAR(20) NOT NULL UNIQUE,
  rules_json JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE,
  published_by UUID NOT NULL,  -- User ID
  notes TEXT,
  status VARCHAR(20),  -- "draft", "active", "deprecated"
  deprecated_at TIMESTAMP WITH TIME ZONE,
  CONSTRAINT version_format CHECK (version ~ '^[0-9]\.[0-9]\.[0-9]$')
);

CREATE INDEX idx_rule_versions_status ON rule_versions(status);
CREATE INDEX idx_rule_versions_version ON rule_versions(version);
```

---

### FR-012: Rules Migration (Phase A → Phase B)
Seed inicial: copiar v0.1.0 (6 rules) para DB.

```
Alembic migration:
1. Create rule_versions table
2. INSERT v0.1.0 (6 rules)
   - Copy .semgrep/theloop-rules.yml → rules_json
3. Mark v0.1.0 as "active"
```

---

### FR-013: Documentation
Documentar API, versioning strategy, migration guide.

```
THELOOP.md (updated):
  - "Phase B: Rules are now served via API"
  - "Backward compatible: Phase A workflows still work (fallback)"
  - "Example: fetch specific version"

API docs (in spec/011/):
  - Endpoint reference
  - Error codes
  - Examples (curl, JavaScript, Python)
```

---

## Critérios de Sucesso (Success Criteria)

### SC-001: API Latency
GET /api/v1/rules/latest returns in <50ms (cached).

**Medição:** CloudRun metrics, `time curl ...`  
**Target:** P99 <100ms

---

### SC-002: Rule Versioning
Deploy v0.2.0 (6 original + 14 novas = 20 rules).

**Medição:** `GET /api/v1/rules/v0.2.0 | jq '.rules_count'` = 20  
**Target:** Exatamente 20 rules, all valid

---

### SC-003: Rollback Works
Conseguir ativar v0.1.0 se v0.2.0 quebra (in <2 min).

**Medição:** Teste: publicar v0.2.0 ruim → ativar v0.1.0 → tudo funciona  
**Target:** Rollback em <2 min sem redeployment

---

### SC-004: Workflow Compatibility
Workflow Phase B funciona identicamente a Phase A para usuários finais.

**Medição:** Same comment on PR, same merge-blocking behavior  
**Target:** 0 breaking changes

---

### SC-005: Fallback Reliability
Se API down, workflow usa cached rules sem erro.

**Medição:** Teste: kill API, rodar workflow, verifica fallback  
**Target:** Fallback ativa em <5 seg, scan funciona

---

### SC-006: Test Coverage
Unit + Integration tests cobrem 80% do novo código.

**Medição:** `pytest --cov=src --cov-report=term-missing`  
**Target:** ≥80%

---

### SC-007: Documentation Completeness
API, versioning strategy, migration guide documentados.

**Medição:** Existem docs para: endpoints, semver, rollback, examples  
**Target:** Sem TODOs em docs

---

### SC-008: Database Integrity
Migrations aplicadas sem erro, seed data válida.

**Medição:** Rodar alembic upgrade head, verificar rule_versions table  
**Target:** 0 migration errors

---

### SC-009: Analytics Ready
Infra pronta para rastrear qual versão usada por projeto (Phase D).

**Medição:** incidents table tem campo rules_version_used  
**Target:** Campo populado automaticamente

---

## User Stories

### US1: Admin publica versão de rule (FR-004, FR-005)
**Como** admin  
**Quero** publicar v0.2.0 com 20 rules  
**Para que** todos os projetos usem regras atualizadas

**Acceptance Criteria:**
- [ ] Posso fazer POST /api/v1/rules/publish com v0.2.0
- [ ] Semver validado (rejeita "v0.2", "latest", etc)
- [ ] Response inclui rules_count = 20
- [ ] GET /api/v1/rules/latest retorna v0.2.0

---

### US2: Project fetch latest rules (FR-001, FR-007, FR-009)
**Como** desenvolvedora em projeto X  
**Quero** que meu workflow busque rules mais recentes  
**Para que** beneficie de novas regras sem alterar workflow

**Acceptance Criteria:**
- [ ] Workflow curl /api/v1/rules/latest automaticamente
- [ ] Latência <50ms (cacheado)
- [ ] Se API down, usa fallback local
- [ ] PR comment reflete v0.2.0 rules

---

### US3: Admin rollback bad version (FR-006)
**Como** admin  
**Quero** ativar v0.1.0 se v0.2.0 quebra  
**Para que** reverter erro rapidamente

**Acceptance Criteria:**
- [ ] GET /api/v1/rules/v0.1.0 funciona (mesmo deprecated)
- [ ] Posso marcar v0.2.0 como deprecated
- [ ] GET /api/v1/rules/latest volta para v0.1.0

---

### US4: Project pins specific version (FR-010)
**Como** desenvolvedor cauteloso  
**Quero** pinnar THELOOP_RULES_VERSION=v0.1.0  
**Para que** meu projeto não sofra com breaking changes

**Acceptance Criteria:**
- [ ] Workflow suporta env var THELOOP_RULES_VERSION
- [ ] curl /api/v1/rules/v0.1.0 (não /latest)
- [ ] Backcompatível se env var não definida

---

### US5: Admin sees version history (FR-003)
**Como** admin  
**Quero** listar todas as versões com status  
**Para que** rastrear histórico de regras

**Acceptance Criteria:**
- [ ] GET /api/v1/rules/versions retorna array de versions
- [ ] Cada versão tem: version, status, created_at, rules_count
- [ ] Versões deprecated mostram deprecated_at

---

## Edge Cases

### E1: Versão não existe
```
GET /api/v1/rules/v999.0.0
Response 404: { "error": "RuleVersionNotFound", ... }
```

### E2: Semver inválido
```
POST /api/v1/rules/publish
Body: { "version": "latest" }  ❌
Response 400: { "error": "InvalidVersionFormat", ... }
```

### E3: Versão duplicada
```
POST /api/v1/rules/publish
Body: { "version": "0.2.0" }  (já existe)
Response 409: { "error": "VersionAlreadyExists", ... }
```

### E4: API timeout
```
Workflow: curl --max-time 5 /api/v1/rules/latest
Timeout → use .semgrep/theloop-rules.yml (fallback)
Log: "API unavailable, using cached rules v0.1.0"
```

### E5: Admin republish
```
POST /api/v1/rules/publish (v0.2.0 segunda vez)
Response 409: Cannot republish version
❌ Solução: usar v0.2.1 (patch bump)
```

---

## Constraints

### Technical
- **Database:** PostgreSQL 16 (Cloud SQL)
- **Language:** Python 3.12 (FastAPI)
- **ORM:** SQLAlchemy 2.0 async
- **Caching:** In-memory (Redis optional Phase C)
- **Rate Limit:** slowapi (existing)

### Organizational
- **Responsável:** @renatobardi (você)
- **Timeline:** 3-4 semanas (mai-jun)
- **Reviewers:** (quando houver team)
- **Governance:** CONSTITUTION.md (13 mandamentos)

### Performance
- **Latency:** <50ms (cached)
- **Throughput:** 60 req/min per IP
- **Payload:** <100KB per response
- **Uptime:** 99.5% SLA

---

## Relacionamentos com Specs Anteriores

```
Spec-004: Incident CRUD (data model)
  └─ incidents table terá campo rules_version_used

Spec-007: Incident CRUD Phase 1
  └─ Routes criadas, agora adicionamos regras

Spec-008: Incident CRUD Phase 2
  └─ Sub-resources (timeline, responders) — não afetado

Spec-010: Phase A (Static Rules) ✅
  └─ Phase B constrói em cima de Phase A
  └─ Backward compatible (fallback)
```

---

## Deliverables

```
Code:
  ✅ specs/011/spec.md (este arquivo)
  ✅ specs/011/plan.md (arquitetura técnica)
  ✅ specs/011/tasks.md (74 tarefas)
  ✅ specs/011/data-model.md (schema)
  ✅ .semgrep/theloop-rules.yml (updated com 20 rules)
  ✅ .github/workflows/theloop-guard.yml (updated com API fetch)
  ✅ THELOOP.md (updated)

Backend:
  ✅ apps/api/src/adapters/postgres/models.py (RuleVersionRow)
  ✅ apps/api/src/domain/models.py (RuleVersion)
  ✅ apps/api/src/ports/rule_version_repo.py
  ✅ apps/api/src/adapters/postgres/rule_version_repository.py
  ✅ apps/api/src/domain/services.py (RuleVersionService)
  ✅ apps/api/src/api/routes/rules.py (4 endpoints)
  ✅ Alembic migration 007

Tests:
  ✅ tests/unit/domain/test_rule_version.py
  ✅ tests/unit/services/test_rule_version_service.py
  ✅ tests/api/test_rules.py
  ✅ tests/integration/test_rule_versions.py

Documentation:
  ✅ Private: ~/projetos/_deepwiki/the-loop/NOTES/spec-011-learnings.md
  ✅ Private: ~/projetos/_deepwiki/the-loop/ROADMAP.md (updated)
```

---

**Última atualização:** 2026-04-03  
**Próxima revisão:** Após Planning Phase (antes de T001)
