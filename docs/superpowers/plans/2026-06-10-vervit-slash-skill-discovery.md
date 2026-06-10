# Vervit Slash Skill Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Exibir as cinco skills do Vervit individualmente ao filtrar `/vervit` no menu slash do Codex app.

**Architecture:** Manter as skills distribuídas exclusivamente pelo plugin e adicionar metadados nativos `agents/openai.yaml` com nomes visíveis iniciados por `Vervit:`. Um teste de contrato valida a presença, unicidade e empacotamento desses metadados.

**Tech Stack:** Codex plugin skills, YAML de metadados, Python `unittest`.

---

### Task 1: Contrato de descoberta das skills

**Files:**
- Create: `tests/test_skill_discovery.py`
- Create: `skills/*/agents/openai.yaml`

- [x] **Step 1: Escrever teste que exige metadados nas cinco skills**

O teste deve ler os arquivos como texto, validar `display_name` e
`short_description`, exigir o prefixo `Vervit:` e confirmar nomes únicos.

- [x] **Step 2: Executar o teste e confirmar falha**

Run: `python -m unittest tests.test_skill_discovery -v`

Expected: `FAIL` porque os arquivos `agents/openai.yaml` ainda não existem.

- [x] **Step 3: Adicionar os cinco arquivos de metadados**

Criar:

- `skills/vervit-assistant-main/agents/openai.yaml`
- `skills/vervit-init-project/agents/openai.yaml`
- `skills/vervit-map-codebase/agents/openai.yaml`
- `skills/vervit-especificar-tarefa/agents/openai.yaml`
- `skills/vervit-implementar-tarefa/agents/openai.yaml`

Todos devem usar `interface.display_name` iniciado por `Vervit:` e uma
`interface.short_description` específica.

- [x] **Step 4: Executar o teste e confirmar sucesso**

Run: `python -m unittest tests.test_skill_discovery -v`

Expected: `OK`.

### Task 2: Empacotamento e documentação

**Files:**
- Modify: `tests/test_skill_discovery.py`
- Modify: `README.md`
- Regenerate: `plugins/vervit-assistant/skills/**`

- [x] **Step 1: Adicionar teste que exige metadados no pacote**

O teste deve reconstruir o pacote com `build_marketplace_plugin.py` e comparar
cada `agents/openai.yaml` de origem com sua cópia em
`plugins/vervit-assistant/skills/`.

- [x] **Step 2: Executar o teste e confirmar falha**

Run: `python -m unittest tests.test_skill_discovery -v`

Expected: `FAIL` antes de reconstruir o pacote.

- [x] **Step 3: Reconstruir o pacote e documentar `/vervit`**

Run: `python scripts/build_marketplace_plugin.py`

Atualizar `README.md` explicando que `/vervit` filtra as cinco skills
habilitadas após instalar o plugin e abrir uma nova thread.

- [x] **Step 4: Executar verificações finais**

Run:

```powershell
python -m unittest discover -s tests -v
node --test tests/install-cli.test.mjs
python C:\Users\gerbs\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py C:\Vervit\vervit-assistant
git diff --check
```

Expected: todos os comandos terminam com código `0`.
