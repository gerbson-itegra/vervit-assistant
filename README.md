# Vervit Assistant

Plugin Codex para inicializar projetos e conduzir desenvolvimento Jira rastreavel com o padrao Vervit.

## O Que Ele Faz

- Cria onboarding seguro para projetos existentes.
- Mapeia stack, estrutura, testes, integracoes e pontos de atencao.
- Cria `.specs/project/` e `.specs/codebase/` como memoria tecnica do projeto.
- Cria ou sugere `AGENTS.md` e `.agents/main-agent.md`.
- Guia tres fluxos de trabalho:
  - feature grande;
  - melhoria pequena;
  - bug fix.
- Verifica Atlassian/Jira quando o plugin Atlassian Rovo estiver disponivel.
- Adiciona `vervit-assistant-main` como fachada para selecao Jira, PRD, TDD, checklist manual, hotfix e release planejada.
- Executa operacoes Jira deterministicas pela REST API v3 com planos confirmados por hash.
- Aplica SemVer, tags `vX.Y.Z`, Fix Versions e regressao geral antes da liberacao.
- Roteia somente tarefas textuais triviais por uma cadeia configuravel de provedores externos.
- Mantem Jira como pendente quando nao houver conexao, sem bloquear o onboarding.
- Registra TLC Spec-Driven como complemento opcional para quem quer `.specs/` mais estruturado.

## Skills

- `vervit-assistant-main`: ciclo completo de desenvolvimento Jira, integracao e releases.
- `vervit-init-project`: onboarding completo do projeto.
- `vervit-map-codebase`: mapeamento ou revisao de `.specs/codebase/`.
- `vervit-especificar-tarefa`: especificacao de tarefas Jira Vervit.
- `vervit-implementar-tarefa`: implementacao de tarefas Jira Vervit.

## Uso

Depois de instalar o plugin no Codex, inicie uma nova thread no projeto alvo e peca:

```text
/init Vervit neste projeto
```

Ou:

```text
Inicialize este projeto com o padrao Vervit
```

Para trabalhar em uma atividade:

```text
Use o Vervit Assistant para listar minhas atividades Jira e iniciar uma tarefa
```

## Configuracao

O onboarding cria `.agents/vervit-assistant.json` com nomes de variaveis de ambiente, branches e cadeia de provedores. Segredos nunca entram no arquivo.

Variaveis Jira esperadas:

```text
JIRA_BASE_URL
JIRA_EMAIL
JIRA_API_TOKEN
```

Adapters operacionais iniciais: `openai-compatible` e `ollama`. Provedores externos nunca recebem tarefas de analise, planejamento, debugging, codigo, review, SemVer ou integracao.

Cadastre N instancias em `providers`, cada uma com `priority`, `adapter`, `endpoint`, `model`, `apiKeyEnv`, tarefas permitidas e consentimento Jira. O roteador tenta em ordem e usa o agente principal como ultimo fallback.

## Script De Onboarding

O skill de inicializacao usa:

```powershell
python C:\Vervit\vervit-assistant\scripts\init_project.py --target <caminho-do-projeto>
```

O script e seguro por padrao:

- escreve arquivos novos;
- quando `AGENTS.md` ou `.agents/main-agent.md` ja existem, gera `.vervit-suggested.md`;
- atualiza `.agents/vervit-onboarding.json` como estado gerado.

## Dependencias Guiadas

Plugins Codex nao possuem instalacao automatica obrigatoria entre plugins. Por isso, o Vervit Assistant verifica e orienta:

- Superpowers: recomendado para todos os fluxos.
- TLC Spec-Driven: opcional, sob demanda, para mapeamento brownfield, requisitos rastreaveis, tarefas atomicas, quick tasks e retomada de trabalho.
- Atlassian Rovo: recomendado para Jira, mas nao bloqueante.

## Fluxos Superpowers E TLC

- Feature grande: `brainstorming`, plano formal quando necessario, TDD quando houver comportamento verificavel e verificacao antes de concluir.
- Melhoria pequena: Superpowers em modo leve, plano compacto e verificacao proporcional.
- Bug fix: `systematic-debugging`, causa raiz, regressao quando viavel e verificacao do sintoma original.

Superpowers e o padrao Vervit. TLC Spec-Driven pode ser chamado sob demanda quando o usuario pedir `tlc`, `map codebase TLC`, `specify feature`, `quick task`, `pause work` ou `resume work` nesse estilo. Nesse caso, use TLC para estrutura e rastreabilidade em `.specs/`, mantendo Superpowers para debugging, TDD, review e verificacao final.

## Verificacao Do Plugin

```powershell
python -m unittest discover -s tests -v
python C:\Users\gerbs\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py C:\Vervit\vervit-assistant
```
