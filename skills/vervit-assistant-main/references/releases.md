# Hotfix E Release Planejada

## Politica SemVer

- Jira Fix Version: `X.Y.Z`
- Tag Git anotada: `vX.Y.Z`
- Memoria local: `.specs/releases/X.Y.Z/`
- Breaking change: major.
- Presenca de feature: minor.
- Somente bugs/improvements: patch.
- Hotfix: patch.

Use `scripts/release_guard.py` para calcular/validar a versao. Nunca aceite versao duplicada ou incompatível.

## Hotfix

1. Criar Fix Version apos confirmacao.
2. Criar `hotfix/KEY-slug` a partir de `main`.
3. Concluir gates da tarefa.
4. Confirmar commit, push e merge `--no-ff` em `main`.
5. Confirmar tag anotada `vX.Y.Z` e push.
6. Mesclar `main` em `release`, validar e enviar.
7. Aplicar/liberar Fix Version e fechar issue somente apos verificacao.

## Release Planejada

1. Manter uma unica issue central `Proxima Release` e `.specs/releases/NEXT/`.
2. Integrar tarefas validadas em `release` e fecha-las apos o merge.
3. No inicio da regressao, congelar escopo.
4. Calcular SemVer, criar Fix Version e aplica-la a todas as tarefas.
5. Renomear issue central para `Release X.Y.Z`.
6. Gerar checklist de regressao geral focado nas tarefas e impactos.
7. Bloquear publicacao ate regressao manual, testes automatizados e release notes estarem completos.
8. Confirmar merge `release` em `main`, tag anotada e push.
9. Mesclar `main` em `release`, validar e enviar.
10. Liberar Fix Version e fechar issue central.
