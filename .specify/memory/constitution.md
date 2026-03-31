<!--
  ============================================================
  SYNC IMPACT REPORT
  ============================================================
  Version change: 1.0.0 -> 1.1.0 (MINOR — new principle)

  Added principles (1 new, 13 total):
    - XIII. Dependencias no Plano de Execucao

  Modified principles: None
  Removed principles: None
  Added sections: None
  Removed sections: None

  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ no update needed
      (Constitution Check section is dynamic, references this file)
    - .specify/templates/spec-template.md ✅ no update needed
      (generic template, no constitution-specific references)
    - .specify/templates/tasks-template.md ⚠ should reference
      Mandamento XIII when generating dependency/infra tasks
    - .specify/templates/commands/*.md ✅ no command files exist

  Follow-up TODOs:
    - tasks-template.md could add dependency task phase guidance
      referencing Mandamento XIII (not blocking)
  ============================================================
-->

# The Loop Constitution

**Status**: IMUTAVEL — Requer dupla verificacao de @renatobardi
para qualquer alteracao.
**Criado**: 2026-03-30
**Ultima verificacao**: 2026-03-31

> **AVISO**: Este documento contem mandamentos constitucionais do
> projeto The Loop. Nenhuma IA, automacao ou contribuidor pode
> alterar, contornar ou ignorar estas regras. Qualquer alteracao
> requer aprovacao EXPLICITA e DUPLA de @renatobardi (confirmacao
> verbal + aprovacao de PR).

## Core Principles

### I. Trunk-Based Development

O projeto segue **Trunk-Based Development** com as seguintes
regras inviolaveis:

- `main` e a unica branch de longa duracao
- Todo codigo chega a `main` exclusivamente via Pull Request
- **Push direto em `main` e PROIBIDO** — sem excecoes
- Deploy para producao e **automatico** apos merge em `main`
- Merge so acontece apos: aprovacao obrigatoria + todos os
  status checks passarem

### II. Design System Imutavel

O projeto mantem um **design system forte e centralizado**:

- Tokens de design (cores, tipografia, spacing, border-radius,
  shadows) sao definidos em `packages/ui/` (ou
  `apps/web/src/lib/ui/`)
- Componentes base seguem exclusivamente os tokens definidos
- **Nenhuma alteracao visual pode ser feita fora do design
  system**
- Qualquer mudanca em tokens ou componentes do design system
  requer PR dedicado com aprovacao de @renatobardi
- Componentes de pagina consomem o design system — nunca
  definem estilos ad-hoc que contradigam os tokens

### III. Taxonomia de Branches

Toda branch segue a taxonomia abaixo. Branches fora deste
padrao serao rejeitadas:

| Prefixo | Uso | Exemplo |
|---------|-----|---------|
| `feat/` | Novas funcionalidades | `feat/waitlist-form` |
| `fix/` | Correcoes de bugs | `fix/email-validation` |
| `hotfix/` | Correcoes urgentes em producao | `hotfix/firestore-rules` |
| `chore/` | Infra, CI, docs, configs | `chore/ci-lint-step` |

- Nomes em **kebab-case**, descritivos, em ingles
- Sem branches de longa duracao alem de `main`

### IV. Main Protegida

A branch `main` possui as seguintes protecoes obrigatorias no
GitHub:

- **Require pull request before merging**: ativado
- **Required approvals**: minimo 1 (obrigatoriamente
  @renatobardi)
- **Require status checks to pass**: ativado (lint, type-check,
  testes, build)
- **No force push**: ativado
- **No deletion**: ativado
- **Require signed commits**: ativado
- **CODEOWNERS**: `* @renatobardi` — owner obrigatorio de todos
  os arquivos

### V. Merge Controlado por @renatobardi

- **@renatobardi e o unico responsavel por mergear PRs em
  `main`** — sem excecoes
- Review pode ser feito por qualquer contribuidor, IA ou
  automacao — o gate de qualidade sao os CI checks
  (Mandamento VII), nao o approval humano
- Nenhum PR pode ser mergeado sem TODOS os status checks
  passarem (lint, type-check, test, build, vuln scan,
  docs-check)
- @renatobardi decide quando e se o merge acontece

### VI. Sem Ambiente de Dev

- O projeto possui **um unico ambiente: producao**
- Nao existe ambiente de desenvolvimento, staging, ou preview
  permanente
- `main` = producao. Sempre.
- Todo codigo mergeado em `main` vai para producao
  automaticamente
- Isso exige que o CI seja **extremamente rigoroso** (ver
  Mandamento VII)

### VII. CI Rigoroso (Gates Obrigatorios)

Todo PR MUST passar por TODOS os gates abaixo antes de
permitir merge:

#### Lint

- **Python**: Ruff (com regras estritas)
- **TypeScript/Svelte**: ESLint + Prettier

#### Type Check

- **Python**: mypy em modo strict
- **TypeScript**: strict mode ativado no tsconfig.json

#### Testes

- **Python**: pytest (com cobertura minima definida por fase)
- **Frontend**: vitest (unit) + playwright (e2e quando
  aplicavel)

#### Build

- Docker build MUST completar sem erros nem warnings
- SvelteKit build MUST completar sem erros

#### Seguranca

- **Vulnerability scan**: trivy ou grype em dependencias e
  Docker images
- **Secret scanning**: ativo no GitHub

Se QUALQUER gate falhar, o merge e bloqueado. Sem excecoes.

### VIII. Seguranca Mandatoria

#### Camada 1 — Repositorio (GitHub)

- Branch protection em `main` com todas as regras do
  Mandamento IV
- CODEOWNERS com @renatobardi como owner obrigatorio
- Signed commits obrigatorios (GPG ou SSH)
- Dependabot ativo para dependencias Python e Node.js
  (security updates automaticos)
- Secret scanning ativo para detectar tokens/keys commitados
- GitHub Actions com permissions restrito ao minimo necessario
  (principle of least privilege)

#### Camada 2 — CI/CD Pipeline

- Todos os gates do Mandamento VII sao obrigatorios
- Nenhum secret hardcoded — tudo via GitHub Secrets (CI) e
  GCP Secret Manager (runtime)
- Docker images: base images oficiais, multi-stage builds,
  non-root user
- Vulnerability scan (trivy/grype) em toda build

#### Camada 3 — Aplicacao (Runtime)

- **HTTPS only**: TLS forcado em todo trafego, HSTS headers
- **CSP headers**: Content Security Policy restritiva
- **CORS**: configuracao explicita, NUNCA wildcard `*`
- **Rate limiting**: desde a landing page (protecao contra
  abuse no endpoint de waitlist)
- **Input validation**: Pydantic v2 (backend) e Zod ou
  equivalente (frontend) — nunca confiar em input do client
- **Firebase Security Rules**: Firestore com rules restritivas
  — waitlist permite somente write, nunca read publico

#### Camada 4 — Infraestrutura (GCP)

- **Workload Identity Federation**: GitHub Actions autentica
  no GCP sem service account keys — zero keys no repositorio
- **IAM least privilege**: cada servico com service account
  propria e permissoes minimas
- **Secret Manager**: todos os secrets gerenciados via GCP
  Secret Manager
- **VPC / Ingress rules**: Cloud Run com ingress restrito
  quando aplicavel
- **Audit logging**: Cloud Audit Logs ativo para rastrear
  acoes na infra

### IX. Clean Code

Todo codigo do projeto segue os principios de **Clean Code**
sem excecao:

- **Funcoes pequenas e single responsibility**: cada funcao
  faz uma coisa e faz bem
- **Nomes descritivos**: variaveis, funcoes, arquivos e
  modulos tem nomes que explicam o que sao/fazem — sem
  abreviacoes obscuras
- **Zero codigo morto**: nenhum codigo comentado, funcoes nao
  utilizadas ou imports orfaos
- **DRY pragmatico**: eliminar duplicacao real, mas preferir
  repeticao a abstracoes prematuras
- **Separacao clara de responsabilidades**: cada
  arquivo/modulo tem um proposito unico e definido
- **Sem magic numbers/strings**: constantes nomeadas para todo
  valor que nao seja autoexplicativo
- **Testes como documentacao**: testes MUST descrever o
  comportamento esperado de forma legivel

Violacoes de Clean Code sao motivo suficiente para rejeitar
um PR.

### X. Arquitetura Hexagonal (a partir da Fase 1)

A partir da Fase 1 (quando o produto real comecar), o projeto
adota **Arquitetura Hexagonal (Ports & Adapters)**:

- **Domain layer** (entidades, value objects, domain services):
  zero dependencias externas — so Python puro
- **Ports** (interfaces): definem contratos que o domain
  espera — sem implementacao
- **Adapters** (implementacoes): conectam ports a tecnologias
  concretas (PostgreSQL, Vertex AI, GitHub API, Firebase)
- Hexagonal se aplica **somente em boundaries reais** onde
  existem multiplas implementacoes ou dependencias externas
  pesadas
- **NAO criar interfaces especulativas**: se ha so uma
  implementacao e nenhuma razao concreta para abstracao, nao
  crie um port

**Na Fase 0** (landing page + waitlist): Clean Code e
suficiente. Hexagonal nao se aplica porque nao existem domain
entities nem boundaries reais.

**Justificativa de cada boundary MUST ser documentada** na
Complexity Tracking table do plan.md de cada fase.

### XI. Pasta .project/ (Historico do Projeto)

O projeto mantem uma pasta **`.project/`** na raiz do
repositorio com o historico completo de decisoes, specs e
documentacao de cada fase:

```
.project/
├── phases/
│   ├── 00-landing/
│   │   ├── spec.md
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   └── decisions/
│   ├── 01-foundation/
│   └── ...
├── research/
└── archive/
```

Regras inviolaveis:

- **Nenhum arquivo em `.project/` pode ser deletado** —
  documentos obsoletos vao para `.project/archive/`
- Cada fase tem seu proprio diretorio com spec, plan e tasks
  independentes
- Decisoes arquiteturais (ADRs) sao registradas em
  `decisions/` dentro da fase relevante
- Esta pasta e **publica** — faz parte do repositorio e e
  visivel para qualquer contribuidor

### XII. Documentacao e Codigo

A documentacao do projeto e tratada com o mesmo rigor que o
codigo:

- **README.md** na raiz e em cada app/package MUST estar
  sempre atualizado
- **Alteracoes estruturais** (novos endpoints, novos
  componentes, mudancas de arquitetura) MUST vir acompanhadas
  de atualizacao de docs no mesmo PR
- O CI inclui um gate **`docs-check`** que:
  1. Executa `scripts/generate-docs.sh` para regenerar partes
     automaticas dos docs
  2. Verifica via `git diff --exit-code` se o output commitado
     esta atualizado
  3. Verifica se paths monitorados (routes/, components/, etc.)
     foram alterados sem touch nos docs correspondentes
- Se o gate `docs-check` falhar, o **merge e bloqueado**
- Docs estaticas (CONSTITUTION.md, specs, ADRs) sao mantidas
  manualmente e validadas por PR review
- Docs semi-geradas (READMEs, lista de endpoints, estrutura de
  pastas) usam scripts de geracao

### XIII. Dependencias no Plano de Execucao

**Toda dependencia** de uma feature — backend, infraestrutura,
APIs externas, bancos de dados, alteracoes em servicos
existentes, DNS, secrets, CI/CD — MUST fazer parte explicita
do plano de execucao (spec, plan e tasks).

#### Infraestrutura e Servicos

- **Provisionamento**: Cloud Run, Cloud SQL, Artifact Registry,
  Secret Manager, IAM, DNS — MUST estar como tasks ANTES das
  tasks de codigo
- **CI/CD**: novos jobs de qualidade e deploy MUST ser criados
  no mesmo PR ou antes do codigo que depende deles
- **Secrets**: variaveis de ambiente e service accounts MUST
  estar configurados antes do deploy

#### APIs e Integracoes Externas

- **APIs de terceiros**: se a feature consome uma API externa,
  o plano MUST incluir: configuracao de credenciais, tratamento
  de erros/indisponibilidade, e fallback/degradacao graciosa
- **APIs internas**: se o frontend depende de um backend novo,
  as tasks MUST cobrir deploy do backend ANTES de mergear o
  frontend que o consome
- **Alteracoes em servicos existentes**: migracao de banco,
  mudanca de schema, novos endpoints — MUST estar no plano com
  ordem de execucao explicita

#### Degradacao Graciosa

- Se uma dependencia (backend, API, banco) ainda nao existe no
  momento do deploy, o sistema MUST renderizar um estado vazio
  funcional — **NUNCA erro 500 ou pagina em branco**
- Validacao pre-merge: nenhum codigo que dependa de algo
  inexistente pode ser mergeado sem (a) a dependencia estar
  provisionada ou (b) degradacao graciosa implementada e
  testada em producao

**Codigo sem suas dependencias e codigo quebrado.** O spec,
plan e tasks MUST cobrir toda a cadeia: dependencias → infra →
CI/CD → deploy → codigo → validacao em producao.

**Origem**: Mandamento adicionado apos o incidente
006-incident-crud, onde 74 tasks de codigo foram geradas sem
nenhuma task de provisionamento (Cloud SQL, Cloud Run para API,
secrets, CI jobs). Resultado: backend mergeado mas nunca
deployado, frontend quebrado em producao atraves de 4 PRs de
hotfix consecutivos.

## Aplicacao e Verificacao

- Este documento MUST existir na raiz do repositorio como
  `CONSTITUTION.md`
- Todo PR que toque em CI, infra, seguranca ou design system
  MUST referenciar o mandamento relevante
- Nenhuma IA (Claude, Copilot, ou qualquer outra) pode sugerir
  ou executar acoes que violem estes mandamentos
- Em caso de duvida, a decisao e NAO fazer ate que
  @renatobardi aprove explicitamente

## Governance

- Este documento e **IMUTAVEL** — alteracoes requerem dupla
  verificacao de @renatobardi
- Procedimento de emenda: (1) solicitacao explicita de
  @renatobardi, (2) PR dedicado referenciando mandamentos
  afetados, (3) confirmacao dupla antes do merge
- Versionamento segue Semantic Versioning: MAJOR para remocao
  ou redefinicao de mandamentos, MINOR para novos mandamentos
  ou expansao material, PATCH para clarificacoes e ajustes de
  redacao
- Todo PR que toque em CI, infra, seguranca ou design system
  MUST verificar compliance com os mandamentos relevantes
- Compliance review: revisao obrigatoria por @renatobardi em
  todo PR

**Assinatura**: Este documento foi criado e aprovado por
@renatobardi em 2026-03-30. Qualquer alteracao requer:
(1) solicitacao explicita de @renatobardi, (2) confirmacao
dupla antes do merge.

**Version**: 1.1.0 | **Ratified**: 2026-03-30 | **Last Amended**: 2026-03-31
