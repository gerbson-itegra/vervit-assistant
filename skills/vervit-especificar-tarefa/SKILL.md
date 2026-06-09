---
name: vervit-especificar-tarefa
description: Use esta skill, normalmente delegada por vervit-assistant-main, para especificar, detalhar, refinar ou criar o PRD de uma tarefa Jira Vervit. Leia o estado e o Markdown da tarefa, use o contexto do projeto, esclareca lacunas e aplique Superpowers conforme o tipo confirmado. Nao implemente codigo.
metadata:
  short-description: Especificar tarefa Jira Vervit
---

# Vervit Especificar Tarefa

Use esta skill para transformar o Markdown de uma tarefa Jira em uma especificacao de desenvolvimento clara, interativa e versionada.

## Fluxo

1. Leia o prompt preparado por `vervit-assistant-main`.
2. Abra `.specs/jira/<KEY>/PRD.md`, `TRACE.md` e `state.json`.
3. Use o contexto do projeto fornecido no prompt para evitar uma especificacao generica.
4. Use Superpowers para conduzir a especificacao: brainstorming para escopo grande ou ambiguidade relevante, e fluxo simplificado para melhoria pequena.
5. Faca perguntas quando houver lacunas importantes antes de fechar decisoes.
6. Defina cenarios de validacao manual claros, executaveis e rastreaveis.
7. Atualize o PRD e aguarde aprovacao explicita antes de retornar para implementacao.

## Regras

- Escreva em portugues do Brasil.
- Nao implemente codigo nesta etapa.
- Separe fato encontrado, inferencia e pergunta aberta.
- Cite caminhos concretos do projeto quando houver evidencia.
- Preserve a rastreabilidade com a chave Jira.
- Nao publique nem altere Jira diretamente; retorne o PRD e os cenarios para a skill principal.
- Se o Markdown da tarefa estiver incompleto, complete apenas com informacoes confirmadas ou pergunte ao usuario.

## Saida Esperada

Atualize o Markdown da tarefa com secoes adequadas para descricao, escopo, regras de negocio, criterios de aceitacao, impactos tecnicos, cenarios de teste, riscos e perguntas abertas.
