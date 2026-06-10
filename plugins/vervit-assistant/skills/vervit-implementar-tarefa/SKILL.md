---
name: vervit-implementar-tarefa
description: Use quando uma tarefa Jira Vervit tiver PRD aprovado e checklist manual publicado e estiver pronta para implementação.
metadata:
  short-description: Implementar tarefa Jira Vervit
---

# Vervit Implementar Tarefa

1. Leia `state.json`; bloqueie sem PRD aprovado ou checklist manual publicado.
2. Abra `PRD.md` e somente código/testes relevantes.
3. Siga o estado: debugging para bug, plano para feature, fluxo compacto para improvement.
4. Use TDD em mudança comportamental; implemente, revise e verifique.
5. Devolva mudanças, testes, riscos e bloqueios.

Prefira `request_user_input`; permita uma pergunta textual se necessário ou indisponível. Nunca grave perguntas pendentes. Não abra/atualize `TRACE.md` nem faça commit, push, merge, tag ou transição Jira.
