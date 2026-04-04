# Plan — Spec-016: Semgrep Platform

**Status:** Ready for implementation  
**Branch:** `feat/016-semgrep-platform`

---

## Stack & Constraints

- Backend: FastAPI + SQLAlchemy 2.0 async + PostgreSQL 16 (hexagonal architecture)
- Frontend: SvelteKit 2 + Svelte 5 runes + Tailwind 4
- Infra: GCP Cloud Run + Global External Load Balancer (existente)
- Auth: Firebase (usuários) + API keys próprias (workflows CI)
- CI: todos os gates existentes permanecem (ruff, mypy strict, pytest ≥80%, build, Trivy)

---

## Modelo de Dados

### Tabela `users` — extensão (migration 011)
```sql
ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE;
```
Seed: `UPDATE users SET is_admin = TRUE WHERE firebase_uid = '<renato_uid>'`
Para obter o uid: `SELECT firebase_uid FROM users WHERE email = 'loop@oute.pro';`

### Tabela `api_keys` (migration 012)
```sql
CREATE TABLE api_keys (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name        TEXT NOT NULL,                    -- ex: "my-repo-prod"
  key_hash    TEXT NOT NULL UNIQUE,             -- SHA-256 do token, nunca plaintext
  prefix      TEXT NOT NULL,                    -- primeiros 8 chars para identificação
  last_used_at TIMESTAMPTZ,
  revoked_at  TIMESTAMPTZ,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```
Formato do token gerado: `tlp_` + 32 bytes base64url (ex: `tlp_aB3xZ...`). Exibido **uma única vez** na criação. Armazenado apenas como `SHA-256(token)`.

### Tabela `scans` (migration 012, mesma migration)
```sql
CREATE TABLE scans (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  api_key_id      UUID NOT NULL REFERENCES api_keys(id),
  repository      TEXT NOT NULL,               -- "owner/repo"
  branch          TEXT NOT NULL,
  pr_number       INTEGER,                     -- NULL se scan manual
  rules_version   TEXT NOT NULL,               -- ex: "0.2.0"
  findings_count  INTEGER NOT NULL DEFAULT 0,
  errors_count    INTEGER NOT NULL DEFAULT 0,
  warnings_count  INTEGER NOT NULL DEFAULT 0,
  duration_ms     INTEGER,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_scans_api_key_id ON scans(api_key_id);
CREATE INDEX idx_scans_created_at ON scans(created_at DESC);
```

### Tabela `scan_findings` (migration 012, mesma migration)
```sql
CREATE TABLE scan_findings (
  id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_id   UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
  rule_id   TEXT NOT NULL,       -- ex: "injection-001"
  file_path TEXT NOT NULL,
  line      INTEGER NOT NULL,
  severity  TEXT NOT NULL        -- "ERROR" | "WARNING"
);
CREATE INDEX idx_scan_findings_scan_id ON scan_findings(scan_id);
CREATE INDEX idx_scan_findings_rule_id ON scan_findings(rule_id);
```
Enviados no payload do `POST /api/v1/scans` como array `findings: [{rule_id, file_path, line, severity}]`. Habilita "top rules" no dashboard.

### Tabela `rule_whitelists` (migration 013)
```sql
CREATE TABLE rule_whitelists (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  api_key_id  UUID NOT NULL REFERENCES api_keys(id) ON DELETE CASCADE,
  rule_id     TEXT NOT NULL,                   -- ex: "injection-001"
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(api_key_id, rule_id)
);
```
Apenas usuários autenticados (Firebase) podem gerenciar o whitelist de suas keys. `GET /api/v1/rules/{version}` com API key aplica o whitelist automaticamente.

---

## Arquitetura de Autenticação — Princípio Global do Produto

Este modelo se aplica a **todos** os endpoints do The Loop, agora e no futuro:

```
Sem Authorization header      → Anônimo / Free  → comportamento padrão, sem personalização
Authorization: Bearer tlp_... → API key          → padrão + whitelist e configs de projeto
Authorization: Bearer eyJ...  → Firebase JWT     → tudo + dashboard + settings + admin
```

**Regra:** qualquer configuração, personalização ou ajuste exige identidade. Sem token = comportamento padrão, zero features extras. Ao projetar qualquer nova feature: "é personalização?" → exige identidade. "é comportamento global?" → funciona anônimo.

`deps.py` detecta o prefixo e roteia:
- `get_api_key_data()` — `SHA-256(token)` → lookup em `api_keys` → retorna `ApiKeyData`
- `get_optional_identity()` — aceita qualquer tier; retorna `None | ApiKeyData | FirebaseTokenData`
- `get_firebase_token_data()` — Firebase JWT obrigatório
- `require_admin()` — Firebase + `user.is_admin == True`

**Por tipo de rota:**
- Rotas CI (`POST /api/v1/scans`): requerem API key
- `GET /api/v1/rules/{version}`: anônimo (retorna tudo) ou API key (aplica whitelist)
- Rotas de usuário (settings, scans, api-keys): requerem Firebase
- Rotas de admin: requerem Firebase + `is_admin`

---

## Fases de Implementação

### Phase 1 — Infraestrutura: `api.loop.oute.pro` (2 dias)

**⚠️ PRÉ-REQUISITO — @renatobardi no Hostinger (antes de iniciar qualquer task):**
Adicionar o seguinte registro DNS no painel do Hostinger para o domínio `oute.pro`:
```
Tipo:  A
Nome:  api.loop
Valor: 34.110.250.203
TTL:   3600 (ou padrão)
```
Após confirmar que o registro foi adicionado, este pré-requisito é considerado concluído e a implementação segue sem bloqueio.

**Phase 1a — GCP (executado por Claude via gcloud, independente do DNS propagar):**
1. Criar SSL cert Google-managed: `theloop-api-cert` para `api.loop.oute.pro`
2. Criar Serverless NEG: `theloop-api-neg` → Cloud Run `theloop-api`
3. Criar backend service: `theloop-api-backend`
4. Adicionar NEG ao backend service
5. Atualizar URL map `the-loop-urlmap` com host rule: `api.loop.oute.pro/* → theloop-api-backend`
6. Adicionar `theloop-api-cert` ao HTTPS proxy `the-loop-https-proxy`

**Phase 1b — Código (independente do DNS, pode rodar em paralelo com 1a):**
- Search & replace `theloop-api-1090621437043.us-central1.run.app` → `api.loop.oute.pro` ✅ concluído
- Atualizar `deploy.yml`: `PUBLIC_API_BASE_URL=https://api.loop.oute.pro`
- Atualizar `theloop-guard.yml`: URL do curl
- Atualizar fallbacks em `incidents.ts`, `analytics.ts`, `users.ts`
- Atualizar docs: `README.md`, `THELOOP.md`, `CLAUDE.md`, `ANALYTICS.md`

**Phase 1c — Validação (requer DNS propagado + SSL provisionado, ~10–60 min após DNS do Hostinger):**
- `curl https://api.loop.oute.pro/api/v1/health` → `{"status":"ok"}`
- Verificar `gcloud compute ssl-certificates describe theloop-api-cert` → status `ACTIVE`

---

### Phase 2 — Quick Wins: Job Summary + PR comment (2 dias)

**`theloop-guard.yml` — Job Summary:**
- Capturar `START_TIME=$(date +%s%3N)` antes do scan
- Após scan: `DURATION=$(( $(date +%s%3N) - START_TIME ))`
- Contar regras: `python3 -c "import yaml; ...` lendo `.semgrep/theloop-rules.yml`
- Escrever em `$GITHUB_STEP_SUMMARY` o formato aprovado (clean / findings)

**`theloop-guard.yml` — PR comment melhorado:**
- Adicionar coluna "Description" na tabela: extrair `r.extra.message` do JSON do semgrep
- Linha de métricas no rodapé: `X rules checked · Y findings · scan completed in Zs`
- Corrigir link "View rules": `.semgrep/theloop-rules.yml` → `https://loop.oute.pro/rules/latest`

---

### Phase 3 — Página pública `/rules/latest` (2 dias)

**Backend:**
- `GET /api/v1/rules/latest` e `GET /api/v1/rules/{version}` já existem
- Atualizar para aceitar `get_optional_identity()`: anônimo retorna tudo, API key aplica whitelist
- Garantir que retornam `message`/`description` por regra (verificar schema atual)

**Frontend — SvelteKit:**
- `src/routes/rules/+page.server.ts` → fetch SSR de `GET /api/v1/rules/latest`
- `src/routes/rules/[version]/+page.server.ts` → fetch SSR de `GET /api/v1/rules/{version}`
- Componente `RulesPage.svelte`: lista de regras com badge de severity, descrição, exemplo de código
- Rota pública: sem guard de auth no layout
- Design: tokens existentes (`bg-bg`, `text-text`, `Badge` com variant por severity)

---

### Phase 4 — Backend: API Keys + Scans (3 dias)

**Hexagonal pattern (mesmo padrão de sub-resources):**

```
domain/models.py       → ApiKey, Scan, ScanFinding (Pydantic, frozen)
domain/exceptions.py   → ApiKeyNotFoundError, ApiKeyRevokedError, ApiKeyInvalidError, ScanNotFoundError
ports/api_key_repo.py  → ApiKeyRepoPort (Protocol)
ports/scan_repo.py     → ScanRepoPort (Protocol)
adapters/postgres/api_key_repository.py
adapters/postgres/scan_repository.py
adapters/postgres/models.py → ApiKeyRow, ScanRow, ScanFindingRow
domain/services.py     → ApiKeyService (create, list_by_user, revoke, validate, get_whitelist, add_to_whitelist, remove_from_whitelist), ScanService
api/routes/api_keys.py → CRUD endpoints (Firebase auth)
api/routes/scans.py    → POST /api/v1/scans (API key auth) + GET + summary (Firebase auth)
api/deps.py            → get_api_key_data(), get_optional_identity(), require_admin()
```

**Endpoints:**
```
POST   /api/v1/api-keys                          → criar key (Firebase auth) → retorna token UMA VEZ
GET    /api/v1/api-keys                          → listar keys do usuário (sem revelar hash)
DELETE /api/v1/api-keys/{id}                     → revogar key
GET    /api/v1/api-keys/{id}/whitelist           → listar regras suprimidas da key (Firebase auth)
POST   /api/v1/api-keys/{id}/whitelist           → adicionar regra à whitelist (Firebase auth)
DELETE /api/v1/api-keys/{id}/whitelist/{rule_id} → remover regra da whitelist (Firebase auth)
POST   /api/v1/scans                             → registrar scan (API key auth, best-effort)
GET    /api/v1/scans                             → listar scans do usuário (Firebase auth)
GET    /api/v1/scans/summary                     → métricas agregadas para dashboard
```

**Linguagem por rule_id:** `GET /api/v1/admin/metrics` e `GET /api/v1/scans/summary` derivam linguagem do prefixo do `rule_id` em `scan_findings` — `js-` → JS/TS, `go-` → Go, demais → Python. Sem coluna extra no banco.

**`POST /api/v1/scans` — chamado pelo workflow:**
```bash
curl -X POST https://api.loop.oute.pro/api/v1/scans \
  -H "Authorization: Bearer $THELOOP_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"repository":"owner/repo","branch":"feat/x","pr_number":42,
       "rules_version":"0.2.0","findings_count":2,"errors_count":1,
       "warnings_count":1,"duration_ms":4230,
       "findings":[{"rule_id":"injection-001","file_path":"src/db.py","line":42,"severity":"ERROR"}]}'
```

**Workflow update:** 
- Step de fetch já captura versão: `RULES_VERSION=$(python3 -c "import json; print(json.load(open('/tmp/rules.json'))['version'])")`
- Adicionar step `Register scan` após o scan, com `continue-on-error: true` (falha no registro não bloqueia o CI)
- Payload inclui array `findings` com cada finding individual para popular `scan_findings`

---

### Phase 5 — Dashboard de violations (3 dias)

**Backend:**
- `GET /api/v1/scans/summary` agrega dados de **todas as keys do usuário** (todos os repos): `total_scans`, `total_findings`, `scans_by_week` (últimas 4 semanas), `top_rules` (top 5 rule_ids por frequência de findings). Filtro por repo é fase futura.

**Frontend:**
- `src/routes/dashboard/+page.svelte` (hoje placeholder "Under construction") → implementar
- Seções: Scan Timeline (sparkline semanal), Top Rules (lista rankeada), Stats cards (total scans, total findings, repos ativos)
- Dados via `GET /api/v1/scans/summary` com Firebase auth
- Loading/empty states em inglês

---

### Phase 6 — Admin de regras na UI (4 dias)

**Backend:**
- `require_admin` dependency: `Depends(get_authenticated_user)` + check `user.is_admin`
- `POST /api/v1/rules/versions` — criar versão draft (novo endpoint, require_admin); versão especificada pelo admin no body (`{"version": "0.3.0"}`); retorna `{version: "0.3.0", status: "draft"}`
- `PUT /api/v1/rules/{version}/rules/{rule_id}` — editar regra individual (novo endpoint, require_admin)
- `POST /api/v1/rules/publish` já existe — adicionar guard `require_admin`
- `GET /api/v1/admin/metrics` — agrega dados globais: `active_repos` (repos com scan nos últimos 30 dias), `scans_by_week` (4 semanas, todos os usuários), `top_languages` (derivado do prefixo do rule_id em scan_findings, require_admin)

**Frontend:**
- `src/routes/admin/+layout.svelte` → guard: redirect se `!$profile?.is_admin`
- `src/routes/admin/rules/+page.svelte` → lista versões + botão "New Version"
- `src/routes/admin/rules/[version]/+page.svelte` → lista regras da versão com botão editar
- `src/routes/admin/rules/[version]/edit/+page.svelte` → editor: campos `id`, `message`, `severity`, `pattern` + preview JSON
- `src/routes/admin/rules/[version]/publish/+page.svelte` → resumo + botão confirmar publicação

---

### Phase 7 — Onboarding + API key management (3 dias)

**Frontend — Settings page (nova aba "API Keys" + "Onboarding"):**
- `src/routes/settings/+page.svelte` → adicionar tabs "API Keys" e "Onboarding" ao `TABS` array existente (fluxo natural: criar key → copiar workflow na mesma tela)
- Lista de keys: nome, prefix (`tlp_aBc3...`), criada em, último uso, botão revogar
- Criar key: input de nome → POST → modal com token completo + aviso "Save now — this won't be shown again"
- Revogar: confirmação → DELETE

**Frontend — Onboarding (`/settings/` aba "Onboarding"):**
- Selecionar key existente ou criar nova
- Exibir `theloop-guard.yml` pré-preenchido com a key em textarea + botão "Copy"
- Link para documentação

---

### Phase 8 — Regras JS/TS + Go — v0.3.0 (6 dias)

**JS/TS — 15 regras:**

| Rule ID | Categoria | Severity |
|---------|-----------|----------|
| js-injection-001 | SQL via string concat (knex/raw) | ERROR |
| js-injection-002 | eval() com input externo | ERROR |
| js-injection-003 | innerHTML/dangerouslySetInnerHTML | ERROR |
| js-injection-004 | child_process.exec com template string | ERROR |
| js-crypto-001 | MD5/SHA1 via crypto.createHash | WARNING |
| js-crypto-002 | Math.random() para tokens/secrets | ERROR |
| js-security-001 | JWT hardcoded secret | ERROR |
| js-security-002 | CORS origin: '*' (express) | WARNING |
| js-security-003 | process.env.NODE_ENV === 'production' desabilitando TLS | ERROR |
| js-security-004 | Prototype pollution via Object.assign | WARNING |
| js-perf-001 | await dentro de loop (N+1 async) | WARNING |
| js-config-001 | console.log com dados sensíveis | WARNING |
| js-config-002 | hardcoded URL de produção no código | WARNING |
| ts-security-001 | any type em dados de entrada externa | WARNING |
| ts-security-002 | as unknown as T (type assertion forçado) | WARNING |

**Go — 10 regras:**

| Rule ID | Categoria | Severity |
|---------|-----------|----------|
| go-injection-001 | fmt.Sprintf em SQL query | ERROR |
| go-injection-002 | exec.Command com variável externa | ERROR |
| go-injection-003 | path.Join com input externo sem validação | ERROR |
| go-crypto-001 | md5.New() / sha1.New() | WARNING |
| go-crypto-002 | math/rand em vez de crypto/rand | ERROR |
| go-security-001 | InsecureSkipVerify: true | ERROR |
| go-security-002 | JWT com secret hardcoded | ERROR |
| go-error-001 | err ignorado com `_` em operação crítica | WARNING |
| go-error-002 | panic() em handler HTTP | WARNING |
| go-config-001 | http.ListenAndServe sem TLS em produção | WARNING |

**Convenção de IDs:** namespace por linguagem — `js-injection-001`, `go-crypto-001` etc. Evita colisão com as regras Python existentes e deixa claro no finding qual linguagem foi afetada.

**Por regra:** definição YAML + test data `bad/<lang>/` + test data `good/<lang>/`
**Publicação:** v0.3.0 via admin UI (Phase 6) ou `POST /api/v1/rules/publish` diretamente
**Atualizar** `.semgrep/theloop-rules.yml.bak` com todas as 45 regras

---

### Phase 9 — Testes, docs, polish (3 dias)

- `pytest --cov=src --cov-fail-under=80` passando
- `mypy src/` strict: 0 erros
- `ruff check src/ tests/`: 0 erros
- Testes API: `test_api_keys.py`, `test_scans.py`
- Testes unitários: `test_api_key_service.py`, `test_scan_service.py`
- Atualizar `README.md`: nova seção "API Keys & Scan History"
- Atualizar `THELOOP.md`: workflow com step de registro de scan
- Atualizar `CLAUDE.md`: novos modelos e rotas

---

## Sequência de Migrations Alembic

```
011_add_is_admin_to_users.py
012_create_api_keys_scans_and_findings.py   ← api_keys + scans + scan_findings
013_create_rule_whitelists.py

Nota: migrations 008 (postmortems), 009 (analytics indexes) e 010 (users) já existem.
```

---

## Riscos & Mitigações

| Risco | Mitigação |
|-------|-----------|
| SSL cert demorando a provisionar (GCP pode levar até 24h) | Phase 1 pode rodar em paralelo com Phase 2; merge do código só depois que cert estiver ACTIVE |
| `POST /api/v1/scans` aumentando latência do CI | `continue-on-error: true` + timeout de 3s no curl; falha no registro não bloqueia scan |
| Token API key exposto em logs do CI | Workflow usa `${{ secrets.THELOOP_API_TOKEN }}` — GitHub mascara automaticamente |
| Regras JS/TS com muitos false positives | Test data rigoroso (good/ deve ter 0 findings); `semgrep --validate` obrigatório antes de publicar |

---

**Última atualização:** 2026-04-04  
**Próximo passo:** implementação (Phase 1 — `api.loop.oute.pro`)
