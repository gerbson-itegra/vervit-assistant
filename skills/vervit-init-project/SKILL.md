---
name: vervit-init-project
description: Use esta skill quando o usuario pedir "/init Vervit", "inicializar projeto Vervit", "configurar padrao Vervit", onboarding completo de projeto, mapear codebase inicial, preparar AGENTS.md, criar .specs, verificar Jira/Atlassian ou instalar/configurar dependencias do fluxo Vervit.
metadata:
  short-description: Onboarding completo Vervit para projetos Codex
---

# Vervit Init Project

Inicialize um projeto existente para trabalhar com Codex no padrao Vervit.

## Objetivo

Criar um onboarding completo e seguro:

- mapear stack, estrutura, testes, integracoes e riscos do codebase;
- criar memoria tecnica em `.specs/`;
- criar ou sugerir `AGENTS.md` e `.agents/main-agent.md`;
- verificar prontidao de Superpowers e Atlassian Rovo;
- preparar `vervit-assistant-main`, executor Jira REST e politica de releases;
- criar configuracao segura em `.agents/vervit-assistant.json`;
- verificar ou registrar TLC Spec-Driven como complemento opcional;
- deixar Jira pendente quando nao houver conexao, sem bloquear o onboarding;
- explicar os tres fluxos de trabalho Vervit: feature grande, melhoria pequena e bug fix.

## Pre-Requisitos Guiados

Plugins Codex nao possuem uma dependencia obrigatoria automatica confiavel. Por isso, faca verificacao guiada:

1. Se as skills do Superpowers estiverem disponiveis, use-as normalmente.
2. Se Superpowers nao estiver disponivel e houver ferramenta de instalacao de plugins, solicite a instalacao do plugin Superpowers.
3. Se Atlassian Rovo estiver disponivel, verifique usuario/recursos acessiveis.
4. Se Atlassian Rovo nao estiver disponivel, registre Jira como pendente e, quando a ferramenta de instalacao permitir, solicite a instalacao do plugin Atlassian Rovo.
5. Verifique se `JIRA_BASE_URL`, `JIRA_EMAIL` e `JIRA_API_TOKEN` existem no ambiente sem imprimir valores.
6. Se as credenciais REST estiverem disponiveis, teste leitura basica com `scripts/jira_executor.py`; a integracao REST e preferida para operacoes deterministicas e versoes.
7. Se `tlc-spec-driven` estiver disponivel, registre como opcional recomendado para `.specs/` estruturado, mapeamento brownfield, requisitos rastreaveis, quick tasks e retomada de trabalho.
8. Se `tlc-spec-driven` nao estiver disponivel, nao bloqueie o onboarding; apenas registre que o modo TLC esta pendente e pode ser instalado/chamado depois.

Nao bloqueie o onboarding por Jira ausente.
Nao substitua Superpowers por TLC automaticamente: Superpowers e o padrao Vervit; TLC e complemento sob demanda.

## Fluxo

1. Leia instrucoes locais existentes:
   - `AGENTS.md`
   - `.agents/main-agent.md`
   - `CLAUDE.md`, `GEMINI.md` ou equivalentes, se existirem
2. Rode `scripts/init_project.py` a partir da raiz deste plugin, apontando para o projeto alvo.
3. Revise os arquivos gerados e sugeridos.
4. Se Atlassian Rovo estiver disponivel, tente obter informacoes de usuario e recursos acessiveis.
5. Verifique se TLC Spec-Driven esta disponivel no ambiente e confirme o status em `.agents/vervit-onboarding.json`.
6. Atualize o relatorio final com:
   - arquivos criados;
   - arquivos sugeridos porque ja existiam;
   - stack detectada;
   - comandos de verificacao detectados;
   - status TLC;
   - status de Jira/Atlassian;
   - status do executor Jira REST e provedores operacionais;
   - proximos passos.

## Comando Recomendado

Use o Python disponivel no ambiente:

```powershell
python C:\Vervit\vervit-assistant\scripts\init_project.py --target <caminho-do-projeto>
```

Se estiver dentro do projeto alvo:

```powershell
python C:\Vervit\vervit-assistant\scripts\init_project.py
```

## Politica De Escrita

- Nunca sobrescreva `AGENTS.md` ou `.agents/main-agent.md` existentes sem pedido explicito.
- Quando o arquivo existir, gere uma versao `.vervit-suggested.md`.
- Pode atualizar `.agents/vervit-onboarding.json`, pois e estado gerado pelo onboarding.
- Preserve trabalho local e nao faca commit, push, deploy ou migracao remota sem pedido explicito.

## Fluxos Vervit

Use `vervit-assistant-main` como entrada para todo trabalho Jira. Ela coordena as skills de especificacao/implementacao, Superpowers, executor Jira, roteamento de provedores e guardiao de releases.

### Padrao E Complemento

- Padrao: Superpowers.
- Complemento sob demanda: `tlc-spec-driven`.
- Use TLC quando o usuario pedir um fluxo com fases `Specify/Design/Tasks/Execute`, requisitos rastreaveis, mapeamento brownfield TLC, quick tasks TLC, `pause work` ou `resume work`.
- Quando combinar TLC e Superpowers, use TLC para estrutura em `.specs/` e Superpowers para debugging, TDD, review e verificacao antes de concluir.

### Feature Grande

Use Superpowers em fluxo completo:

1. `superpowers:brainstorming`
2. plano formal com `superpowers:writing-plans` quando houver varias etapas, decisoes tecnicas ou risco relevante
3. TDD quando houver comportamento verificavel
4. implementacao
5. `superpowers:verification-before-completion`

Registre em `.specs/features/<slug>/`.
Se o usuario pedir TLC, deixe `tlc-spec-driven` conduzir `Specify`, `Design` e `Tasks`, mantendo verificacao final proporcional com Superpowers.

### Melhoria Pequena

Use Superpowers em modo simplificado:

1. contexto rapido;
2. plano compacto;
3. TDD apenas quando houver risco real ou mudanca comportamental;
4. implementacao pequena;
5. verificacao proporcional.

Registre em `.specs/quick/<id>-<slug>/` quando houver valor de rastreabilidade.

### Bug Fix

Use `superpowers:systematic-debugging`:

1. reproduzir ou reunir evidencia;
2. localizar causa raiz;
3. corrigir escopo minimo;
4. criar teste de regressao quando viavel;
5. verificar o sintoma original.

Nao pule causa raiz, mesmo quando o fluxo for curto.

### Hotfix E Release Planejada

- Hotfix nasce de `main`, usa `hotfix/KEY-slug`, incrementa patch e volta diretamente para `main`.
- Tarefa planejada nasce de `release`, usa `tipo/KEY-slug` e volta para `release`.
- Uma unica `Proxima Release` pode estar ativa por repositorio/projeto Jira.
- Antes de publicar, congele escopo, calcule SemVer, execute regressao geral e sincronize `main` em `release`.

## Saida Esperada

Ao final, responda em PT-BR com um resumo objetivo:

- projeto analisado;
- arquivos criados/sugeridos;
- status de dependencias;
- status TLC;
- status Jira;
- comandos recomendados para validar o projeto;
- primeiro proximo fluxo recomendado.
