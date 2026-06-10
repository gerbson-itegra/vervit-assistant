---
name: vervit-assistant-main
description: Use quando uma atividade Jira Vervit precisar ser selecionada, especificada, implementada, integrada ou liberada.
metadata:
  short-description: Orquestrar atividade Jira Vervit
---

# Vervit Assistant Main

## Contexto Sob Demanda

- Reuse contexto; não releia arquivos.
- Leia `state.json` primeiro; `PRD.md` ao especificar/implementar; `TRACE.md` ao auditar/registrar marco.
- Sob demanda, carregue `task-workflow.md`, `jira-operations.md`, `provider-routing.md` ou `releases.md`.
- Delegue skills somente ao iniciar a etapa.

## Gates

- Confirme tipo, trilho e branch antes dos artefatos.
- Exija PRD aprovado e checklist manual publicado antes de implementar.
- Exija checklist completo, testes e review antes de integrar.
- Jira sensível, merge, push e tag exigem confirmação explícita.
- Preserve trabalho local; nunca exponha credenciais, anexos ou binários.

Prefira `request_user_input`; use uma pergunta textual quando necessário ou indisponível.
Registre no `TRACE.md` apenas marcos confirmados. Informe mudanças, evidências, bloqueios e próximo gate.
