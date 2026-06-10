# Economia De Tokens Do Vervit Assistant

## Objetivo

Reduzir o contexto obrigatório inicial em pelo menos 60% e o texto das skills
frequentes em pelo menos 40%, sem remover gates de segurança.

## Estrategia

`vervit-assistant-main` será um roteador curto orientado pelo gate atual. O agente
deve reutilizar contexto já disponível e carregar somente o menor artefato ou
referência necessário para a próxima ação.

## Carregamento Sob Demanda

- Leia instruções locais somente quando ainda não estiverem no contexto.
- Leia `state.json` primeiro para descobrir o gate atual.
- Abra `PRD.md` somente para especificar, aprovar ou implementar.
- Abra `TRACE.md` somente para registrar ou auditar marcos.
- Carregue `task-workflow.md`, `jira-operations.md`, `provider-routing.md` e
  `releases.md` apenas quando a ação correspondente for necessária.
- Não delegue para outra skill quando o trabalho atual já puder ser concluído
  diretamente com segurança.

## Escrita E Saída

- `TRACE.md` registra apenas marcos confirmados: gates, operações Jira,
  provedores/fallbacks, testes e integrações.
- Resumos finais mostram somente mudanças, evidências, bloqueios e próximo gate.
- Provedores externos continuam limitados a transformações textuais permitidas.

## Gates Preservados

- PRD aprovado e checklist manual publicado antes da implementação.
- Testes, checklist manual e review completos antes da integração.
- Confirmação explícita para Jira sensível, merge, push e tag.
- Credenciais, anexos e binários nunca enviados a provedores.
- Trabalho local nunca sobrescrito ou revertido sem autorização.

## Verificação

Testes automatizados devem impor limites de palavras nas skills frequentes,
detectar instruções de leitura obrigatória redundante e confirmar a presença dos
gates preservados. A medição final compara o orçamento textual anterior e novo.
