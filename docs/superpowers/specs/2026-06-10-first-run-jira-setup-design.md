# First Run E Configuracao Jira

## Objetivo

Instalar o Vervit Assistant com uma primeira execução guiada, permitindo
configurar Jira sem expor segredos no chat ou em arquivos versionados.

## Credenciais

- O onboarding cria `.env.vervit.example` com `JIRA_BASE_URL`, `JIRA_EMAIL` e
  `JIRA_API_TOKEN` vazios.
- `.env.vervit.local` é ignorado pelo Git e preenchido pelo usuário localmente.
- Scripts carregam `.env.vervit.local` sem sobrescrever variáveis de ambiente.
- Valores nunca aparecem em saídas, estados ou documentação gerada.

## Primeira Execucao

`.agents/vervit-onboarding.json` registra `firstRun`, status Jira e ações
disponíveis. Quando Jira estiver pendente, o assistente explica como preencher o
arquivo local e não pede a API key no chat.

O menu inicial oferece: configurar Jira, listar issues, mapear projeto, iniciar
feature/bug/hotfix e preparar release.

## Instalacao

Após testes e validação, atualizar o cachebuster do manifesto e reinstalar
`vervit-assistant@personal`. Uma nova thread deve ser usada para carregar a
versão atualizada.
