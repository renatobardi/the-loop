# The Loop Constitution

**Status**: IMUTÁVEL — Requer dupla verificação de @renatobardi
para qualquer alteração.
**Criado**: 2026-03-30
**Última verificação**: 2026-03-31

> **AVISO**: Este documento contém mandamentos constitucionais do
> projeto The Loop. Nenhuma IA, automação ou contribuidor pode
> alterar, contornar ou ignorar estas regras. Qualquer alteração
> requer aprovação EXPLÍCITA e DUPLA de @renatobardi (confirmação
> verbal + aprovação de PR).

## Core Principles

### I. Trunk-Based Development

O projeto segue **Trunk-Based Development** com as seguintes
regras invioláveis:

- `main` é a única branch de longa duração
- Todo código chega a `main` exclusivamente via Pull Request
- **Push direto em `main` é PROIBIDO** — sem exceções
- Deploy para produção é **automático** após merge em `main`
- Merge só acontece após: aprovação obrigatória + todos os
  status checks passarem

### II. Design System Imutável

O projeto mantém um **design system forte e centralizado**:

- Tokens de design (cores, tipografia, spacing, border-radius,
  shadows) são definidos em `packages/ui/` (ou
  `apps/web/src/lib/ui/`)
- Componentes base seguem exclusivamente os tokens definidos
- **Nenhuma alteração visual pode ser feita fora do design
  system**
- Qualquer mudança em tokens ou componentes do design system
  requer PR dedicado com aprovação de @renatobardi
- Componentes de página consomem o design system — nunca
  definem estilos ad-hoc que contradigam os tokens

### III. Taxonomia de Branches

Toda branch segue a taxonomia abaixo. Branches fora deste
padrão serão rejeitadas:

| Prefixo | Uso | Exemplo |
|---------|-----|---------|
| `feat/` | Novas funcionalidades | `feat/waitlist-form` |
| `fix/` | Correções de bugs | `fix/email-validation` |
| `hotfix/` | Correções urgentes em produção | `hotfix/firestore-rules` |
| `chore/` | Infra, CI, docs, configs | `chore/ci-lint-step` |

- Nomes em **kebab-case**, descritivos, em inglês
- Sem branches de longa duração além de `main`

### IV. Main Protegida

A branch `main` possui as seguintes proteções obrigatórias no
GitHub:

- **Require pull request before merging**: ativado
- **Required approvals**: mínimo 1 (obrigatoriamente
  @renatobardi)
- **Require status checks to pass**: ativado (lint, type-check,
  testes, build)
- **No force push**: ativado
- **No deletion**: ativado
- **Require signed commits**: ativado
- **CODEOWNERS**: `* @renatobardi` — owner obrigatório de todos
  os arquivos

### V. Merge Controlado por @renatobardi

- **@renatobardi é o único responsável por mergear PRs em
  `main`** — sem exceções
- Review pode ser feito por qualquer contribuidor, IA ou
  automação — o gate de qualidade são os CI checks
  (Mandamento VII), não o approval humano
- Nenhum PR pode ser mergeado sem TODOS os status checks
  passarem (lint, type-check, test, build, vuln scan,
  docs-check)
- @renatobardi decide quando e se o merge acontece

### VI. Sem Ambiente de Dev

- O projeto possui **um único ambiente: produção**
- Não existe ambiente de desenvolvimento, staging, ou preview
  permanente
- `main` = produção. Sempre.
- Todo código mergeado em `main` vai para produção
  automaticamente
- Isso exige que o CI seja **extremamente rigoroso** (ver
  Mandamento VII)

### VII. CI Rigoroso (Gates Obrigatórios)

Todo PR MUST passar por TODOS os gates abaixo antes de
permitir merge:

#### Lint

- **Python**: Ruff (com regras estritas)
- **TypeScript/Svelte**: ESLint + Prettier

#### Type Check

- **Python**: mypy em modo strict
- **TypeScript**: strict mode ativado no tsconfig.json

#### Testes

- **Python**: pytest (com cobertura mínima definida por fase)
- **Frontend**: vitest (unit) + playwright (e2e quando
  aplicável)

#### Build

- Docker build MUST completar sem erros nem warnings
- SvelteKit build MUST completar sem erros

#### Segurança

- **Vulnerability scan**: trivy ou grype em dependências e
  Docker images
- **Secret scanning**: ativo no GitHub

Se QUALQUER gate falhar, o merge é bloqueado. Sem exceções.

### VIII. Segurança Mandatória

#### Camada 1 — Repositório (GitHub)

- Branch protection em `main` com todas as regras do
  Mandamento IV
- CODEOWNERS com @renatobardi como owner obrigatório
- Signed commits obrigatórios (GPG ou SSH)
- Dependabot ativo para dependências Python e Node.js
  (security updates automáticos)
- Secret scanning ativo para detectar tokens/keys commitados
- GitHub Actions com permissions restrito ao mínimo necessário
  (principle of least privilege)

#### Camada 2 — CI/CD Pipeline

- Todos os gates do Mandamento VII são obrigatórios
- Nenhum secret hardcoded — tudo via GitHub Secrets (CI) e
  GCP Secret Manager (runtime)
- Docker images: base images oficiais, multi-stage builds,
  non-root user
- Vulnerability scan (trivy/grype) em toda build

#### Camada 3 — Aplicação (Runtime)

- **HTTPS only**: TLS forçado em todo tráfego, HSTS headers
- **CSP headers**: Content Security Policy restritiva
- **CORS**: configuração explícita, NUNCA wildcard `*`
- **Rate limiting**: desde a landing page (proteção contra
  abuse no endpoint de waitlist)
- **Input validation**: Pydantic v2 (backend) e Zod ou
  equivalente (frontend) — nunca confiar em input do client
- **Firebase Security Rules**: Firestore com rules restritivas
  — waitlist permite somente write, nunca read público

#### Camada 4 — Infraestrutura (GCP)

- **Workload Identity Federation**: GitHub Actions autentica
  no GCP sem service account keys — zero keys no repositório
- **IAM least privilege**: cada serviço com service account
  própria e permissões mínimas
- **Secret Manager**: todos os secrets gerenciados via GCP
  Secret Manager
- **VPC / Ingress rules**: Cloud Run com ingress restrito
  quando aplicável
- **Audit logging**: Cloud Audit Logs ativo para rastrear
  ações na infra

### IX. Clean Code

Todo código do projeto segue os princípios de **Clean Code**
sem exceção:

- **Funções pequenas e single responsibility**: cada função
  faz uma coisa e faz bem
- **Nomes descritivos**: variáveis, funções, arquivos e
  módulos têm nomes que explicam o que são/fazem — sem
  abreviações obscuras
- **Zero código morto**: nenhum código comentado, funções não
  utilizadas ou imports órfãos
- **DRY pragmático**: eliminar duplicação real, mas preferir
  repetição a abstrações prematuras
- **Separação clara de responsabilidades**: cada
  arquivo/módulo tem um propósito único e definido
- **Sem magic numbers/strings**: constantes nomeadas para todo
  valor que não seja autoexplicativo
- **Testes como documentação**: testes MUST descrever o
  comportamento esperado de forma legível

Violações de Clean Code são motivo suficiente para rejeitar
um PR.

### X. Arquitetura Hexagonal (a partir da Fase 1)

A partir da Fase 1 (quando o produto real começar), o projeto
adota **Arquitetura Hexagonal (Ports & Adapters)**:

- **Domain layer** (entidades, value objects, domain services):
  zero dependências externas — só Python puro
- **Ports** (interfaces): definem contratos que o domain
  espera — sem implementação
- **Adapters** (implementações): conectam ports a tecnologias
  concretas (PostgreSQL, Vertex AI, GitHub API, Firebase)
- Hexagonal se aplica **somente em boundaries reais** onde
  existem múltiplas implementações ou dependências externas
  pesadas
- **NÃO criar interfaces especulativas**: se há só uma
  implementação e nenhuma razão concreta para abstração, não
  crie um port

**Na Fase 0** (landing page + waitlist): Clean Code é
suficiente. Hexagonal não se aplica porque não existem domain
entities nem boundaries reais.

**Justificativa de cada boundary MUST ser documentada** na
Complexity Tracking table do plan.md de cada fase.

### XI. Pasta .project/ (Histórico do Projeto)

O projeto mantém uma pasta **`.project/`** na raiz do
repositório com o histórico completo de decisões, specs e
documentação de cada fase:

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

Regras invioláveis:

- **Nenhum arquivo em `.project/` pode ser deletado** —
  documentos obsoletos vão para `.project/archive/`
- Cada fase tem seu próprio diretório com spec, plan e tasks
  independentes
- Decisões arquiteturais (ADRs) são registradas em
  `decisions/` dentro da fase relevante
- Esta pasta é **pública** — faz parte do repositório e é
  visível para qualquer contribuidor

### XII. Documentação e Código

A documentação do projeto é tratada com o mesmo rigor que o
código:

- **README.md** na raiz e em cada app/package MUST estar
  sempre atualizado
- **Alterações estruturais** (novos endpoints, novos
  componentes, mudanças de arquitetura) MUST vir acompanhadas
  de atualização de docs no mesmo PR
- O CI inclui um gate **`docs-check`** que:
  1. Executa `scripts/generate-docs.sh` para regenerar partes
     automáticas dos docs
  2. Verifica via `git diff --exit-code` se o output commitado
     está atualizado
  3. Verifica se paths monitorados (routes/, components/, etc.)
     foram alterados sem touch nos docs correspondentes
- Se o gate `docs-check` falhar, o **merge é bloqueado**
- Docs estáticas (CONSTITUTION.md, specs, ADRs) são mantidas
  manualmente e validadas por PR review
- Docs semi-geradas (READMEs, lista de endpoints, estrutura de
  pastas) usam scripts de geração

### XIII. Dependências no Plano de Execução

**Toda dependência** de uma feature — backend, infraestrutura,
APIs externas, bancos de dados, alterações em serviços
existentes, DNS, secrets, CI/CD — MUST fazer parte explícita
do plano de execução (spec, plan e tasks).

#### Infraestrutura e Serviços

- **Provisionamento**: Cloud Run, Cloud SQL, Artifact Registry,
  Secret Manager, IAM, DNS — MUST estar como tasks ANTES das
  tasks de código
- **CI/CD**: novos jobs de qualidade e deploy MUST ser criados
  no mesmo PR ou antes do código que depende deles
- **Secrets**: variáveis de ambiente e service accounts MUST
  estar configurados antes do deploy

#### APIs e Integrações Externas

- **APIs de terceiros**: se a feature consome uma API externa,
  o plano MUST incluir: configuração de credenciais, tratamento
  de erros/indisponibilidade, e fallback/degradação graciosa
- **APIs internas**: se o frontend depende de um backend novo,
  as tasks MUST cobrir deploy do backend ANTES de mergear o
  frontend que o consome
- **Alterações em serviços existentes**: migração de banco,
  mudança de schema, novos endpoints — MUST estar no plano com
  ordem de execução explícita

#### Degradação Graciosa

- Se uma dependência (backend, API, banco) ainda não existe no
  momento do deploy, o sistema MUST renderizar um estado vazio
  funcional — **NUNCA erro 500 ou página em branco**
- Validação pré-merge: nenhum código que dependa de algo
  inexistente pode ser mergeado sem (a) a dependência estar
  provisionada ou (b) degradação graciosa implementada e
  testada em produção

**Código sem suas dependências é código quebrado.** O spec,
plan e tasks MUST cobrir toda a cadeia: dependências → infra →
CI/CD → deploy → código → validação em produção.

**Origem**: Mandamento adicionado após o incidente
006-incident-crud, onde 74 tasks de código foram geradas sem
nenhuma task de provisionamento (Cloud SQL, Cloud Run para API,
secrets, CI jobs). Resultado: backend mergeado mas nunca
deployado, frontend quebrado em produção através de 4 PRs de
hotfix consecutivos.

## Aplicação e Verificação

- Este documento MUST existir na raiz do repositório como
  `CONSTITUTION.md`
- Todo PR que toque em CI, infra, segurança ou design system
  MUST referenciar o mandamento relevante
- Nenhuma IA (Claude, Copilot, ou qualquer outra) pode sugerir
  ou executar ações que violem estes mandamentos
- Em caso de dúvida, a decisão é NÃO fazer até que
  @renatobardi aprove explicitamente

## Governance

- Este documento é **IMUTÁVEL** — alterações requerem dupla
  verificação de @renatobardi
- Procedimento de emenda: (1) solicitação explícita de
  @renatobardi, (2) PR dedicado referenciando mandamentos
  afetados, (3) confirmação dupla antes do merge
- Versionamento segue Semantic Versioning: MAJOR para remoção
  ou redefinição de mandamentos, MINOR para novos mandamentos
  ou expansão material, PATCH para clarificações e ajustes de
  redação
- Todo PR que toque em CI, infra, segurança ou design system
  MUST verificar compliance com os mandamentos relevantes
- Compliance review: revisão obrigatória por @renatobardi em
  todo PR

**Assinatura**: Este documento foi criado e aprovado por
@renatobardi em 2026-03-30. Qualquer alteração requer:
(1) solicitação explícita de @renatobardi, (2) confirmação
dupla antes do merge.

**Version**: 1.1.0 | **Ratified**: 2026-03-30 | **Last Amended**: 2026-03-31
