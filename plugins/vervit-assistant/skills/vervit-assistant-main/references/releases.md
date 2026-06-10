# Releases

Use `scripts/release_guard.py`.

- Hotfix: nasce/volta para `main`, incrementa patch e sincroniza `release`.
- Planejado: nasce de `release`; congele escopo, execute regressão, integre em `main`.
- Jira usa `X.Y.Z`; Git usa tag anotada `vX.Y.Z`.
- Breaking: major; feature: minor; bug/improvement: patch.
- Fix Version, merge/push/tag/liberação exigem confirmação explícita.
