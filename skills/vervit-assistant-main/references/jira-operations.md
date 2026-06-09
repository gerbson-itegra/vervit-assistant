# Operacoes Jira

Use `scripts/jira_executor.py` com Jira Cloud REST v3.

## Credenciais

- `JIRA_BASE_URL`
- `JIRA_EMAIL`
- `JIRA_API_TOKEN`

Nunca registre ou envie os valores para agentes/provedores.

## Operacoes Automaticas Permitidas

- `get_issue`
- `get_project`
- `list_my_open_issues`
- `list_project_versions`
- `list_transitions`
- `comment_checkpoint`
- `update_checklist`

Exemplo:

```powershell
python scripts/jira_executor.py auto list_my_open_issues '@.specs/jira/list-open-payload.json'
python scripts/jira_executor.py auto get_project '@.specs/jira/project-payload.json'
```

## Operacoes Sensíveis

Crie um plano, apresente operacao/payload/hash ao usuario e execute somente apos confirmacao:

- `create_issue`
- `transition_issue`
- `link_issues`
- `create_version`
- `apply_fix_version`
- `release_version`
- `edit_issue`

```powershell
python scripts/jira_executor.py plan create_version '@.specs/releases/NEXT/create-version-payload.json' --output .specs/releases/NEXT/jira-plan.json
python scripts/jira_executor.py execute .specs/releases/NEXT/jira-plan.json --confirm-hash <hash-confirmado>
```

No Windows PowerShell, prefira sempre `@arquivo.json`; JSON inline pode perder aspas ao ser passado para processos nativos.

O checklist usa uma secao gerenciada delimitada. Preserve todo o restante da descricao e nunca remova cenarios silenciosamente.
