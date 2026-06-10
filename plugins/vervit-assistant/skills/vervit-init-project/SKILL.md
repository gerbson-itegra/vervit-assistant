---
name: vervit-init-project
description: Use quando o usuário pedir inicialização, onboarding ou configuração do padrão Vervit em um projeto.
metadata:
  short-description: Inicializar projeto Vervit
---

# Vervit Init Project

## Primeira Execução

Apresente ações: configurar/listar Jira, mapear projeto, iniciar tarefa ou preparar release. Se Jira estiver pendente, oriente copiar `.env.vervit.example` para `.env.vervit.local` e preencher `JIRA_BASE_URL`, `JIRA_EMAIL` e `JIRA_API_TOKEN` localmente; nunca peça segredo.

## Fluxo

1. Leia instruções locais apenas se afetarem a ação.
2. Rode `python C:\Vervit\vervit-assistant\scripts\init_project.py --target <projeto>`.
3. Revise saídas e `.agents/vervit-onboarding.json`.
4. Verifique Rovo se exposto; Jira ausente não bloqueia.
5. Use `--install-skills` após autorização. Reinicie o Codex após instalar/atualizar skills.

## Regras

- Não sobrescreva `AGENTS.md` ou `.agents/main-agent.md`; preserve trabalho local.
- Não faça commit, push, deploy ou migração.
- Superpowers é padrão; TLC, somente quando pedido.
- Nunca imprima credenciais Jira.
- Prefira `request_user_input`; permita pergunta textual se necessário/indisponível. Nunca grave perguntas pendentes.

Use `vervit-assistant-main` para Jira posterior. Informe mudanças, verificação e status.
