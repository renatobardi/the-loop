# Checklist de Validação: Incident CRUD (Phase A)

**PR**: #12
**Como testar**: API via Swagger (`http://localhost:8000/docs`) com token Firebase válido. Frontend via `http://localhost:5173/en/incidents/`.

> **Nota**: O code review encontrou 6 issues que afetam o fluxo end-to-end via frontend (auth stub, SSR fetch). A validação via Swagger (API direta) funciona normalmente.

---

## Backend — API (via Swagger em /docs)

### Infraestrutura

- [ ] Health check: `GET /api/v1/health` retorna `{"status": "ok"}`
- [ ] Migration criou a tabela `incidents` com todas as colunas
- [ ] Extensões pgvector e pg_trgm ativas no PostgreSQL
- [ ] CORS rejeita origens não autorizadas (testar com `curl -H "Origin: http://evil.com"`)

### Create (POST /api/v1/incidents)

- [ ] Criar incidente com campos obrigatórios (title, category, severity, anti_pattern, remediation) retorna 201
- [ ] Resposta inclui id (UUID), version=1, created_at, updated_at, created_by
- [ ] embedding é null na resposta
- [ ] Criar com source_url duplicada retorna 409 com mensagem clara
- [ ] Criar com semgrep_rule_id inválido (ex: "bad_format") retorna 422
- [ ] Criar com semgrep_rule_id válido (ex: "injection-001") retorna 201
- [ ] Criar sem title retorna 422 com erro no campo
- [ ] Criar com title de 500 chars funciona (boundary)
- [ ] Criar com title de 501 chars retorna 422
- [ ] source_url vazia ("") é tratada como null
- [ ] Sem token de auth retorna 401

### List (GET /api/v1/incidents)

- [ ] Lista retorna items[], total, page, per_page
- [ ] Ordenação padrão: created_at DESC (mais recente primeiro)
- [ ] Paginação padrão: page=1, per_page=20
- [ ] `?per_page=5` retorna 5 items com total correto
- [ ] `?per_page=200` é limitado a 100
- [ ] `?category=injection` filtra apenas incidentes dessa categoria
- [ ] `?severity=critical` filtra apenas incidentes critical
- [ ] `?category=injection&severity=high` combina filtros
- [ ] `?q=ReDoS` busca no title, anti_pattern e remediation (case-insensitive)
- [ ] Incidente soft-deleted não aparece na lista
- [ ] Página além do total retorna items=[] com total correto

### Read (GET /api/v1/incidents/{id})

- [ ] Retorna incidente completo (todos os campos) com 200
- [ ] ID inexistente retorna 404
- [ ] Incidente soft-deleted retorna 404

### Update (PUT /api/v1/incidents/{id})

- [ ] Update com version correta retorna 200 e version incrementada (+1)
- [ ] updated_at é atualizado
- [ ] Update com version errada (stale) retorna 409 com current_version
- [ ] Mudar category quando semgrep_rule_id existe retorna 409
- [ ] Mudar source_url para uma já existente retorna 409
- [ ] id, created_at, created_by são imutáveis (ignorados se enviados)
- [ ] Incidente soft-deleted retorna 404

### Soft-Delete (DELETE /api/v1/incidents/{id})

- [ ] Delete retorna 200 com `{"detail": "Incident deleted"}`
- [ ] Incidente deletado tem deleted_at preenchido (verificar no DB)
- [ ] Incidente deletado não aparece mais no GET list nem GET by ID
- [ ] Re-deletar o mesmo incidente retorna 200 (idempotente)
- [ ] Deletar incidente com semgrep_rule_id retorna 409 com mensagem
- [ ] ID inexistente retorna 404

---

## Frontend — UI (via browser)

### Navegação

- [ ] Link "Incidents" aparece no Navbar
- [ ] `/en/incidents/` carrega a lista
- [ ] `/pt/incidents/` carrega a lista (i18n)
- [ ] `/es/incidents/` carrega a lista (i18n)

### Lista de Incidentes

- [ ] Exibe cards com title, category badge, severity badge, organization, data
- [ ] Tags aparecem nos cards
- [ ] Estado vazio mostra mensagem "No incidents found"
- [ ] Filtro por category funciona
- [ ] Filtro por severity funciona
- [ ] Busca por keyword funciona (com debounce ~300ms)
- [ ] "Clear filters" limpa todos os filtros
- [ ] Paginação mostra total, página atual, e navegação
- [ ] Seletor de per_page (10, 20, 50, 100) funciona
- [ ] Skeleton loading aparece durante fetch

### Criar Incidente

- [ ] Formulário exibe todos os campos (obrigatórios marcados com *)
- [ ] Dropdowns de category (12 opções) e severity (4 opções) funcionam
- [ ] Validação client-side impede submit sem campos obrigatórios
- [ ] Após submit com sucesso, redireciona para detalhe do incidente criado
- [ ] Erro de validação exibe mensagem inline sem perder dados preenchidos
- [ ] Erro de source_url duplicada exibe mensagem clara

### Detalhe do Incidente

- [ ] Exibe todos os campos agrupados (Description, Classification, Remediation, Metadata)
- [ ] code_example renderiza em monospace
- [ ] Tags aparecem como badges
- [ ] Severity e category com badges coloridos
- [ ] source_url é um link clicável (abre em nova aba)
- [ ] Botões "Edit" e "Delete" visíveis

### Editar Incidente

- [ ] Formulário pré-preenchido com valores atuais
- [ ] Campos editáveis funcionam normalmente
- [ ] Após submit, redireciona para detalhe com dados atualizados
- [ ] Erro de conflito (version stale) exibe mensagem explicativa

### Deletar Incidente

- [ ] Modal de confirmação aparece ao clicar "Delete"
- [ ] Botão "Cancel" fecha o modal
- [ ] Botão "Delete" no modal executa o soft-delete
- [ ] Após delete, redireciona para a lista
- [ ] Erro de regra ativa (semgrep_rule_id) exibe mensagem no modal

### i18n

- [ ] Todos os labels, botões e mensagens estão traduzidos em EN
- [ ] Todos os labels, botões e mensagens estão traduzidos em PT
- [ ] Todos os labels, botões e mensagens estão traduzidos em ES
- [ ] Trocar idioma no LanguageSelector mantém contexto

---

## Testes Automatizados

- [ ] `pytest tests/unit/` — testes de domain models e exceptions passam
- [ ] `npm run check` — 0 errors no svelte-check
- [ ] `npm run build` — build de produção passa
- [ ] `npm run test -- --run` — 20 testes existentes continuam passando
- [ ] `npm run lint` — 0 errors no ESLint

---

## Bloqueios Conhecidos (Code Review PR #12)

> Estes items VÃO falhar até os fixes do code review serem aplicados:

- [ ] ~~Rate limiting funcional (request: object → precisa ser Request)~~
- [ ] ~~Auth token passado nas requests do frontend (getAuthToken stub)~~
- [ ] ~~SSR funciona sem erro de window.location~~
- [ ] ~~Fetch da API funciona em SSR/produção (relative URL)~~
- [ ] ~~Lista não faz double-load no mount ($effect)~~
- [ ] ~~CLAUDE.md reflete Phase 1 (não Phase 0)~~
