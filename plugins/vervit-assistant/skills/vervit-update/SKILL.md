---
name: vervit-update
description: Atualizar Vervit, sincronizar skills, migrar estrutura.
metadata:
  short-description: Atualizar Vervit e projeto
---

## Fluxo
1. `cd C:\Vervit\vervit-assistant && git pull`
2. `set PYTHONPATH=C:\Vervit\vervit-assistant && python -m cli update --target <projeto>`
3. Informe o que mudou

## Regras
- Se projeto não iniciado: use `request_user_input` (fallback: `pergunta textual`)
- Não confirme git pull fast-forward
- Conflitos: reporte e pare
- Nunca peça credenciais no chat
- Não faça commit, push ou deploy
