# Onboarding Readiness And Skill Sources

## Objetivo

Alinhar `scripts/init_project.py` ao contrato de onboarding Vervit, registrando o
que o ambiente realmente oferece e permitindo instalar ou atualizar skills a
partir de sua fonte Git original.

## Deteccao

- Superpowers fica `ready` somente quando todas as skills essenciais do fluxo
  Vervit forem encontradas: `brainstorming`, `writing-plans`,
  `systematic-debugging`, `test-driven-development` e
  `verification-before-completion`.
- A busca cobre skills pessoais, plugins instalados/cache e o proprio plugin
  Vervit. O resultado registra caminhos encontrados e skills ausentes.
- TLC mantem seu papel opcional e sua deteccao atual.
- Atlassian registra separadamente:
  - conector exposto, inferido somente por marcadores de ambiente;
  - executor REST, inferido somente pela presenca das tres variaveis Jira;
  - status agregado, sem afirmar conexao ou autenticacao que o script nao pode
    verificar.

## Instalacao E Atualizacao

O comportamento padrao continua sem efeitos externos. A opcao
`--install-skills` habilita sincronizacao Git.

- Superpowers usa por padrao `https://github.com/obra/superpowers.git`.
- Fontes adicionais podem ser fornecidas por `--skill-source NAME=URL`.
- Cada fonte e clonada em `<CODEX_HOME>/skills/sources/<name>` quando ausente.
- Uma fonte existente so e atualizada quando e um checkout Git limpo e seu
  remote `origin` corresponde a URL configurada. A atualizacao usa
  `git pull --ff-only`.
- Checkouts sujos, origens divergentes e falhas Git sao registrados sem apagar
  ou sobrescrever trabalho local.
- O estado registra URL, caminho, acao, status e commit, permitindo atualizacoes
  futuras a partir da mesma origem.

## Estado E Documentacao

`.agents/vervit-onboarding.json` passa a incluir `dependencies` com Superpowers,
TLC, Atlassian/Jira e sincronizacao de fontes. `.specs/codebase/INTEGRATIONS.md`
resume os mesmos fatos. README e a skill de onboarding documentam as novas
opcoes e deixam claro que conectores nao podem ser autenticados pelo script.

## Testes

A suite cobre prontidao completa e incompleta do Superpowers, preserva a
deteccao TLC, diferencia Atlassian exposto de Jira REST configurado, verifica o
estado gerado e exercita clone, atualizacao fast-forward e protecao de checkout
sujo usando repositorios Git locais.
