# Vervit Assistant Token Economy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduzir o contexto obrigatório e a repetição textual do Vervit Assistant preservando seus gates de segurança.

**Architecture:** Skills frequentes serão roteadores concisos orientados pelo gate atual. Referências, artefatos e instruções locais serão carregados apenas quando a próxima ação depender deles.

**Tech Stack:** Markdown skills, Python `unittest`.

---

### Task 1: Criar Contrato De Economia

**Files:**
- Modify: `tests/test_skill_interaction_contract.py`

- [x] Adicionar testes que limitem `vervit-assistant-main`, `vervit-especificar-tarefa`, `vervit-implementar-tarefa` e `vervit-init-project`.
- [x] Adicionar testes para carregamento sob demanda e gates preservados.
- [x] Executar `python -m unittest tests.test_skill_interaction_contract -v` e confirmar falha pelos textos atuais.

### Task 2: Compactar Skills Frequentes

**Files:**
- Modify: `skills/vervit-assistant-main/SKILL.md`
- Modify: `skills/vervit-especificar-tarefa/SKILL.md`
- Modify: `skills/vervit-implementar-tarefa/SKILL.md`
- Modify: `skills/vervit-init-project/SKILL.md`
- Modify: `skills/vervit-map-codebase/SKILL.md`

- [x] Remover explicações e fluxos repetidos.
- [x] Tornar leituras de referências, instruções e artefatos condicionais.
- [x] Preservar interação estruturada, segurança e gates.
- [x] Executar o contrato e confirmar aprovação.

### Task 3: Compactar Instruções Geradas

**Files:**
- Modify: `assets/templates/AGENTS.md`
- Modify: `assets/templates/.agents/main-agent.md`

- [x] Remover políticas duplicadas entre os dois templates.
- [x] Fazer `AGENTS.md` apontar para o perfil somente quando necessário.
- [x] Manter idioma, segurança, roteamento Jira e política de entrega.

### Task 4: Verificar E Medir

**Files:**
- Modify: `tests/test_skill_interaction_contract.py`

- [x] Executar `python -m unittest discover -v`.
- [x] Medir palavras dos arquivos antes/depois com o baseline registrado na spec.
- [x] Confirmar redução mínima de 60% no contexto inicial e 40% nas skills frequentes.
