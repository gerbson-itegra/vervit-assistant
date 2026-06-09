from __future__ import annotations

import argparse
import copy
import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Any, Callable


ALLOWED_TASKS = {
    "issue-summary",
    "checkpoint-draft",
    "fact-extraction",
    "release-notes",
    "test-results-summary",
    "regression-summary",
}
FORBIDDEN_KEYS = {
    "attachment",
    "attachments",
    "binary",
    "apiKey",
    "api_key",
    "apiToken",
    "api_token",
    "password",
    "secret",
    "token",
}
FORBIDDEN_KEYS_NORMALIZED = {
    re.sub(r"[^a-z0-9]", "", key.lower()) for key in FORBIDDEN_KEYS
}
SECRET_PATTERNS = [
    re.compile(r"(?i)\bauthorization\s*:\s*(?:bearer|basic)\s+\S+"),
    re.compile(r"(?i)\b(?:api[_ -]?key|api[_ -]?token|password|secret)\s*[:=]\s*\S+"),
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
]


class ProviderRouterError(RuntimeError):
    """Raised for invalid routing requests or provider failures."""


class ProviderPayloadError(ProviderRouterError):
    """Raised when a payload contains content that cannot leave the guard."""


Adapter = Callable[[dict[str, Any], str, dict[str, Any]], dict[str, Any]]


def _contains_secret(value: Any) -> bool:
    if isinstance(value, str):
        return any(pattern.search(value) for pattern in SECRET_PATTERNS)
    if isinstance(value, dict):
        return any(_contains_secret(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_secret(item) for item in value)
    return False


def sanitize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if _contains_secret(payload):
        raise ProviderPayloadError("Payload contem credencial ou segredo detectado.")

    def sanitize(value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: sanitize(item)
                for key, item in value.items()
                if re.sub(r"[^a-z0-9]", "", key.lower())
                not in FORBIDDEN_KEYS_NORMALIZED
            }
        if isinstance(value, list):
            return [sanitize(item) for item in value]
        if isinstance(value, (bytes, bytearray)):
            return "[binary-removed]"
        return value

    return sanitize(copy.deepcopy(payload))


def _json_request(
    url: str,
    payload: dict[str, Any],
    *,
    headers: dict[str, str] | None = None,
    timeout: float = 30,
) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read())
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        raise ProviderRouterError(f"Falha no provedor {url}.") from exc


def _operator_prompt(task: str, payload: dict[str, Any]) -> str:
    return json.dumps(
        {
            "role": "operador-textual",
            "task": task,
            "rules": [
                "Nao analise, planeje, classifique ou tome decisoes.",
                "Use somente os fatos recebidos.",
                "Retorne somente um objeto JSON valido.",
            ],
            "payload": payload,
        },
        ensure_ascii=False,
    )


def _parse_provider_content(content: Any) -> dict[str, Any]:
    if isinstance(content, dict):
        return content
    if not isinstance(content, str):
        raise ProviderRouterError("Provedor retornou conteudo nao estruturado.")
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ProviderRouterError("Provedor nao retornou JSON valido.") from exc
    if not isinstance(parsed, dict):
        raise ProviderRouterError("Resposta do provedor precisa ser um objeto JSON.")
    return parsed


def openai_compatible_adapter(
    provider: dict[str, Any], task: str, payload: dict[str, Any]
) -> dict[str, Any]:
    endpoint = provider["endpoint"].rstrip("/")
    if not endpoint.endswith("/chat/completions"):
        endpoint += "/chat/completions"
    api_key_env = provider.get("apiKeyEnv")
    api_key = os.environ.get(api_key_env, "") if api_key_env else ""
    if api_key_env and not api_key:
        raise ProviderRouterError(f"Variavel de ambiente ausente: {api_key_env}")
    request_payload = {
        "model": provider["model"],
        "messages": [{"role": "user", "content": _operator_prompt(task, payload)}],
    }
    if provider.get("supportsJsonMode", False):
        request_payload["response_format"] = {"type": "json_object"}
    response = _json_request(
        endpoint,
        request_payload,
        headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
        timeout=float(provider.get("timeoutSeconds", 30)),
    )
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderRouterError("Resposta openai-compatible invalida.") from exc
    return _parse_provider_content(content)


def ollama_adapter(
    provider: dict[str, Any], task: str, payload: dict[str, Any]
) -> dict[str, Any]:
    endpoint = provider.get("endpoint", "http://localhost:11434").rstrip("/") + "/api/chat"
    response = _json_request(
        endpoint,
        {
            "model": provider["model"],
            "messages": [{"role": "user", "content": _operator_prompt(task, payload)}],
            "format": "json",
            "stream": False,
        },
        timeout=float(provider.get("timeoutSeconds", 30)),
    )
    try:
        content = response["message"]["content"]
    except (KeyError, TypeError) as exc:
        raise ProviderRouterError("Resposta Ollama invalida.") from exc
    return _parse_provider_content(content)


class ProviderRouter:
    def __init__(
        self,
        providers: list[dict[str, Any]],
        *,
        adapters: dict[str, Adapter] | None = None,
        clock: Callable[[], float] = time.time,
    ):
        self.providers = sorted(providers, key=lambda item: int(item.get("priority", 100)))
        self.adapters = {
            "openai-compatible": openai_compatible_adapter,
            "ollama": ollama_adapter,
            **(adapters or {}),
        }
        self.clock = clock
        self.failures: dict[str, int] = {}
        self.suspended_until: dict[str, float] = {}

    def route(
        self,
        task: str,
        payload: dict[str, Any],
        *,
        contains_jira_content: bool = False,
    ) -> dict[str, Any]:
        if task not in ALLOWED_TASKS:
            raise ProviderRouterError(
                f"Tarefa {task!r} exige o agente principal OpenAI + Superpowers."
            )
        sanitized = sanitize_payload(payload)
        errors = []
        now = self.clock()

        for provider in self.providers:
            provider_id = provider.get("id", "unnamed")
            if not provider.get("enabled", True):
                continue
            if now < self.suspended_until.get(provider_id, 0):
                continue
            allowed = provider.get("allowedTasks")
            if allowed is not None and task not in allowed:
                continue
            if contains_jira_content and not provider.get("jiraContentConsent", False):
                continue
            adapter = self.adapters.get(provider.get("adapter"))
            if not adapter:
                errors.append({"provider": provider_id, "error": "adapter-not-found"})
                continue
            try:
                result = adapter(provider, task, sanitized)
                if not isinstance(result, dict) or not result:
                    raise ProviderRouterError("Resposta vazia ou invalida.")
                self.failures[provider_id] = 0
                return {
                    "status": "completed",
                    "provider": provider_id,
                    "result": result,
                }
            except Exception as exc:
                failures = self.failures.get(provider_id, 0) + 1
                self.failures[provider_id] = failures
                if failures >= 3:
                    self.suspended_until[provider_id] = now + 15 * 60
                errors.append({"provider": provider_id, "error": type(exc).__name__})

        return {
            "status": "fallback-required",
            "provider": "openai-primary",
            "task": task,
            "errors": errors,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Roteia tarefas operacionais Vervit.")
    parser.add_argument("config")
    parser.add_argument("task", choices=sorted(ALLOWED_TASKS))
    parser.add_argument("payload")
    parser.add_argument("--jira-content", action="store_true")
    args = parser.parse_args()
    with open(args.config, encoding="utf-8") as handle:
        config = json.load(handle)
    with open(args.payload, encoding="utf-8") as handle:
        payload = json.load(handle)
    result = ProviderRouter(config.get("providers", [])).route(
        args.task, payload, contains_jira_content=args.jira_content
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
