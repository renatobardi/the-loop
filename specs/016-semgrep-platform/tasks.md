# Tasks — Spec-016: Semgrep Platform

**Total estimado:** ~28 dias | 9 fases | 168 tasks  
**Branch:** `feat/016-semgrep-platform`  
**[P]** = pode rodar em paralelo com outras tasks [P] da mesma fase

---

## PRÉ-REQUISITO — @renatobardi (antes de iniciar Phase 1)

- [ ] T000: Adicionar registro DNS no Hostinger:
  ```
  Tipo: A | Nome: api.loop | Valor: 34.110.250.203 | TTL: 3600
  ```
  → Confirmar para Claude antes de iniciar Phase 1. A partir da confirmação, considerado concluído.

---

## Phase 1 — Infraestrutura: `api.loop.oute.pro`

### 1a — GCP (independente do DNS propagar)

- [ ] T001: Criar SSL cert Google-managed `theloop-api-cert` para domínio `api.loop.oute.pro`
  ```bash
  gcloud compute ssl-certificates create theloop-api-cert \
    --domains=api.loop.oute.pro --global --project=theloopoute
  ```
- [ ] T002: Criar Serverless NEG `theloop-api-neg` apontando para Cloud Run `theloop-api`
  ```bash
  gcloud compute network-endpoint-groups create theloop-api-neg \
    --region=us-central1 --network-endpoint-type=serverless \
    --cloud-run-service=theloop-api --project=theloopoute
  ```
- [ ] T003: Criar backend service `theloop-api-backend`
  ```bash
  gcloud compute backend-services create theloop-api-backend \
    --load-balancing-scheme=EXTERNAL_MANAGED --global --project=theloopoute
  ```
- [ ] T004: Adicionar NEG ao backend service
  ```bash
  gcloud compute backend-services add-backend theloop-api-backend \
    --global --network-endpoint-group=theloop-api-neg \
    --network-endpoint-group-region=us-central1 --project=theloopoute
  ```
- [ ] T005: Atualizar URL map `the-loop-urlmap` com host rule para `api.loop.oute.pro`
  ```bash
  gcloud compute url-maps import the-loop-urlmap --global \
    --project=theloopoute --source /dev/stdin <<'EOF'
  name: the-loop-urlmap
  hostRules:
  - hosts: ["api.loop.oute.pro"]
    pathMatcher: api-matcher
  - hosts: ["*"]
    pathMatcher: web-matcher
  pathMatchers:
  - name: api-matcher
    defaultService: global/backendServices/theloop-api-backend
  - name: web-matcher
    defaultService: global/backendServices/the-loop-backend
  EOF
  ```
- [ ] T006: Adicionar `theloop-api-cert` ao HTTPS proxy existente `the-loop-https-proxy`
  ```bash
  gcloud compute target-https-proxies update the-loop-https-proxy \
    --global --ssl-certificates=the-loop-cert,theloop-api-cert \
    --project=theloopoute
  ```

### 1b — Código (paralelo com 1a) [P]

- [x] T007: [P] Search & replace `theloop-api-1090621437043.us-central1.run.app` → `api.loop.oute.pro` em todos os arquivos ativos do projeto
- [ ] T008: [P] Atualizar `deploy.yml`: `PUBLIC_API_BASE_URL=https://api.loop.oute.pro`
- [ ] T009: [P] Atualizar `theloop-guard.yml`: URL do curl para fetch de regras
- [ ] T010: [P] Atualizar fallbacks em `apps/web/src/lib/services/incidents.ts`, `analytics.ts`, `users.ts`
- [ ] T011: [P] Atualizar docs: `README.md`, `THELOOP.md`, `CLAUDE.md`, `ANALYTICS.md`
- [ ] T012: [P] Atualizar spec files históricos: `specs/011/`, `specs/012/`, `specs/014/`

### 1c — Validação (requer DNS propagado + SSL ACTIVE)

- [ ] T013: Verificar SSL provisionado: `gcloud compute ssl-certificates describe theloop-api-cert --global` → status `ACTIVE`
- [ ] T014: `curl https://api.loop.oute.pro/api/v1/health` → `{"status":"ok"}`
- [ ] T015: Verificar HTTPS: certificado válido, sem warnings de segurança no browser
- [ ] T016: Commit + PR Phase 1

---

## Phase 2 — Quick Wins: Job Summary + PR Comment

- [ ] T017: Capturar tempo de início no workflow: `START_TIME=$(date +%s%3N)` antes do step de scan
- [ ] T018: Calcular duração após scan: `DURATION_S=$(( ($(date +%s%3N) - START_TIME) / 1000 ))`
- [ ] T019: Contar regras ativas: `RULES_COUNT=$(python3 -c "import yaml; d=yaml.safe_load(open('.semgrep/theloop-rules.yml')); print(len(d['rules']))")`
- [ ] T020: Capturar versão das regras do JSON: `RULES_VERSION=$(python3 -c "import json; print(json.load(open('/tmp/rules.json')).get('version','unknown'))")`
- [ ] T021: Escrever Job Summary no step "Comment PR" — formato aprovado (clean):
  ```
  ## 🔁 The Loop — Incident Guard
  ✅ No incident patterns detected. Code is clean.
  {RULES_COUNT} rules checked · 0 findings · scan completed in {DURATION_S}s
  > Browse active rules → loop.oute.pro/rules/latest
  > Protect your codebase → loop.oute.pro
  ```
- [ ] T022: Escrever Job Summary — formato com findings (🔴/🟡 + tabela + métricas + links)
- [ ] T023: Adicionar coluna "Description" na tabela do PR comment: extrair `r.extra.message` do JSON do semgrep
- [ ] T024: Adicionar linha de métricas no rodapé do PR comment: `{RULES_COUNT} rules checked · {N} findings · scan completed in {DURATION_S}s`
- [ ] T025: Corrigir link "View rules" no PR comment: `.semgrep/theloop-rules.yml` → `https://loop.oute.pro/rules/latest`
- [ ] T026: Testar workflow localmente com `act` ou via PR de teste em the-loop-tester
- [ ] T027: Commit + PR Phase 2

---

## Phase 3 — Página Pública `/rules/latest`

### Backend
- [ ] T028: Verificar schema de resposta de `GET /api/v1/rules/{version}` — confirmar que `message` e `severity` estão presentes por regra
- [ ] T029: Atualizar `get_optional_identity()` em `deps.py` — aceita anônimo, API key ou Firebase sem obrigar auth
- [ ] T030: Atualizar `GET /api/v1/rules/latest` e `GET /api/v1/rules/{version}` para usar `get_optional_identity()` — anônimo retorna tudo, API key aplica whitelist (whitelist vazia por ora, implementação completa na Phase 4)

### Frontend
- [ ] T031: Criar `src/routes/rules/+page.server.ts` — SSR fetch de `GET /api/v1/rules/latest`
- [ ] T032: Criar `src/routes/rules/[version]/+page.server.ts` — SSR fetch de `GET /api/v1/rules/{version}`
- [ ] T033: Criar componente `RuleCard.svelte` em `src/lib/components/rules/` — nome, severity badge, descrição, exemplo de código
- [ ] T034: Criar `src/routes/rules/+page.svelte` — lista de regras com `RuleCard`, agrupadas por severity
- [ ] T035: Criar `src/routes/rules/[version]/+page.svelte` — mesma estrutura, com indicação da versão
- [ ] T036: Estado vazio: sem versão publicada → mensagem "No rules published yet."
- [ ] T037: Rota pública: garantir que não há guard de auth no layout de `/rules/`
- [ ] T038: Adicionar link `/rules/latest` no footer ou navbar (visível para não logados)
- [ ] T039: `npm run check` + `npm run test -- --run` passando
- [ ] T040: Commit + PR Phase 3

---

## Phase 4 — Backend: API Keys + Scans

### Migrations
- [ ] T041: Alembic migration `011_add_is_admin_to_users.py` — `ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE`
- [ ] T042: Seed: `UPDATE users SET is_admin = TRUE WHERE firebase_uid = '<renato_firebase_uid>'`
- [ ] T043: Alembic migration `012_create_api_keys_scans_and_findings.py` — tabelas `api_keys`, `scans`, `scan_findings` com índices
- [ ] T044: Alembic migration `013_create_rule_whitelists.py` — tabela `rule_whitelists`
- [ ] T045: Aplicar migrations em produção: `alembic upgrade head`

### Domain Layer [P]
- [ ] T046: [P] `domain/models.py` — adicionar `ApiKey`, `Scan`, `ScanFinding` (Pydantic, frozen)
- [ ] T047: [P] `domain/exceptions.py` — `ApiKeyNotFoundError`, `ApiKeyRevokedError`, `ApiKeyInvalidError`, `ScanNotFoundError`
- [ ] T048: [P] `domain/models.py` — atualizar `User` com campo `is_admin: bool = False`

### Ports [P]
- [ ] T049: [P] `ports/api_key_repo.py` — `ApiKeyRepoPort` Protocol
- [ ] T050: [P] `ports/scan_repo.py` — `ScanRepoPort` Protocol

### Adapters [P]
- [ ] T051: [P] `adapters/postgres/models.py` — `ApiKeyRow`, `ScanRow`, `ScanFindingRow` ORM rows
- [ ] T052: [P] `adapters/postgres/api_key_repository.py` — `PostgresApiKeyRepository`
- [ ] T053: [P] `adapters/postgres/scan_repository.py` — `PostgresScanRepository` (inclui `create_with_findings`)

### Auth & Dependencies
- [ ] T054: `api/deps.py` — `get_api_key_data()`: detecta prefixo `tlp_`, SHA-256, lookup em `api_keys`, retorna `ApiKeyData`
- [ ] T055: `api/deps.py` — `get_optional_identity()`: detecta anônimo / `tlp_` / `eyJ`, retorna `None | ApiKeyData | FirebaseTokenData`
- [ ] T056: `api/deps.py` — `require_admin()`: Firebase + `user.is_admin == True`, lança 403 se falhar

### Services [P]
- [ ] T057: [P] `domain/services.py` — `ApiKeyService`: `create()` (gera token `tlp_` + SHA-256), `list_by_user()`, `revoke()`, `validate()`, `get_whitelist()`, `add_to_whitelist()`, `remove_from_whitelist()`
- [ ] T058: [P] `domain/services.py` — `ScanService`: `register()` (cria scan + findings), `list_by_user()`, `get_summary()`

### API Endpoints [P]
- [ ] T059: [P] `api/routes/api_keys.py` — `POST /api/v1/api-keys` (Firebase auth, retorna token uma única vez)
- [ ] T060: [P] `api/routes/api_keys.py` — `GET /api/v1/api-keys` (Firebase auth, lista sem revelar hash)
- [ ] T061: [P] `api/routes/api_keys.py` — `DELETE /api/v1/api-keys/{id}` (Firebase auth, revoga key)
- [ ] T062: [P] `api/routes/scans.py` — `POST /api/v1/scans` (API key auth, registra scan + findings)
- [ ] T063: [P] `api/routes/scans.py` — `GET /api/v1/scans` (Firebase auth, lista scans do usuário)
- [ ] T064: [P] `api/routes/scans.py` — `GET /api/v1/scans/summary` (Firebase auth) — apenas skeleton da rota + auth wiring; aggregation SQL implementada em T075
- [ ] T065: Registrar routers em `main.py`
- [ ] T066: Aplicar whitelist em `GET /api/v1/rules/{version}` — quando API key autenticada, filtrar regras em `rule_whitelists`
- [ ] T066b: [P] `api/routes/api_keys.py` — `GET /api/v1/api-keys/{id}/whitelist` (Firebase auth, lista rule_ids suprimidos)
- [ ] T066c: [P] `api/routes/api_keys.py` — `POST /api/v1/api-keys/{id}/whitelist` (Firebase auth, adiciona rule_id à whitelist)
- [ ] T066d: [P] `api/routes/api_keys.py` — `DELETE /api/v1/api-keys/{id}/whitelist/{rule_id}` (Firebase auth, remove regra)

### Workflow Update
- [ ] T067: Adicionar step `Register scan` no `theloop-guard.yml` após o scan:
  ```bash
  curl -s --max-time 3 -X POST https://api.loop.oute.pro/api/v1/scans \
    -H "Authorization: Bearer ${{ secrets.THELOOP_API_TOKEN }}" \
    -H "Content-Type: application/json" \
    -d "{\"repository\":\"$GITHUB_REPOSITORY\",\"branch\":\"$GITHUB_REF_NAME\",
         \"pr_number\":${{ github.event.pull_request.number }},
         \"rules_version\":\"$RULES_VERSION\",\"findings_count\":$FINDINGS_COUNT,
         \"errors_count\":$ERRORS_COUNT,\"warnings_count\":$WARNINGS_COUNT,
         \"duration_ms\":$DURATION_MS,\"findings\":$FINDINGS_JSON}" || true
  ```
- [ ] T068: Montar `FINDINGS_JSON` no workflow: extrair array `[{rule_id, file_path, line, severity}]` do JSON do semgrep

### Tests [P]
- [ ] T069: [P] `tests/unit/domain/test_api_key_service.py` — create, validate, revoke, token format
- [ ] T070: [P] `tests/unit/domain/test_scan_service.py` — register, summary, top_rules
- [ ] T071: [P] `tests/api/test_api_keys.py` — POST/GET/DELETE key CRUD + GET/POST/DELETE whitelist com mocked service
- [ ] T072: [P] `tests/api/test_scans.py` — POST (API key auth), GET/summary (Firebase auth)
- [ ] T073: `pytest --cov=src --cov-fail-under=80` passando
- [ ] T074: Commit + PR Phase 4

---

## Phase 5 — Dashboard de Violations

### Backend
- [ ] T075: Implementar `GET /api/v1/scans/summary` — agrega scans das keys do usuário: `total_scans`, `total_findings`, `scans_by_week` (4 semanas), `top_rules` (top 5 por findings)
- [ ] T076: Testes para `GET /api/v1/scans/summary`

### Frontend
- [ ] T077: Criar `src/lib/services/scans.ts` — `getScansSummary()`, `getScans()` com Firebase auth
- [ ] T078: Criar `src/lib/types/scans.ts` — `ScanSummary`, `ScanEntry`, `WeeklyBucket`, `TopRule`
- [ ] T079: Substituir placeholder em `src/routes/dashboard/+page.svelte` pela implementação real
- [ ] T080: Seção "Stats" — cards: Total Scans, Total Findings, Active Repos (contagem de keys distintas com scans)
- [ ] T081: Seção "Weekly Findings" — sparkline/gráfico simples com `scans_by_week` (últimas 4 semanas)
- [ ] T082: Seção "Top Rules" — lista rankeada das 5 regras que mais disparam com contagem
- [ ] T083: Loading states com skeleton (design tokens existentes)
- [ ] T084: Empty state: sem scans registrados → mensagem + link para `/settings/` (tab Onboarding)
- [ ] T085: `npm run check` + `npm run test -- --run` passando
- [ ] T086: Commit + PR Phase 5

---

## Phase 6 — Admin de Regras na UI

### Backend
- [ ] T086b: `POST /api/v1/rules/versions` — criar versão draft (require_admin); body `{"version":"0.3.0"}`; retorna `{version, status: "draft"}`
- [ ] T087: Aplicar `require_admin` em `POST /api/v1/rules/publish` (endpoint existente)
- [ ] T088: `PUT /api/v1/rules/{version}/rules/{rule_id}` — editar regra individual (require_admin)
- [ ] T088b: `GET /api/v1/admin/metrics` — retorna `active_repos`, `scans_by_week`, `top_languages` (derivado do prefixo do rule_id); require_admin
- [ ] T089: Testes para rotas admin: 403 para não-admin, 200 para admin (publish, edit, metrics)

### Frontend
- [ ] T090: Criar `src/routes/admin/+layout.svelte` — guard: redirect para `/` se `!$profile?.is_admin`
- [ ] T090b: Criar `src/routes/admin/metrics/+page.svelte` — painel de adoção: Active Repos (30d), Scans by Week (4 semanas), Top Languages; dados via `GET /api/v1/admin/metrics`
- [ ] T091: Criar `src/routes/admin/rules/+page.svelte` — lista versões publicadas + botão "New Version"
- [ ] T092: Criar `src/routes/admin/rules/[version]/+page.svelte` — lista regras da versão com botão editar
- [ ] T093: Criar `src/routes/admin/rules/[version]/edit/+page.svelte` — editor: campos `id`, `message`, `severity`, `pattern` (textarea) + preview JSON
- [ ] T094: Criar `src/routes/admin/rules/[version]/publish/+page.svelte` — resumo + botão confirmar publicação
- [ ] T095: `src/lib/services/admin.ts` — `createVersion()`, `publishVersion()`, `editRule()`, `listVersions()`
- [ ] T096: `npm run check` + `npm run test -- --run` passando
- [ ] T097: Commit + PR Phase 6

---

## Phase 7 — Onboarding + API Key Management

### Frontend — Settings (novas abas)
- [ ] T098: Adicionar tabs "API Keys" e "Onboarding" ao array `TABS` em `src/routes/settings/+page.svelte`
- [ ] T099: **Aba "API Keys"** — listar keys: nome, prefix (`tlp_aBc3...`), criada em, último uso, botão "Revoke"
- [ ] T100: **Aba "API Keys"** — criar key: input de nome → POST → modal com token completo + aviso "Save now — this won't be shown again"
- [ ] T101: **Aba "API Keys"** — revogar: dialog de confirmação → DELETE → atualizar lista
- [ ] T101b: **Aba "API Keys"** — gerenciar whitelist de uma key: expandir linha da key → listar regras suprimidas → input para adicionar rule_id → botão remover por regra
- [ ] T102: **Aba "Onboarding"** — selector de key existente (ou criar nova inline)
- [ ] T103: **Aba "Onboarding"** — gerar `theloop-guard.yml` pré-preenchido com a key selecionada em textarea readonly + botão "Copy to clipboard"
- [ ] T103b: Teste unitário: validar que o YAML gerado pelo onboarding passa em `yamllint` (SC-006)
- [ ] T104: **Aba "Onboarding"** — instruções passo a passo: (1) Add secret to GitHub, (2) Copy workflow, (3) Create `.github/workflows/theloop-guard.yml`
- [ ] T105: `src/lib/services/api_keys.ts` — `createApiKey()`, `listApiKeys()`, `revokeApiKey()`, `getWhitelist()`, `addToWhitelist()`, `removeFromWhitelist()`
- [ ] T106: `src/lib/types/api_keys.ts` — `ApiKey`, `CreateApiKeyResponse`
- [ ] T107: `npm run check` + `npm run test -- --run` passando
- [ ] T108: Commit + PR Phase 7

---

## Phase 8 — Regras JS/TS + Go (v0.3.0)

### JS/TS — 15 regras [P]
- [ ] T109: [P] `js-injection-001` — SQL via string concat (knex/raw) + test data
- [ ] T110: [P] `js-injection-002` — `eval()` com input externo + test data
- [ ] T111: [P] `js-injection-003` — `innerHTML` / `dangerouslySetInnerHTML` + test data
- [ ] T112: [P] `js-injection-004` — `child_process.exec` com template string + test data
- [ ] T113: [P] `js-crypto-001` — `crypto.createHash('md5'/'sha1')` + test data
- [ ] T114: [P] `js-crypto-002` — `Math.random()` para tokens/secrets + test data
- [ ] T115: [P] `js-security-001` — JWT hardcoded secret + test data
- [ ] T116: [P] `js-security-002` — CORS `origin: '*'` (express) + test data
- [ ] T117: [P] `js-security-003` — `NODE_TLS_REJECT_UNAUTHORIZED = '0'` + test data
- [ ] T118: [P] `js-security-004` — prototype pollution via `Object.assign({}, req.body)` + test data
- [ ] T119: [P] `js-perf-001` — `await` dentro de loop (N+1 async) + test data
- [ ] T120: [P] `js-config-001` — `console.log` com dados sensíveis (password/token/secret) + test data
- [ ] T121: [P] `js-config-002` — URL hardcoded de produção no código + test data
- [ ] T122: [P] `ts-security-001` — `any` type em dados de entrada externa + test data
- [ ] T123: [P] `ts-security-002` — `as unknown as T` (type assertion forçado) + test data

### Go — 10 regras [P]
- [ ] T124: [P] `go-injection-001` — `fmt.Sprintf` em SQL query + test data
- [ ] T125: [P] `go-injection-002` — `exec.Command` com variável externa + test data
- [ ] T126: [P] `go-injection-003` — `path.Join` com input externo sem validação + test data
- [ ] T127: [P] `go-crypto-001` — `md5.New()` / `sha1.New()` + test data
- [ ] T128: [P] `go-crypto-002` — `math/rand` em vez de `crypto/rand` + test data
- [ ] T129: [P] `go-security-001` — `InsecureSkipVerify: true` + test data
- [ ] T130: [P] `go-security-002` — JWT com secret hardcoded + test data
- [ ] T131: [P] `go-error-001` — `err` ignorado com `_` em operação crítica + test data
- [ ] T132: [P] `go-error-002` — `panic()` em handler HTTP + test data
- [ ] T133: [P] `go-config-001` — `http.ListenAndServe` sem TLS + test data

### Validação + Publicação
- [ ] T134: `semgrep --validate --config .semgrep/theloop-rules.yml` — deve passar com 45 regras
- [ ] T135: `semgrep scan tests/test-data/bad/js/` — confirmar findings esperados (zero false negatives)
- [ ] T136: `semgrep scan tests/test-data/good/js/` — confirmar 0 findings (zero false positives)
- [ ] T137: `semgrep scan tests/test-data/bad/go/` — confirmar findings esperados
- [ ] T138: `semgrep scan tests/test-data/good/go/` — confirmar 0 findings
- [ ] T139: Atualizar `.semgrep/theloop-rules.yml.bak` com todas as 45 regras
- [ ] T140: Publicar v0.3.0 via `POST /api/v1/rules/publish` (admin auth)
- [ ] T141: Commit + PR Phase 8

---

## Phase 9 — Testes, Docs, Polish

### Quality Gates [P]
- [ ] T142: [P] `pytest --cov=src --cov-fail-under=80` passando
- [ ] T143: [P] `mypy src/` strict: 0 erros
- [ ] T144: [P] `ruff check src/ tests/`: 0 erros
- [ ] T145: [P] `npm run check`: 0 erros
- [ ] T146: [P] `npm run lint`: 0 erros
- [ ] T147: [P] `npm run test -- --run`: todos passando

### Docs [P]
- [ ] T148: [P] Atualizar `README.md` — nova seção "API Keys & Scan History", atualizar URLs
- [ ] T149: [P] Atualizar `THELOOP.md` — workflow com step de registro de scan + nova versão v0.3.0
- [ ] T150: [P] Atualizar `CLAUDE.md` — novos modelos (`ApiKey`, `Scan`), novas rotas, auth tiers
- [ ] T151: [P] Atualizar `specs/016-semgrep-platform/spec.md` status → COMPLETE
- [ ] T152: [P] Criar `specs/016-semgrep-platform/CHANGELOG.md` com decisões tomadas durante impl

### Final
- [ ] T153: Rodar `bash scripts/generate-docs.sh` — gate docs-check
- [ ] T154: PR final + code review
- [ ] T155: Merge para `main`
- [ ] T156: Verificar deploy automático no Cloud Run
- [ ] T157: Smoke test em produção: `curl https://api.loop.oute.pro/api/v1/health`, acessar `loop.oute.pro/rules/latest`, verificar Job Summary em PR de teste
- [ ] T158: Atualizar memória do projeto com status COMPLETE da spec-016

---

## Resumo por fase

| Fase | Tasks | Paralel. | Est. dias |
|------|-------|----------|-----------|
| PRÉ-REQ | T000 | — | @renatobardi |
| 1 — Infra | T001–T016 | 1a ∥ 1b | 2 |
| 2 — Quick wins | T017–T027 | — | 2 |
| 3 — Rules page | T028–T040 | parcial | 2 |
| 4 — API keys + scans | T041–T074 (+T066b,c,d) | alta | 3 |
| 5 — Dashboard | T075–T086 (+T086b) | parcial | 3 |
| 6 — Admin UI | T087–T097 (+T088b, T090b) | parcial | 4 |
| 7 — Onboarding | T098–T108 (+T101b, T103b) | — | 3 |
| 8 — JS/TS + Go rules | T109–T141 | muito alta | 6 |
| 9 — Polish | T142–T158 | alta | 3 |
| **Total** | **168 tasks** | | **~28 dias** |
