---
name: vervit-implementar-tarefa
description: Use esta skill, normalmente delegada por vervit-assistant-main, para implementar uma tarefa Jira Vervit a partir do PRD aprovado e do checklist manual publicado. Aplique o fluxo Superpowers confirmado, TDD para toda mudanca comportamental, valide e devolva evidencias sem integrar branches por conta propria.
metadata:
  short-description: Implementar tarefa Jira Vervit
---

# Vervit Implementar Tarefa

Use esta skill para implementar uma tarefa Jira usando o Markdown/spec salvo como fonte de verdade.

## Fluxo

1. Leia o prompt preparado por `vervit-assistant-main`.
2. Abra `.specs/jira/<KEY>/PRD.md`, `TRACE.md` e `state.json`.
3. Confirme que PRD esta aprovado e que os cenarios manuais ja foram publicados no Jira.
4. Se a especificacao estiver insuficiente, volte para esclarecimento, brainstorming ou plano antes de editar codigo.
5. Use Superpowers em modo adaptativo: feature com plano formal, improvement com plano compacto, bug com systematic-debugging.
6. Use TDD para bug, feature e toda melhoria comportamental.
7. Implemente seguindo os padroes existentes do projeto.
8. Rode testes, review e verificacao antes de declarar conclusao.
9. Atualize o TRACE com decisoes, riscos, testes e desvios.

## Regras

- Interaja quando uma decisao de produto, UX, dados, permissao ou teste nao estiver clara.
- Prefira padroes existentes no repositorio.
- Nao faca commit, push, merge, tag ou transicao Jira; devolva evidencias para `vervit-assistant-main`.
- Mantenha o escopo restrito a tarefa.
- Registre desvios da spec antes de implementa-los.

## Saida Esperada

Entregue a implementacao validada, liste arquivos alterados, testes executados e qualquer pendencia ou pergunta aberta.
