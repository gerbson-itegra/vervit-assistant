---
name: vervit-assistant-main
description: Use esta skill como entrada principal para trabalhar em atividades Jira com o padrao Vervit. Ela lista e seleciona issues, confirma classificacao e trilho de entrega, cria branch e PRD, coordena Superpowers/TDD, mantem checklists e rastreabilidade, integra hotfixes e releases planejadas e aplica a politica SemVer.
metadata:
  short-description: Orquestrar desenvolvimento Jira Vervit
---

# Vervit Assistant Main

Esta e a fachada principal do Vervit Assistant. Coordene o ciclo inteiro e delegue etapas especializadas para as demais skills Vervit e Superpowers.

## Pre-Flight Obrigatorio

1. Leia `AGENTS.md`, `.agents/main-agent.md` e `.agents/vervit-assistant.json`.
2. Confirme que a raiz e um repositorio Git com branches `main` e `release`.
3. Bloqueie criacao ou troca de branch quando `git status --porcelain` nao estiver vazio.
4. Verifique `JIRA_BASE_URL`, `JIRA_EMAIL` e `JIRA_API_TOKEN` sem imprimir seus valores.
5. Leia as referencias desta skill antes da etapa correspondente:
   - `references/task-workflow.md`
   - `references/jira-operations.md`
   - `references/provider-routing.md`
   - `references/releases.md`

## Regras Inviolaveis

- Use OpenAI + Superpowers para analise, classificacao, PRD, planejamento, debugging, TDD, cenarios, review, SemVer, merges e liberacao.
- Provedores externos executam somente transformacoes textuais triviais permitidas.
- Nunca envie credenciais, anexos ou binarios para provedores externos.
- Nunca implemente antes de o PRD ser aprovado e o checklist manual existir no Jira.
- Nunca integre com checklist manual pendente ou testes automatizados falhando.
- Nunca execute operacao Jira sensivel, merge, push ou tag sem confirmacao explicita.
- Registre decisoes, operacoes Jira, provedores usados, fallbacks, testes e merges em `.specs/jira/<KEY>/TRACE.md`.

## Fluxo Principal

1. Liste minhas issues abertas pelo executor Jira e permita selecionar uma.
2. Reuna descricao, criterios, comentarios e contexto do projeto.
3. Sugira `bug`, `feature` ou `improvement`; explique e aguarde confirmacao.
4. Sugira `hotfix` ou `planned`; explique impacto e aguarde confirmacao.
5. Calcule o nome da branch com `scripts/release_guard.py`:
   - hotfix: `hotfix/KEY-slug`, baseada em `main`;
   - planejada: `tipo/KEY-slug`, baseada em `release`.
6. Crie `.specs/jira/<KEY>/PRD.md`, `TRACE.md` e `state.json` com `scripts/task_artifacts.py`.
7. Use `vervit-especificar-tarefa`; aguarde aprovacao explicita do PRD.
8. Use Superpowers para definir somente cenarios de validacao manual e publique a secao gerenciada no Jira.
9. Use `vervit-implementar-tarefa` com o fluxo adaptativo retornado por `scripts/workflow_guard.py`.
10. Rode review e verificacao fresca; peca ao desenvolvedor para concluir os cenarios manuais no Jira.
11. Releia a issue e bloqueie integracao enquanto houver item pendente.
12. Siga o trilho de entrega em `references/releases.md`.

## Artefatos Da Tarefa

- `PRD.md`: requisitos aprovados, escopo, criterios, impactos e cenarios manuais.
- `TRACE.md`: log cronologico e auditavel, sem segredos.
- `state.json`: gates estruturados usados por `scripts/workflow_guard.py`.

## Saida

Responda em PT-BR com estado atual, gates completos/pendentes, evidencias de teste, operacoes Jira realizadas, branch/versao e a proxima confirmacao necessaria.
