# Descoberta Das Skills Vervit Pelo Menu Slash

## Objetivo

Ao instalar e habilitar o plugin `vervit-assistant`, suas cinco skills devem
aparecer individualmente na lista de comandos do Codex app. Digitar `/vervit`
deve filtrar essa lista e exibir todas as skills Vervit.

## Experiencia Esperada

O menu deve apresentar entradas individuais e pesquisaveis:

- `Vervit: Assistente Principal`
- `Vervit: Inicializar Projeto`
- `Vervit: Mapear Codebase`
- `Vervit: Especificar Tarefa`
- `Vervit: Implementar Tarefa`

Selecionar uma entrada deve invocar a skill correspondente. `/vervit` nao sera
um novo comando executavel nem uma skill-fachada; sera o texto usado para
filtrar as skills habilitadas na lista slash.

## Arquitetura

Cada diretorio em `skills/` recebera um arquivo `agents/openai.yaml` com
metadados de apresentacao para o Codex app. O `interface.display_name` de todas
as skills comecara por `Vervit:`, garantindo que a busca por `vervit` encontre
as cinco entradas. O `interface.short_description` explicara a acao especifica
da skill.

Os nomes tecnicos existentes nos front matters de `SKILL.md` permanecerao
inalterados para preservar invocacoes explicitas e compatibilidade. A descoberta
e instalacao continuarao sendo feitas pelo campo `skills: "./skills/"` do
manifesto do plugin.

## Instalacao E Atualizacao

O instalador continuara adicionando o marketplace e instalando somente
`vervit-assistant@vervit`. Nenhuma skill sera copiada para
`~/.agents/skills`, `~/.codex/skills` ou outro diretorio pessoal.

O script `build_marketplace_plugin.py` ja sincroniza toda a arvore `skills/`;
portanto, os novos arquivos `agents/openai.yaml` serao incluidos no pacote do
marketplace sem uma nova etapa de instalacao.

Depois de instalar ou atualizar o plugin, o usuario deve iniciar uma nova
thread para carregar as skills atualizadas.

## Validacao E Testes

Um teste automatizado verificara que:

- as cinco skills esperadas possuem `agents/openai.yaml`;
- cada arquivo possui `interface.display_name` iniciado por `Vervit:`;
- os cinco nomes visiveis sao distintos;
- o pacote gerado pelo marketplace contem os mesmos metadados.

A validacao final executara a suite existente, reconstruira o pacote do
marketplace e executara o validador oficial de plugins.

## Limites

- Nao criar custom prompts, pois estao depreciados.
- Nao criar um comando slash customizado `/vervit`.
- Nao duplicar skills em diretorios pessoais durante a instalacao.
- Nao alterar o comportamento interno das skills.
