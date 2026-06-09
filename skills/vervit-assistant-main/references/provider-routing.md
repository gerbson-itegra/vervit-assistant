# Roteamento Multi-Provider

O roteador operacional vive em `scripts/provider_router.py` e le a lista `providers` de `.agents/vervit-assistant.json`.

Cada item representa uma instancia independente e pode usar seu proprio `apiKeyEnv`. Cadastre quantas instancias forem necessarias; menor `priority` e tentada primeiro.

```json
{
  "providers": [
    {
      "id": "external-primary",
      "adapter": "openai-compatible",
      "priority": 10,
      "endpoint": "https://provider.example/v1",
      "model": "model-name",
      "apiKeyEnv": "PROVIDER_PRIMARY_API_KEY",
      "allowedTasks": ["issue-summary", "checkpoint-draft"],
      "jiraContentConsent": true,
      "enabled": true
    },
    {
      "id": "ollama-fallback",
      "adapter": "ollama",
      "priority": 20,
      "endpoint": "http://localhost:11434",
      "model": "local-model",
      "allowedTasks": ["issue-summary", "checkpoint-draft"],
      "jiraContentConsent": true,
      "enabled": true
    }
  ]
}
```

## Permitido

- `issue-summary`
- `checkpoint-draft`
- `fact-extraction`
- `release-notes`
- `test-results-summary`
- `regression-summary`

## Proibido

Classificacao, PRD, planejamento, cenarios, arquitetura, debugging, codigo, review, SemVer, decisoes Jira, merges, liberacao e declaracao de conclusao.

## Politica

- Percorra provedores habilitados por prioridade.
- Respeite `allowedTasks` e `jiraContentConsent`.
- Uma falha segue para o proximo provedor.
- Tres falhas suspendem o provedor por 15 minutos.
- Quando todos falharem, use o agente OpenAI principal e registre o fallback.
- Adapters iniciais: `openai-compatible` e `ollama`; outros exigem adapter validado.
