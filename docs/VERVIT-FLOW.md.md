# Vervit Assistant — Fluxo Completo

## 1. Visão Geral

Vervit Assistant é um **plugin Codex** (OpenCode) que orquestra desenvolvimento orientado a tarefas Jira com gates de qualidade, roteamento multicamada de provedores e releases SemVer com guardrails. Ele opera como um agente dentro do ecossistema OpenCode, usando skills especializadas para cada fase.

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenCode (Codex)                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │             vervit-assistant-main                     │  │
│  │  (orquestrador: seleciona gate, delega, verifica)     │  │
│  └────┬──────────┬──────────┬──────────┬─────────────────┘  │
│       │          │          │          │                    │
│  ┌────▼──┐ ┌─────▼──────┐ ┌▼────────┐ ┌▼──────────────┐   │
│  │init   │ │map-codebase│ │especificar│ │implementar    │   │
│  │project│ │           │ │tarefa   │ │tarefa        │   │
│  └───────┘ └───────────┘ └─────────┘ └───────────────┘   │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            Scripts Python (CLI auxiliar)              │  │
│  │  init_project  provider_router  jira_executor         │  │
│  │  release_guard  workflow_guard  task_artifacts        │  │
│  │  detect_project  vervit_env                           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Plugin (plugin.json)

```json
{
  "name": "vervit-assistant",
  "skills": "./skills/",
  "interface": {
    "displayName": "Vervit Assistant",
    "defaultPrompt": [
      "Inicie o Vervit Assistant neste projeto",
      "Configure o Jira e liste minhas atividades",
      "Mostre as ações disponíveis no Vervit Assistant"
    ]
  }
}
```

O plugin se registra no OpenCode. Quando instalado, as skills ficam disponíveis e prompts padrão aparecem na interface.

## 3. Onboarding — `vervit-init-project`

```
Usuário: "Inicie o Vervit Assistant neste projeto"
```

**Fluxo:**

```
1. Leia instruções locais (AGENTS.md) se existirem
2. Execute: python scripts/init_project.py --target <projeto>
3. Revise arquivos criados e .agents/vervit-onboarding.json
4. Verifique dependências (Superpowers, TLC, Jira)
5. Se Jira pendente: peça para criar .env.vervit.local
6. Informe status ao usuário
```

### O script `init_project.py` faz:

```
a) Detecta: linguagem, framework, CI, Docker, testes, etc.
b) Cria: .specs/codebase/ (STACK, ARCHITECTURE, CONVENTIONS, STRUCTURE, TESTING, INTEGRATIONS, CONCERNS)
c) Cria: .specs/project/ (PROJECT, ROADMAP, STATE)
d) Cria: .specs/releases/NEXT/ (RELEASE, TRACE, state.json)
e) Cria: .specs/jira/README.md
f) Cria: AGENTS.md, .agents/main-agent.md, .agents/vervit-assistant.json
g) Cria: .env.vervit.example
h) Cria: .agents/vervit-onboarding.json (estado)
i) Detecta dependências: Superpowers, TLC Spec-Driven, Atlassian/Jira
```

### Arquivos gerados:

```
projeto/
├── AGENTS.md                    # Guia local do agente
├── .env.vervit.example          # Template de variáveis
├── .gitignore                   # .env.vervit.local adicionado
├── .agents/
│   ├── main-agent.md            # Perfil do agente principal
│   ├── vervit-assistant.json    # Config (Jira, git, providers)
│   └── vervit-onboarding.json   # Estado do onboarding
├── .specs/
│   ├── codebase/
│   │   ├── STACK.md             # Stack detectada
│   │   ├── ARCHITECTURE.md      # Arquitetura inicial
│   │   ├── CONVENTIONS.md       # Convenções Vervit
│   │   ├── STRUCTURE.md         # Diretórios principais
│   │   ├── TESTING.md           # Comandos de teste
│   │   ├── INTEGRATIONS.md      # Integrações detectadas
│   │   └── CONCERNS.md          # Riscos iniciais
│   ├── project/
│   │   ├── PROJECT.md           # Descrição do projeto
│   │   ├── ROADMAP.md           # Próximos passos
│   │   └── STATE.md             # Estado do projeto
│   ├── jira/README.md           # Issues Jira
│   └── releases/
│       ├── README.md            # Releases
│       └── NEXT/
│           ├── RELEASE.md       # Notas da próxima release
│           ├── TRACE.md         # Rastreamento
│           └── state.json       # Estado da release
```

### `.agents/vervit-assistant.json` — configuração:

```json
{
  "schemaVersion": 1,
  "jira": {
    "projectKey": "PROJ",
    "baseUrlEnv": "JIRA_BASE_URL",
    "emailEnv": "JIRA_EMAIL",
    "apiTokenEnv": "JIRA_API_TOKEN"
  },
  "git": {
    "mainBranch": "main",
    "releaseBranch": "release"
  },
  "providers": []
}
```

### Dependências detectadas:

```python
dependencies = {
    "superpowers": { "status": "ready"|"incomplete", "missingSkills": [...] },
    "tlc": { "status": "available"|"pending", "mode": "optional" },
    "atlassian": { "status": "available"|"pending", "connector": {...}, "rest": {...} },
    "skillSources": { ... }
}
```

---

## 4. Arquitetura de Skills

Cada skill é um agente especializado no OpenCode:

```
skills/
├── vervit-assistant-main/        ← Orquestrador principal
│   ├── SKILL.md                  # Instruções do agente
│   └── references/
│       ├── task-workflow.md      # Fluxo adaptativo (bug/feature/improvement)
│       ├── jira-operations.md    # Operações Jira
│       ├── provider-routing.md   # Roteamento de provedores
│       └── releases.md           # Política de releases
├── vervit-init-project/          ← Onboarding
│   └── SKILL.md
├── vervit-map-codebase/          ← Mapeamento técnico
│   └── SKILL.md
├── vervit-especificar-tarefa/    ← PRD + critérios
│   └── SKILL.md
└── vervit-implementar-tarefa/    ← Código + testes
    └── SKILL.md
```

---

## 5. Ciclo de Tarefa — `vervit-assistant-main`

O orquestrador é o ponto de entrada para qualquer atividade Jira.

### Gates (checkpoints obrigatórios):

```
GATE 1: Confirmar tipo da tarefa
        ├── feature → fluxo completo (brainstorming, plano, TDD)
        ├── improvement → fluxo compacto
        └── bug → systematic-debugging + causa raiz

GATE 2: PRD aprovado e checklist manual publicado
        Antes de implementar, exige:
        - PRD revisado e aprovado
        - Checklist de validação manual publicado no Jira

GATE 3: Checklist completo, testes e review
        Antes de integrar, exige:
        - Todos os itens do checklist marcados
        - Testes automatizados passando
        - Review concluído

GATE 4: Operações sensíveis (Jira, merge, push, tag)
        Toda ação remota exige confirmação explícita do usuário
```

### Fluxo de contexto sob demanda:

```
1. Reuse contexto disponível (não releia arquivos)
2. Para tarefa existente: leia .specs/jira/<KEY>/state.json
3. Abra PRD.md para especificar/implementar
4. TRACE.md: somente para auditar ou registrar marco
5. Carregue referência necessária:
   - task-workflow.md → para fluxo
   - jira-operations.md → para Jira
   - provider-routing.md → para provedor externo
   - releases.md → para integração/liberação
6. Delegue para vervit-especificar-tarefa ou vervit-implementar-tarefa
   somente quando a etapa começar
```

---

## 6. Especificação — `vervit-especificar-tarefa`

```
Entrada: tarefa Jira selecionada
Saída: PRD.md atualizado com especificação completa
```

### Fluxo:

```
1. Leia state.json da tarefa
2. Abra PRD.md existente (se houver)
3. Reúna contexto do código relevante
4. Separe:
   - Fatos encontrados (evidências)
   - Inferências (conclusões com base nos fatos)
   - Decisões confirmadas (aprovadas pelo usuário)
5. Defina:
   - Escopo (o que será feito)
   - Critérios de aceitação (testáveis)
   - Impactos técnicos (arquivos, módulos)
   - Riscos
   - Cenários manuais executáveis (checklist)
6. Atualize PRD.md
7. Aguarde aprovação explícita do usuário
```

### Regras:

- Prefira `request_user_input` para perguntas
- Nunca grave perguntas pendentes
- Não altere Jira nem TRACE.md
- Não implemente código
- Use Superpowers brainstorming para escopo grande

---

## 7. Implementação — `vervit-implementar-tarefa`

```
Entrada: tarefa com PRD aprovado e checklist publicado
Saída: código implementado, testes passando
```

### Fluxo:

```
1. Leia state.json
2. Bloqueie se não tiver PRD aprovado ou checklist publicado
3. Abra PRD.md
4. Leia somente código e testes relevantes
5. Siga o fluxo:
   - Bug: systematic-debugging (causa raiz → correção → regressão)
   - Feature: plano de implementação formal → TDD → código
   - Improvement: fluxo compacto (plano leve → código)
6. Use TDD para mudança comportamental (teste falha → código → teste passa)
7. Implemente
8. Faça review
9. Execute verificação fresca (testes limpos)
10. Devolva ao agente principal:
    - Arquivos alterados
    - Testes (unitários, integração)
    - Riscos identificados
    - Bloqueios
```

### Regras:

- Implemente o menor escopo aprovado
- Não abra nem atualize TRACE.md
- Não faça commit, push, merge, tag ou transição Jira
- Prefira `request_user_input` para perguntas
- Nunca grave perguntas pendentes

---

## 8. Scripts Python

### `scripts/provider_router.py` — Roteamento de provedores

```
Uso: python scripts/provider_router.py <config> <task> <payload> [--jira-content]

Tarefas permitidas (apenas textuais triviais):
  issue-summary        → resumo de issue
  checkpoint-draft     → rascunho de checkpoint
  fact-extraction      → extração de fatos
  release-notes        → notas de release
  test-results-summary → resumo de testes
  regression-summary   → resumo de regressão

Tarefas PROIBIDAS (exigem agente principal):
  análise, decisões, PRD, planejamento, código,
  review, SemVer, Jira sensível, integração
```

**Arquitetura:**

```
ProviderRouter
├── providers[] (ordenados por prioridade)
├── adapters:
│   ├── openai-compatible → POST /v1/chat/completions (Bearer auth)
│   └── ollama → POST /api/chat (localhost:11434)
├── sanitize_payload(): remove secrets, binários
├── circuit breaker: 3 falhas → suspenso 15min
└── fallback: se todos falham → retorna "openai-primary"
```

**Config (`.agents/vervit-assistant.json`):**

```json
{
  "providers": [
    {
      "id": "meu-ollama",
      "priority": 1,
      "adapter": "ollama",
      "endpoint": "http://localhost:11434",
      "model": "llama3",
      "allowedTasks": ["issue-summary", "release-notes"],
      "jiraContentConsent": false,
      "enabled": true
    }
  ]
}
```

### `scripts/jira_executor.py` — Operações Jira REST

```
Uso: python scripts/jira_executor.py plan <operation> <payload>
     python scripts/jira_executor.py auto <operation> <payload>
     python scripts/jira_executor.py execute <plan.json> [--confirm-hash]
```

**Operações:**

| Operação | Automática? | Sensível? |
|---|---|---|
| get_issue | sim | não |
| get_project | sim | não |
| list_my_open_issues | sim | não |
| list_project_versions | sim | não |
| list_transitions | sim | não |
| comment_checkpoint | sim | não |
| update_checklist | sim | não |
| create_issue | não | sim |
| transition_issue | não | sim |
| link_issues | não | sim |
| create_version | não | sim |
| apply_fix_version | não | sim |
| release_version | não | sim |
| edit_issue | não | sim |

**Operações sensíveis exigem:**
1. `plan` → gera JSON com `operation`, `payload`, `hash`
2. Usuário confirma hash
3. `execute` com `--confirm-hash=<hash>`

**Checklist gerenciado:**
- Delimitado por `[[VERVIT-CHECKLIST-START]]` e `[[VERVIT-CHECKLIST-END]]`
- Formato ADF (Atlassian Document Format)
- Atualizável sem perder estados anteriores
- `checklist_complete()` verifica se 100% DONE

### `scripts/release_guard.py` — Guardiões de Release

```
Uso: python scripts/release_guard.py bump <current_version> <level>
     python scripts/release_guard.py guard <next_version> <issues.json>
```

**Bump SemVer:**
- `major` → X+1.0.0 (breaking)
- `minor` → X.Y+1.0 (feature/story/epic)
- `patch` → X.Y.Z+1 (bug/improvement)

**Política de release:**
- **Hotfix**: nasce de `main` → `hotfix/KEY-slug` → `main` → tag `vX.Y.Z` → sincroniza `release`
- **Planejado**: nasce de `release` → congelamento de escopo → regressão → merge em `main` → tag → sincroniza `release`
- Fix Version no Jira: `vX.Y.Z - YYYY-MM-DD`
- Tag Git anotada: `vX.Y.Z`

### `scripts/workflow_guard.py` — Validação de Gates

```
Uso: python scripts/workflow_guard.py <task_type>
```

Valida:
- Tipo: bug, feature ou improvement
- Trilho: hotfix ou planned
- Branch correta
- PRD aprovado antes de código
- Checklist completo antes de integrar

### `scripts/task_artifacts.py` — Artefatos de tarefa

```
Uso: python scripts/task_artifacts.py <comando> <issue_key> [dados]
```

Gerencia:
- `.specs/jira/<KEY>/PRD.md`
- `.specs/jira/<KEY>/PLAN.md`
- `.specs/jira/<KEY>/TESTS.md`
- `.specs/jira/<KEY>/CHECKLIST.md`
- `.specs/jira/<KEY>/state.json`
- `.specs/jira/<KEY>/TRACE.md`

### `scripts/detect_project.py` — Detecção de stack

Analisa:
- Linguagem (Node, Python, Rust, Go, TypeScript)
- Package manager (npm, pip, cargo, go mod)
- Frameworks (React, Vue, Next, Express, Fastify, NestJS, Prisma, etc.)
- CI/CD (GitHub Actions, GitLab CI, Jenkins)
- Docker (Dockerfile, docker-compose)
- Testes (Jest, Mocha, Vitest, pytest, unittest)
- Convenções existentes

---

## 9. Roteamento Multicamada

```
                    ┌─────────────────────────┐
                    │   Agente Principal      │
                    │   (OpenCode / Codex)     │
                    │   Análise, PRD, Código,  │
                    │   Review, SemVer, Jira   │
                    └────────────┬────────────┘
                                 │
                    Tarefa textual trivial?
                    (resumo, release notes, fatos)
                                 │
                    ┌────────────▼────────────┐
                    │    ProviderRouter        │
                    │    (provider_router.py)  │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
       ┌────────────┐    ┌────────────┐    ┌────────────┐
       │ Ollama     │    │ OpenAI-    │    │ Outros     │
       │ (local)    │    │ Compatible │    │ (custom)   │
       │ Llama 3    │    │ GPT,       │    │            │
       │ Grátis     │    │ DeepSeek,  │    │            │
       │            │    │ Gemini     │    │            │
       └────────────┘    └────────────┘    └────────────┘
               │                 │                 │
               └─────────────────┼─────────────────┘
                                 ▼
                        Fallback: agente principal
                        (se todos provedores falharem)
```

### Regras de segurança:

1. Payload é sanitizado: remove secrets, binários, credenciais
2. Tarefas proibidas nunca são roteadas externamente
3. Conteúdo Jira só vai se `jiraContentConsent = true`
4. Circuit breaker: 3 falhas consecutivas → suspenso 15 min

---

## 10. Release — Fluxo Completo

```
┌────────────────────────────────────────────────────────────┐
│                    RELEASE PIPELINE                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  HOTFIX:                                                   │
│  ┌──────┐    ┌──────────────┐    ┌──────┐    ┌─────────┐  │
│  │ main │───►│hotfix/KEY-slug│───►│ main │───►│ tag     │  │
│  │      │    │              │    │      │    │ vX.Y.Z  │  │
│  └──────┘    └──────────────┘    └──────┘    └─────────┘  │
│                                        │                   │
│                                        ▼                   │
│                                  ┌──────────┐              │
│                                  │ sincroniza│             │
│                                  │ release   │             │
│                                  └──────────┘              │
│                                                            │
│  PLANEJADO:                                                │
│  ┌─────────┐   ┌──────────────┐   ┌──────┐   ┌─────────┐ │
│  │ release │──►│ regressão    │──►│ main │──►│ tag     │ │
│  │ (tarefas)│   │ geral       │   │      │   │ vX.Y.Z  │ │
│  └─────────┘   └──────────────┘   └──────┘   └─────────┘ │
│                                        │                   │
│                                        ▼                   │
│                                  ┌──────────┐              │
│                                  │ sincroniza│             │
│                                  │ release   │             │
│                                  └──────────┘              │
└────────────────────────────────────────────────────────────┘
```

### Passos:

```
1. release_guard.py calcula bump (major/minor/patch)
2. release_guard.py valida issues (tipos, consistência)
3. Cria Fix Version no Jira
4. Atribui Fix Version às issues
5. Executa regressão (git log, build, testes)
6. Gera release notes (via provider_router ou agente principal)
7. Cria tag anotada git vX.Y.Z
8. Push tag
9. Marca version como released no Jira
```

---

## 11. Estrutura de Diretórios do Plugin

```
vervit-assistant/
├── .codex-plugin/
│   └── plugin.json              # Manifesto do plugin
├── assets/
│   └── templates/               # Templates de onboarding
│       ├── AGENTS.md
│       ├── .env.vervit.example
│       ├── .agents/
│       │   ├── main-agent.md
│       │   └── vervit-assistant.json
│       └── .specs/
│           ├── codebase/        # (7 arquivos: stack, arch, conventions...)
│           ├── project/         # (3 arquivos: project, roadmap, state)
│           ├── jira/README.md
│           └── releases/        # (NEXT/ com release, trace, state)
├── scripts/                     # Python CLI
│   ├── init_project.py          # Onboarding
│   ├── detect_project.py        # Detecção de stack
│   ├── provider_router.py       # Roteamento de provedores
│   ├── jira_executor.py         # Operações Jira REST
│   ├── release_guard.py         # SemVer e releases
│   ├── workflow_guard.py        # Validação de gates
│   ├── task_artifacts.py        # Artefatos de tarefa
│   └── vervit_env.py            # Ambiente (env vars + .env.local)
├── skills/                      # Agentes OpenCode
│   ├── vervit-assistant-main/
│   │   ├── SKILL.md
│   │   └── references/          # (4 arquivos)
│   ├── vervit-init-project/SKILL.md
│   ├── vervit-map-codebase/SKILL.md
│   ├── vervit-especificar-tarefa/SKILL.md
│   └── vervit-implementar-tarefa/SKILL.md
└── tests/                       # Testes Python
```

---

## 12. Resumo do Fluxo Operacional

```
USUÁRIO                            OPENCODE + VERVIT
──────                             ──────────────────
   │                                    │
   │ "Inicie o Vervit Assistant"         │
   ├────────────────────────────────────►│
   │                                    │
   │                              vervit-init-project
   │                              ├── detecta stack
   │                              ├── cria .specs/
   │                              ├── cria .agents/
   │                              └── detecta dependências
   │                                    │
   │ "Liste minhas tarefas"             │
   ├────────────────────────────────────►│
   │                              vervit-assistant-main
   │                              ├── jira_executor.py: list_my_open_issues
   │                              └── retorna lista formatada
   │                                    │
   │ "Iniciar PROJ-123"                │
   ├────────────────────────────────────►│
   │                              vervit-especificar-tarefa
   │                              ├── lê state.json, PRD.md
   │                              ├── reúne contexto
   │                              ├── produz especificação
   │                              └── aguarda aprovação
   │                                    │
   │ "Aprovado"                         │
   ├────────────────────────────────────►│
   │                              vervit-implementar-tarefa
   │                              ├── PRD aprovado? ✓
   │                              ├── checklist publicado? ✓
   │                              ├── debugging/plano/TDD
   │                              ├── implementa
   │                              ├── testa
   │                              └── revisa
   │                                    │
   │ "Preparar release"                 │
   ├────────────────────────────────────►│
   │                              release_guard.py
   │                              ├── calcula bump
   │                              ├── regressão
   │                              ├── release notes
   │                              ├── tag git
   │                              ├── fix version Jira
   │                              └── libera
```
