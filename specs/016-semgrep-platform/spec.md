# Spec-016: Semgrep Platform

**Status:** Ready for implementation  
**Branch:** `feat/016-semgrep-platform`  
**Depende de:** spec-015 (nav/dashboard/profile) mergeada ✅

---

## Contexto

As specs 010–012 entregaram o scanner (Phase A: regras estáticas; Phase B: API + versionamento + 20 regras). O produto funciona mas é invisível: os resultados existem apenas como comentários de PR, sem histórico, sem dashboard, sem onboarding estruturado, sem domínio próprio para a API.

Esta spec transforma o The Loop de scanner em plataforma: histórico persistente de scans, dashboard de violations, página pública de regras, admin de regras pela UI, onboarding self-service, API keys gerenciáveis e expansão para JS/TS e Go.

---

## Functional Requirements

### FR-001: Domínio próprio para a API
A API deve ser acessível em `api.loop.oute.pro` em vez da URL gerada pelo Cloud Run. Todas as referências hardcoded no código e documentação devem ser atualizadas.

### FR-002: Job Summary na GitHub Action
Ao final de cada scan, a Action deve escrever um resumo em `$GITHUB_STEP_SUMMARY` com: status (✅/🔴), contagem de regras verificadas, número de findings, tempo de scan, tabela de findings (quando houver) e dois links fixos (`loop.oute.pro/rules/latest` e `loop.oute.pro`).

**Formato aprovado (sem findings):**
```
## 🔁 The Loop — Incident Guard

✅ No incident patterns detected. Code is clean.

20 rules checked · 0 findings · scan completed in 4s

> Browse active rules → loop.oute.pro/rules/latest
> Protect your codebase → loop.oute.pro
```

**Formato aprovado (com findings):**
```
## 🔁 The Loop — Incident Guard

🔴 2 critical findings — merge blocked

| Severity | Rule          | File       | Line |
|:--------:|---------------|------------|:----:|
| 🔴 ERROR | injection-001 | src/db.py  | 42   |
| 🟡 WARN  | unsafe-001    | src/api.py | 17   |

20 rules checked · 2 findings · scan completed in 4s

> Learn what triggered this → loop.oute.pro/rules/latest
> Protect your codebase → loop.oute.pro
```

### FR-003: Descrição da regra no PR comment
Quando uma regra dispara, o comment do PR deve exibir a descrição/mensagem da regra (`r.extra.message`) inline na tabela, além do ID. O campo já existe no JSON de output do semgrep — sem necessidade de busca adicional.

### FR-004: Página pública `/rules/latest`
Rota pública (sem autenticação) que lista todas as regras da versão ativa: nome, severity, descrição, exemplo de código que dispara. Disponível também em `/rules/[version]` para versões específicas. O link "View rules" no PR comment e no Job Summary deve apontar para esta página.

### FR-005: Histórico de scans
Cada execução do workflow deve registrar o resultado via `POST /api/v1/scans`, autenticado com o `THELOOP_API_TOKEN` existente (API key identifica o projeto/repo no backend). O backend persiste: repositório, branch, PR number, findings count, rules version, duração em ms e timestamp. Dados acessíveis no dashboard do usuário autenticado dono da key.

### FR-006: Dashboard de violations
O dashboard do usuário deve exibir: timeline de scans (últimas 4 semanas), top regras que mais disparam, findings por semana. Timeline e contagens provenientes da tabela `scans`; top regras provenientes da tabela `scan_findings`.

### FR-007: Admin de regras na UI
Usuário com `is_admin = true` pode criar, editar e publicar nova versão de regras pelo dashboard, sem precisar de curl ou acesso direto à API. Fluxo: (1) criar nova versão draft via `POST /api/v1/rules/versions`, (2) editar regras individuais via `PUT /api/v1/rules/{version}/rules/{rule_id}`, (3) publicar via `POST /api/v1/rules/publish`. O campo `is_admin: bool` é adicionado à tabela `users` e setado via migration seed para @renatobardi.

### FR-008: Whitelist por projeto
Repositórios podem suprimir regras específicas sem editar o workflow. Projeto = repositório = API key: a configuração de whitelist é armazenada no backend associada à API key. Um usuário pode ter N keys (uma por repo), cada uma com seu próprio whitelist.

### FR-009: Onboarding self-service
Usuário logado pode gerar e copiar o `workflow.yml` pré-configurado com sua API key, pronto para colar no repositório.

### FR-010: API key management
Usuário logado pode criar e revogar `THELOOP_API_TOKEN` pelo dashboard. Rotação = criar nova key + revogar a antiga (não há endpoint dedicado de rotação — são duas operações sequenciais). Cada key tem nome, data de criação e data do último uso.

### FR-011: Métricas de adoção
Dashboard admin exibe: total de repositórios ativos (com scan nos últimos 30 dias), scans por semana, top linguagens escaneadas. Linguagem é derivada do prefixo do `rule_id` em `scan_findings` (`js-` → JS/TS, `go-` → Go, demais → Python) — sem coluna separada no banco.

### FR-012: Regras JS/TS e Go
Publicar v0.3.0 com 25 novas regras cobrindo JS/TS (15 regras) e Go (10 regras) nas categorias: injection, crypto, security, performance, error handling. Test data (bad/ + good/) para cada linguagem.

---

## Success Criteria

### SC-001: API acessível em `api.loop.oute.pro`
`curl https://api.loop.oute.pro/api/v1/health` retorna `{"status": "ok"}` com HTTPS válido.

### SC-002: Zero referências à URL do Cloud Run no código ativo
`grep -r "us-central1.run.app" apps/ .github/` retorna zero resultados.

### SC-003: Job Summary aparece em toda execução da Action
Toda run do `theloop-guard.yml` grava conteúdo em `$GITHUB_STEP_SUMMARY`, visível na aba Summary da Action.

### SC-004: Página `/rules/latest` acessível sem autenticação
`curl https://loop.oute.pro/rules/latest` retorna HTTP 200 com lista de regras.

### SC-005: Scans registrados no backend
Após execução do workflow, `GET /api/v1/scans` retorna o registro com findings_count correto.

### SC-006: Onboarding gera workflow válido
O YAML gerado pelo tab "Onboarding" em `/settings/` passa em `yamllint` (validado por teste unitário — T103b) e o workflow resultante executa sem erros em um repo de teste.

### SC-007: 25 novas regras validadas
`semgrep --validate --config .semgrep/theloop-rules.yml` passa com 45 regras totais (20 Python + 15 JS/TS + 10 Go).

### SC-008: Cobertura de testes ≥ 80%
`pytest --cov=src --cov-fail-under=80` passa no CI.

### SC-009: Dashboard de violations acessível
Usuário autenticado com pelo menos um scan registrado vê timeline e top rules em `loop.oute.pro/dashboard/`.

### SC-010: Admin consegue publicar nova versão pela UI
Usuário com `is_admin = true` acessa `/admin/rules/`, cria versão, edita regras e clica "Publish" sem usar curl ou API diretamente.

### SC-011: Whitelist aplicada no GET rules
`GET /api/v1/rules/latest` com API key que tem `injection-001` na whitelist retorna lista sem essa regra.

### SC-012: API key rotacionada pelo dashboard
Usuário cria nova key, copia token e revoga a anterior — tudo dentro de `/settings/` aba "API Keys".

### SC-013: Métricas de adoção acessíveis ao admin
`GET /api/v1/admin/metrics` (ou equivalente) retorna `active_repos`, `scans_by_week`, `top_languages` com dados reais.


---

## User Stories

### US-001: Dev vê summary na Action
Como desenvolvedor que abriu um PR, quero ver um resumo do scan diretamente na página da Action (sem precisar buscar no PR comment) para entender rapidamente se meu código tem problemas de segurança.

### US-002: Dev não-assinante descobre o The Loop
Como desenvolvedor que viu o Job Summary ou o PR comment, quero clicar em "loop.oute.pro" e entender o que é o produto para considerar adotar na minha empresa.

### US-003: Dev consulta regras ativas
Como desenvolvedor que recebeu um finding, quero acessar `/rules/latest` para entender o que a regra detecta, ver um exemplo de código problemático e a solução recomendada.

### US-004: Admin publica nova versão de regras
Como administrador do The Loop, quero criar e publicar uma nova versão de regras pelo dashboard sem precisar usar a API diretamente.

### US-005: Cliente configura seu repo
Como cliente recém-cadastrado, quero gerar o workflow YAML com minha API key pelo dashboard e copiá-lo para meu repositório.

### US-006: Cliente gerencia sua API key
Como cliente, quero poder revogar e criar uma nova API key pelo dashboard se suspeitar que a chave foi exposta.

---

## Edge Cases

- Workflow sem `THELOOP_API_TOKEN` no step de fetch de regras: fallback para `.semgrep/theloop-rules.yml.bak` com mensagem clara ("API token not configured, using fallback rules").
- Workflow sem `THELOOP_API_TOKEN` no step de registro de scan: `curl` falha com 401, mas `continue-on-error: true` garante que o CI não seja bloqueado — registro é best-effort.
- `POST /api/v1/scans` com API key inválida: retorna 401, workflow não falha (registro de scan é best-effort, não bloqueia o resultado do scan).
- `/rules/latest` sem versão ativa publicada: retorna página informativa "No rules published yet."
- Admin publica regra com YAML inválido: validação prévia via `semgrep --validate` antes de salvar, retorna erro 422 com detalhes.
- Revogação de API key: imediata. Usuário deve atualizar o secret no repositório antes de revogar a key anterior.

---

## Clarifications

### Session 2026-04-04

- Q: Como o workflow autentica no `POST /api/v1/scans`? → A: O mesmo `THELOOP_API_TOKEN` identifica o cliente — o backend resolve o vínculo pela API key. Zero mudança no workflow.
- Q: Quem é "admin" no FR-007? → A: Campo `is_admin: bool` na tabela `users`, setado via migration seed para @renatobardi. Sem sistema de roles complexo.
- Q: O que é "projeto" no FR-008? → A: Projeto = repositório. Cada API key representa um repo. Um usuário pode ter N keys (uma por repo). Whitelist associado à key, não ao usuário.

---

## Fora do escopo

- Redis cache / multi-instância (spec futura — "Scaling")
- Notificações email/Slack (spec futura)
- Webhook outbound / link incident↔violation (spec futura)
- Multi-repo view agregado (spec futura)
- False positive management (spec futura)
- Regras sugeridas por AI (spec futura)
- Java, C#, PHP, Ruby, Kotlin, Rust, C/C++ (spec-017)
- Severity threshold configurável por projeto (spec futura)

---

## Fases de implementação (visão geral)

| Fase | Conteúdo | Est. dias |
|------|----------|-----------|
| 1 | Infraestrutura: `api.loop.oute.pro` + atualização de URLs | 2 |
| 2 | Quick wins: Job Summary + descrição no PR comment + fix View rules | 2 |
| 3 | Página pública `/rules/latest` | 2 |
| 4 | Histórico de scans: backend + POST /api/v1/scans no workflow | 3 |
| 5 | Dashboard de violations | 3 |
| 6 | Admin de regras na UI | 4 |
| 7 | Onboarding self-service + API key management | 3 |
| 8 | Regras JS/TS + Go (v0.3.0) | 6 |
| 9 | Testes, docs, polish, merge | 3 |

**Total estimado:** ~28 dias

---

## Dependências (Mandamento XIII)

- **Infra GCP:** Static IP existente `34.110.250.203`, Load Balancer `the-loop-urlmap`, cert `the-loop-cert` — extensão para `api.loop.oute.pro`
- **DNS:** A record `api.loop.oute.pro → 34.110.250.203` (feito pelo @renatobardi no Hostinger)
- **DB:** 3 Alembic migrations — ver data model em plan.md:
  - Migration 011: coluna `is_admin BOOLEAN` em `users`
  - Migration 012: tabelas `api_keys` (`id, owner_id, name, key_hash, prefix, last_used_at, revoked_at, created_at`), `scans`, `scan_findings`
  - Migration 013: tabela `rule_whitelists`
- **Auth:** Rotas de admin verificam `user.is_admin == True` via `Depends(require_admin)`
- **Semgrep CLI:** Disponível no runner GitHub Actions (já instalado no workflow atual)
- **CI/CD:** Todos os gates existentes (lint, mypy, pytest, build, Trivy) permanecem obrigatórios

---

**Última atualização:** 2026-04-04  
**Próximo passo:** implementação (Phase 1 — `api.loop.oute.pro`)
