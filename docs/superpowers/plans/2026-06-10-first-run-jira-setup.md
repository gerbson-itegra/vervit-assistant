# First Run Jira Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adicionar configuração Jira local segura e primeira execução guiada, depois reinstalar o plugin.

**Architecture:** `init_project.py` cria templates e estado de onboarding; um carregador dotenv mínimo fornece credenciais aos scripts sem sobrescrever o ambiente.

**Tech Stack:** Python, Markdown skills, Codex plugin manifest.

---

### Task 1: Contrato RED

- [x] Testar criação de `.env.vervit.example`, proteção no `.gitignore` e ausência de segredos.
- [x] Testar carregamento de `.env.vervit.local` e precedência do ambiente.
- [x] Testar estado `firstRun` e instruções da skill.
- [x] Confirmar falhas antes da implementação.

### Task 2: Configuração E First Run

- [x] Criar carregador dotenv seguro.
- [x] Integrar carregamento em onboarding e executor Jira.
- [x] Gerar exemplo, proteção Git e estado de primeira execução.
- [x] Atualizar skill, README e prompts do manifesto.

### Task 3: Verificação E Instalação

- [x] Executar suíte completa.
- [x] Validar plugin.
- [x] Atualizar cachebuster.
- [x] Reinstalar `vervit-assistant@personal`.
