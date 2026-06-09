# Reset De Conhecimento No Primeiro Onboarding

## Objetivo

Ao inicializar um projeto pela primeira vez, o Vervit Assistant deve preservar o
conhecimento existente em um backup externo e iniciar o onboarding sem memorias
ou instrucoes antigas. O codigo-fonte, testes, configuracoes tecnicas e
metadados Git permanecem no projeto para serem analisados novamente.

## Gatilho

O reset acontece automaticamente somente quando
`.agents/vervit-onboarding.json` ainda nao existe.

Nas execucoes seguintes, o onboarding atualiza os artefatos Vervit normalmente,
sem criar outro backup e sem remover novamente os arquivos gerados pelo proprio
plugin.

## Escopo Do Backup

O primeiro onboarding move para o backup, quando existirem:

- `AGENTS.md`;
- `CLAUDE.md`;
- `GEMINI.md`;
- `CODEX.md`;
- `.clinerules`;
- `.windsurfrules`;
- o diretorio `.claude/`;
- o diretorio `.cursor/`;
- o arquivo `.github/copilot-instructions.md`, preservando o restante de
  `.github/`;
- todos os arquivos raiz que correspondam a `README*`;
- o diretorio `docs/`;
- o diretorio `.agents/`;
- o diretorio `.specs/`.

O reset nao move:

- codigo-fonte;
- testes;
- configuracoes de build, runtime ou infraestrutura;
- `.git/`, `.github/` ou `.gitignore`;
- arquivos de dependencias ou manifests da aplicacao.

## Local Do Backup

O backup fica fora do projeto:

```text
<diretorio-pai>/.vervit-backups/<nome-projeto>/<data-hora>/
```

O nome de cada entrada preserva seu caminho relativo original. O diretorio
externo nao participa do novo mapeamento do projeto nem entra no Git do projeto.

## Manifesto

Cada backup contem `manifest.json` com:

- versao do formato;
- data e hora UTC;
- caminho absoluto do projeto de origem;
- caminho absoluto do backup;
- lista dos arquivos movidos;
- caminho relativo original;
- tamanho em bytes;
- hash SHA-256;
- estado final da operacao.

O manifesto nao registra conteudo dos arquivos nem valores de segredos.

## Fluxo Transacional

1. Validar que o projeto existe e que o backup esta fora da raiz do projeto.
2. Descobrir todas as entradas elegiveis sem alterar o projeto.
3. Criar o diretorio de backup e o manifesto inicial.
4. Mover as entradas elegiveis preservando seus caminhos relativos.
5. Gerar do zero `AGENTS.md`, `.agents/`, `.specs/` e o novo mapeamento.
6. Registrar em `.agents/vervit-onboarding.json` o caminho do backup, o
   manifesto e a quantidade de arquivos preservados.
7. Marcar o manifesto como concluido.

Se qualquer etapa falhar depois do primeiro movimento, o processo restaura as
entradas movidas para seus caminhos originais. Arquivos parcialmente gerados
pelo onboarding sao removidos somente quando foram criados pela execucao que
falhou.

## Colisoes E Seguranca

- Cada backup usa timestamp UTC com precisao suficiente para nao sobrescrever
  backups anteriores.
- O processo bloqueia se o destino do backup estiver dentro do projeto.
- Links simbolicos sao preservados como links e nao sao percorridos.
- Arquivos fora do escopo nunca sao movidos.
- Uma restauracao bloqueia em vez de sobrescrever um caminho original que tenha
  sido recriado durante a falha.
- O resultado informa claramente backup criado, arquivos movidos, restauracao e
  erros.

## Interface

O comportamento padrao de `initialize_project()` passa a executar o reset na
primeira inicializacao.

O CLI oferece:

```text
--skip-knowledge-reset
```

Essa opcao permite um primeiro onboarding sem mover conhecimento, para
recuperacao ou casos excepcionais. O uso fica registrado no estado de
onboarding.

O retorno de `initialize_project()` continua contendo os resultados dos
arquivos gerados e passa a incluir metadados estruturados do reset.

## Testes

A suite deve cobrir:

- primeiro onboarding move todo o escopo e recria os artefatos Vervit;
- `README*` e `docs/` entram no backup;
- codigo, testes e configuracoes tecnicas permanecem no projeto;
- caminhos e hashes aparecem corretamente no manifesto;
- segunda execucao nao repete o reset;
- `--skip-knowledge-reset` preserva o conhecimento;
- falha durante o onboarding restaura os arquivos movidos;
- colisao durante restauracao bloqueia sobrescrita;
- destino de backup dentro do projeto e rejeitado;
- links simbolicos nao sao percorridos.

## Criterios De Aceite

- O primeiro onboarding inicia sem conhecimento antigo visivel dentro do
  projeto.
- Todo conhecimento removido pode ser localizado e validado pelo manifesto.
- Nenhum arquivo fora do escopo e movido.
- Falhas nao deixam o projeto sem o conhecimento anterior.
- Execucoes posteriores preservam os artefatos criados pelo Vervit.
