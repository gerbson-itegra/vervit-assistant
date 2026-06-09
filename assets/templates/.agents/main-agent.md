# Perfil Do Agente Principal

Este arquivo descreve como o agente deve trabalhar neste projeto usando o padrao Vervit.

## Objetivo

- Evoluir o projeto com mudancas pequenas, verificaveis e alinhadas ao padrao existente.
- Preservar trabalho local do usuario.
- Manter memoria tecnica em `.specs/` quando o trabalho tiver valor recorrente.
- Explicar decisoes tecnicas em portugues claro.

## Comportamento

- Leia o contexto antes de editar.
- Prefira padroes existentes do repositorio.
- Quando a ambiguidade for pequena, escolha a opcao conservadora e registre a suposicao.
- Quando a ambiguidade envolver produto, dados, permissao, seguranca, custo ou UX relevante, pergunte antes.
- Ao final, informe arquivos alterados e verificacao executada.

## Superpowers Em Modo Adaptativo

- Feature grande: brainstorming, specify/design/tasks, TDD quando couber, implementacao e verificacao.
- Melhoria pequena: plano compacto, TDD apenas com risco real, verificacao proporcional.
- Bug fix: systematic-debugging antes da correcao.
- Documentacao/config simples: checklist curto.

## Vervit Assistant Main

- Use `vervit-assistant-main` como fachada para atividades Jira.
- Exija PRD aprovado e checklist manual publicado antes do codigo.
- Exija checklist completo, testes, review e verificacao antes de integrar.
- Mantenha `.specs/jira/<KEY>/PRD.md`, `TRACE.md` e `state.json`.
- Mantenha a release ativa em `.specs/releases/NEXT/`.

## Politica De Entrega

- Hotfix nasce de `main`, volta para `main`, recebe tag patch e e propagado para `release`.
- Trabalho planejado nasce de `release` e volta para `release`.
- Release planejada exige congelamento de escopo, SemVer, regressao geral, release notes, merge em `main`, tag e sincronizacao de volta.
- Acoes remotas e Git sensiveis exigem confirmacao explicita.

## Economia De Tokens

- Provedores externos podem fazer apenas transformacoes textuais triviais permitidas.
- OpenAI + Superpowers sempre executa analise, planejamento, debugging, implementacao, review, versionamento e liberacao.
- Nunca envie credenciais, anexos ou binarios a provedores externos.

## TLC Spec-Driven Opcional

- Superpowers continua sendo o padrao Vervit.
- Use TLC sob demanda quando o usuario pedir explicitamente `tlc`, `TLC Spec-Driven`, `map codebase`, `specify feature`, `quick task`, `pause work` ou `resume work` nesse estilo.
- TLC e preferido para estruturar `.specs/project`, `.specs/codebase`, `.specs/features` e `.specs/quick` com requisitos rastreaveis e tarefas atomicas.
- Superpowers continua preferido para brainstorming formal, systematic-debugging, TDD, recebimento de review e verificacao antes de concluir.
- Quando combinar os dois, registre a decisao em linguagem simples no resumo final.

## Limites

- Nao fazer commit, push, deploy ou migracao remota sem pedido explicito.
- Nao reverter mudancas locais que nao foram feitas pelo agente.
- Nao copiar dependencias externas para o repositorio sem necessidade clara.
