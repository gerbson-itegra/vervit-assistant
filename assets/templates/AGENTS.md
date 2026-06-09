# Guia Local do Agente

Este projeto usa o padrao Vervit Assistant para Codex.

## Prioridade De Instrucoes

1. Pedido direto do usuario
2. Este `AGENTS.md`
3. `.agents/main-agent.md`
4. Skills Vervit
5. Skills Superpowers
6. TLC Spec-Driven quando solicitado
7. Padrao geral do agente

Leia `.agents/main-agent.md` no inicio de cada trabalho.

## Idioma

Responda em portugues do Brasil por padrao, exceto quando o usuario pedir outro idioma.

## Fluxos De Trabalho

Superpowers e o padrao principal do projeto. Use TLC Spec-Driven como complemento sob demanda quando o usuario pedir mais rastreabilidade em `.specs/`, fases `Specify/Design/Tasks/Execute`, quick task TLC, map codebase TLC ou retomada estruturada de trabalho.

Para atividades Jira, use `vervit-assistant-main` como entrada obrigatoria. Ela coordena classificacao, branch, PRD, checklist manual, desenvolvimento, Jira, versoes e integracao.

### Feature Grande

Use Superpowers em fluxo completo:

- brainstorming;
- plano formal quando necessario;
- TDD quando houver comportamento verificavel;
- implementacao;
- verificacao antes de concluir.

Registre specs em `.specs/features/`.

Quando o usuario pedir TLC, use `tlc-spec-driven` para organizar requisitos, decisoes, design e tarefas; mantenha as verificacoes finais do Superpowers quando aplicavel.

### Melhoria Pequena

Use Superpowers em modo simplificado:

- contexto rapido;
- plano compacto;
- TDD somente quando houver risco real ou mudanca comportamental;
- verificacao proporcional.

### Bug Fix

Use `systematic-debugging`:

- reproduzir ou reunir evidencia;
- encontrar causa raiz;
- corrigir escopo minimo;
- testar regressao quando viavel;
- verificar o sintoma original.

## Jira E Atlassian

Use o executor Jira REST do Vervit para operacoes deterministicas. Credenciais devem existir apenas em `JIRA_BASE_URL`, `JIRA_EMAIL` e `JIRA_API_TOKEN`. Use Atlassian Rovo como apoio quando estiver instalado e autenticado.

- Nunca implemente antes de aprovar o PRD e publicar o checklist manual.
- Nunca integre enquanto houver checklist pendente ou teste falhando.
- Operacoes Jira sensiveis, merge, push e tag exigem confirmacao explicita.

## Entrega E Versoes

- Hotfix: branch `hotfix/KEY-slug` baseada em `main`, incremento patch e sincronizacao posterior de `main` em `release`.
- Release planejada: branches `tipo/KEY-slug` baseadas em `release`.
- Jira usa Fix Version `X.Y.Z`; Git usa tag anotada `vX.Y.Z`.
- Breaking gera major; feature gera minor; somente bug/improvement gera patch.
- Antes de publicar uma release planejada, execute regressao geral focada nas tarefas e impactos acumulados.

## Provedores Operacionais

Provedores externos configurados podem resumir e formatar fatos, checkpoints, release notes e resultados. Analise, planejamento, debugging, codigo, review, SemVer, Jira sensivel e integracao permanecem com OpenAI + Superpowers.

## TLC Spec-Driven

- Padrao: Superpowers.
- Sob demanda: TLC para `map codebase`, `specify feature`, `design`, `tasks`, `quick task`, `pause work` e `resume work`.
- Nao duplique documentos sem necessidade; se `.specs/` ja existir, preserve e atualize somente o escopo pedido.
- Quando TLC e Superpowers se sobrepuserem, use TLC para estrutura e rastreabilidade, Superpowers para debugging, TDD, implementacao disciplinada e verificacao.

## Seguranca

- Nao sobrescreva trabalho local sem autorizacao.
- Nao faca commit, push, deploy, migracao remota ou mudanca destrutiva sem pedido explicito.
- Prefira mudancas pequenas, verificaveis e alinhadas aos padroes existentes.
