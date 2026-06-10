# Onboarding Readiness And Skill Sources Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Detectar prontidao real das dependencias de onboarding e sincronizar skills por suas fontes Git originais quando solicitado.

**Architecture:** Concentrar deteccao e sincronizacao em funcoes pequenas de `scripts/init_project.py`, injetando ambiente e caminhos nos testes. Gerar um unico snapshot de dependencias por execucao e reutiliza-lo no estado e na documentacao.

**Tech Stack:** Python standard library, unittest, Git CLI.

---

### Task 1: Deteccao real de dependencias

**Files:**
- Modify: `scripts/init_project.py`
- Test: `tests/test_init_project.py`

- [ ] Escrever testes falhando para Superpowers completo/incompleto, TLC e Atlassian/Jira.
- [ ] Executar `python -m unittest tests.test_init_project -v` e confirmar as falhas esperadas.
- [ ] Implementar busca de skills e snapshot de dependencias.
- [ ] Executar os testes focados e confirmar sucesso.

### Task 2: Sincronizacao de fontes Git

**Files:**
- Modify: `scripts/init_project.py`
- Test: `tests/test_init_project.py`

- [ ] Escrever testes falhando para clone, pull fast-forward e checkout sujo.
- [ ] Executar os testes focados e confirmar as falhas esperadas.
- [ ] Implementar catalogo, parser `NAME=URL` e sincronizacao segura.
- [ ] Executar os testes focados e confirmar sucesso.

### Task 3: Estado, CLI e documentacao

**Files:**
- Modify: `scripts/init_project.py`
- Modify: `README.md`
- Modify: `skills/vervit-init-project/SKILL.md`
- Test: `tests/test_init_project.py`

- [ ] Escrever teste falhando para o estado e `INTEGRATIONS.md` gerados.
- [ ] Implementar reutilizacao do snapshot e opcoes CLI.
- [ ] Atualizar README e contrato da skill.
- [ ] Executar `python -m unittest discover -s tests -v`.
- [ ] Executar o validador do plugin.
