# Workflow Adaptativo

## Selecao E Classificacao

- Liste por padrao issues abertas atribuidas ao usuario atual.
- A classificacao deve ser sugerida pelo agente principal e confirmada pelo usuario.
- `bug`: comportamento incorreto existente.
- `feature`: nova capacidade relevante.
- `improvement`: melhoria pequena e localizada.

## Superpowers

Use `python scripts/workflow_guard.py <tipo>` para conferir o fluxo.

- Bug: `systematic-debugging`, causa raiz, TDD de regressao, review e verificacao.
- Feature: `brainstorming`, plano formal, TDD, review e verificacao.
- Improvement: contexto/plano compactos; TDD obrigatorio quando houver mudanca comportamental; review e verificacao.

## Gates

Antes do codigo:

- classificacao e trilho confirmados;
- branch correta;
- PRD aprovado;
- cenarios manuais publicados no Jira.

Antes de integrar:

- worktree limpa;
- testes automatizados aprovados;
- checklist manual Jira completo;
- review sem problemas criticos/importantes;
- TRACE atualizado.
