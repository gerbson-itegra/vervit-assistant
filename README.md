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
- Detecta prontidao real do Superpowers pelas skills essenciais disponiveis.
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

## Instalacao Para O Time

O repositorio e privado e tambem funciona como marketplace Codex de equipe.
Somente devs com acesso Git autenticado ao repositorio conseguem instala-lo.

Instalacao recomendada:

```bash
npx --yes github:gerbson-itegra/vervit-assistant
```

O comando usa as credenciais Git do dev para baixar temporariamente o
repositorio privado, adiciona ou atualiza o marketplace `vervit` e instala
`vervit-assistant@vervit`. Nada e publicado no npm.

Requisitos:

- acesso ao repositorio privado `gerbson-itegra/vervit-assistant`;
- Git autenticado no GitHub;
- Node.js 18 ou superior;
- Codex CLI disponivel no `PATH`.

Para validar o instalador a partir de um clone local:

```bash
node ./bin/install.mjs --source .
```

O fallback PowerShell local continua disponivel:

```powershell
.\scripts\install_plugin.ps1 -Source $PWD
```

O marketplace de equipe fica em `.agents/plugins/marketplace.json`. Portanto,
novas instalacoes e atualizacoes ficam bloqueadas quando o dev perde acesso ao
repositorio privado. Plugins ja instalados devem ser removidos do ambiente do
dev durante o offboarding. Depois da instalacao, abra uma nova thread no Codex.

Antes de publicar mudancas no plugin, atualize o pacote consumido pelo
marketplace:

```powershell
python .\scripts\build_marketplace_plugin.py
```

O comando sincroniza `.codex-plugin`, `assets`, `scripts` e `skills` para
`plugins/vervit-assistant`, que e o layout exigido pelo marketplace Codex.

## Configuracao

O onboarding cria `.agents/vervit-assistant.json` com nomes de variaveis de ambiente, branches e cadeia de provedores. Segredos nunca entram no arquivo.

Na primeira execução, copie `.env.vervit.example` para `.env.vervit.local` e
preencha localmente. O arquivo local é ignorado pelo Git e seus valores nunca
devem ser enviados no chat.

```env
JIRA_BASE_URL=https://sua-organizacao.atlassian.net
JIRA_EMAIL=seu-email
JIRA_API_TOKEN=sua-api-key
```

Variáveis definidas no ambiente têm precedência sobre `.env.vervit.local`.

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
- apenas detecta dependencias; nao acessa rede sem `--install-skills`.

Para instalar ou atualizar skills preservando a fonte Git original:

```powershell
python C:\Vervit\vervit-assistant\scripts\init_project.py --target <caminho-do-projeto> --install-skills
```

Superpowers usa `https://github.com/obra/superpowers.git` por padrao. Fontes
adicionais ou substitutas podem ser informadas repetindo:

```powershell
--skill-source nome=https://github.com/organizacao/repositorio.git
```

Os checkouts ficam em `CODEX_HOME/skills/sources/<nome>` e as skills publicadas
em `CODEX_HOME/skills/<skill>`. Atualizacoes usam `git pull --ff-only`.
Checkouts sujos, origins divergentes e skills existentes nao gerenciadas nao
sao sobrescritos. Reinicie o Codex depois de instalar ou atualizar skills.

## Dependencias Guiadas

Plugins Codex nao possuem instalacao automatica obrigatoria entre plugins. Por isso, o Vervit Assistant verifica e orienta:

- Superpowers: recomendado para todos os fluxos.
- TLC Spec-Driven: opcional, sob demanda, para mapeamento brownfield, requisitos rastreaveis, tarefas atomicas, quick tasks e retomada de trabalho.
- Atlassian Rovo: recomendado para Jira, mas nao bloqueante.

O estado `.agents/vervit-onboarding.json` registra separadamente a prontidao
do Superpowers, TLC, marcadores de ambiente Atlassian, credenciais Jira REST e
resultado de cada fonte Git. O script nunca registra valores de variaveis de
ambiente e nao afirma que um conector esta autenticado sem verificacao externa.

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
