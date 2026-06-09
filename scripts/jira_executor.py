from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import os
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any, Callable


CHECKLIST_START = "[[VERVIT-CHECKLIST-START]]"
CHECKLIST_END = "[[VERVIT-CHECKLIST-END]]"
SENSITIVE_OPERATIONS = {
    "create_issue",
    "transition_issue",
    "link_issues",
    "create_version",
    "apply_fix_version",
    "release_version",
    "edit_issue",
}
AUTOMATIC_OPERATIONS = {
    "get_project",
    "get_issue",
    "list_my_open_issues",
    "list_project_versions",
    "list_transitions",
    "comment_checkpoint",
    "update_checklist",
}
ALLOWED_OPERATIONS = SENSITIVE_OPERATIONS | AUTOMATIC_OPERATIONS


class JiraExecutorError(RuntimeError):
    """Raised when a Jira operation is invalid, unsafe, or fails."""


def _node_text(node: Any) -> str:
    if isinstance(node, dict):
        own = node.get("text", "")
        return own + "".join(_node_text(child) for child in node.get("content", []))
    if isinstance(node, list):
        return "".join(_node_text(child) for child in node)
    return ""


def _paragraph(text: str) -> dict[str, Any]:
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


def _task_list(scenarios: list[str], states: dict[str, str]) -> dict[str, Any]:
    items = []
    for scenario in scenarios:
        local_id = hashlib.sha256(scenario.encode("utf-8")).hexdigest()[:16]
        items.append(
            {
                "type": "taskItem",
                "attrs": {
                    "localId": local_id,
                    "state": states.get(scenario, "TODO"),
                },
                "content": [_paragraph(scenario)],
            }
        )
    return {
        "type": "taskList",
        "attrs": {"localId": "vervit-validation-checklist"},
        "content": items,
    }


def _managed_adf_bounds(content: list[dict[str, Any]]) -> tuple[int, int] | None:
    start = end = None
    for index, node in enumerate(content):
        text = _node_text(node)
        if CHECKLIST_START in text:
            start = index
        if CHECKLIST_END in text and start is not None:
            end = index
            break
    return (start, end) if start is not None and end is not None else None


def _adf_states(nodes: list[dict[str, Any]]) -> dict[str, str]:
    states: dict[str, str] = {}
    for node in nodes:
        if node.get("type") != "taskList":
            continue
        for item in node.get("content", []):
            if item.get("type") == "taskItem":
                states[_node_text(item)] = item.get("attrs", {}).get("state", "TODO")
    return states


def update_managed_checklist(description: Any, scenarios: list[str]) -> Any:
    if not scenarios or any(not item.strip() for item in scenarios):
        raise JiraExecutorError("O checklist precisa conter cenarios nao vazios.")
    scenarios = [item.strip() for item in scenarios]

    if isinstance(description, str) or description is None:
        text = description or ""
        states: dict[str, bool] = {}
        if CHECKLIST_START in text and CHECKLIST_END in text:
            before, remainder = text.split(CHECKLIST_START, 1)
            managed, after = remainder.split(CHECKLIST_END, 1)
            for line in managed.splitlines():
                if line.startswith("- [x] ") or line.startswith("- [X] "):
                    states[line[6:].strip()] = True
            text = before.rstrip() + "\n\n" + after.lstrip()
        checklist = "\n".join(
            f"- [{'x' if states.get(item) else ' '}] {item}" for item in scenarios
        )
        return (
            text.rstrip()
            + f"\n\n{CHECKLIST_START}\n## Validacao Manual Vervit\n{checklist}\n{CHECKLIST_END}\n"
        ).lstrip()

    if not isinstance(description, dict) or description.get("type") != "doc":
        raise JiraExecutorError("Descricao Jira deve ser texto ou ADF doc.")

    updated = copy.deepcopy(description)
    content = updated.setdefault("content", [])
    bounds = _managed_adf_bounds(content)
    states: dict[str, str] = {}
    if bounds:
        start, end = bounds
        states = _adf_states(content[start : end + 1])
        del content[start : end + 1]
        insertion = start
    else:
        insertion = len(content)
    managed_nodes = [
        _paragraph(CHECKLIST_START),
        {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Validacao Manual Vervit"}]},
        _task_list(scenarios, states),
        _paragraph(CHECKLIST_END),
    ]
    content[insertion:insertion] = managed_nodes
    return updated


def checklist_complete(description: Any) -> bool:
    if isinstance(description, str):
        if CHECKLIST_START not in description or CHECKLIST_END not in description:
            return False
        managed = description.split(CHECKLIST_START, 1)[1].split(CHECKLIST_END, 1)[0]
        items = [line for line in managed.splitlines() if line.startswith("- [")]
        return bool(items) and all(line.startswith(("- [x] ", "- [X] ")) for line in items)
    if isinstance(description, dict):
        content = description.get("content", [])
        bounds = _managed_adf_bounds(content)
        if not bounds:
            return False
        start, end = bounds
        items = [
            item
            for node in content[start : end + 1]
            if node.get("type") == "taskList"
            for item in node.get("content", [])
            if item.get("type") == "taskItem"
        ]
        return bool(items) and all(
            item.get("attrs", {}).get("state") == "DONE" for item in items
        )
    return False


def _canonical_hash(operation: str, payload: dict[str, Any]) -> str:
    raw = json.dumps(
        {"operation": operation, "payload": payload},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def create_operation_plan(operation: str, payload: dict[str, Any]) -> dict[str, Any]:
    if operation not in ALLOWED_OPERATIONS:
        raise JiraExecutorError(f"Operacao Jira nao permitida: {operation}")
    return {
        "operation": operation,
        "payload": payload,
        "sensitive": operation in SENSITIVE_OPERATIONS,
        "hash": _canonical_hash(operation, payload),
    }


def _adf_text(text: str) -> dict[str, Any]:
    return {"type": "doc", "version": 1, "content": [_paragraph(text)]}


Transport = Callable[[str, str, dict[str, str], dict[str, Any] | None], Any]


class JiraExecutor:
    def __init__(
        self,
        base_url: str,
        email: str,
        api_token: str,
        *,
        transport: Transport | None = None,
    ):
        if not base_url or not email or not api_token:
            raise JiraExecutorError("Credenciais Jira incompletas.")
        self.base_url = base_url.rstrip("/")
        self._authorization = base64.b64encode(f"{email}:{api_token}".encode()).decode()
        self.transport = transport or self._urllib_transport

    @classmethod
    def from_env(
        cls,
        base_url_env: str = "JIRA_BASE_URL",
        email_env: str = "JIRA_EMAIL",
        api_token_env: str = "JIRA_API_TOKEN",
        *,
        transport: Transport | None = None,
    ) -> "JiraExecutor":
        return cls(
            os.environ.get(base_url_env, ""),
            os.environ.get(email_env, ""),
            os.environ.get(api_token_env, ""),
            transport=transport,
        )

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {self._authorization}",
        }

    def _urllib_transport(
        self, method: str, url: str, headers: dict[str, str], payload: dict[str, Any] | None
    ) -> Any:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read()
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as exc:
            raise JiraExecutorError(f"Jira respondeu HTTP {exc.code}.") from exc
        except urllib.error.URLError as exc:
            raise JiraExecutorError(f"Falha ao acessar Jira: {exc.reason}") from exc

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        return self.transport(method, f"{self.base_url}{path}", self._headers(), payload)

    def create_plan(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        return create_operation_plan(operation, payload)

    def execute_plan(self, plan: dict[str, Any], *, confirmation_hash: str | None = None) -> Any:
        operation = plan.get("operation")
        payload = plan.get("payload")
        expected_hash = _canonical_hash(operation, payload)
        if plan.get("hash") != expected_hash:
            raise JiraExecutorError("Plano Jira foi alterado apos sua criacao.")
        if operation in SENSITIVE_OPERATIONS and confirmation_hash != expected_hash:
            raise JiraExecutorError("Operacao Jira sensivel exige confirmacao pelo hash.")
        handler = getattr(self, f"_op_{operation}", None)
        if handler is None:
            raise JiraExecutorError(f"Operacao Jira sem executor: {operation}")
        return handler(payload)

    def _op_get_issue(self, payload: dict[str, Any]) -> Any:
        return self._request("GET", f"/rest/api/3/issue/{payload['issueKey']}")

    def _op_get_project(self, payload: dict[str, Any]) -> Any:
        return self._request("GET", f"/rest/api/3/project/{payload['projectKey']}")

    def _op_list_my_open_issues(self, payload: dict[str, Any]) -> Any:
        project = payload.get("projectKey")
        project_filter = f"project = {project} AND " if project else ""
        jql = f"{project_filter}assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC"
        return self._request(
            "POST",
            "/rest/api/3/search/jql",
            {"jql": jql, "fields": ["summary", "issuetype", "status", "priority"], "maxResults": payload.get("maxResults", 25)},
        )

    def _op_list_project_versions(self, payload: dict[str, Any]) -> Any:
        return self._request(
            "GET", f"/rest/api/3/project/{payload['projectKey']}/versions"
        )

    def _op_list_transitions(self, payload: dict[str, Any]) -> Any:
        return self._request(
            "GET", f"/rest/api/3/issue/{payload['issueKey']}/transitions"
        )

    def _op_comment_checkpoint(self, payload: dict[str, Any]) -> Any:
        return self._request(
            "POST",
            f"/rest/api/3/issue/{payload['issueKey']}/comment",
            {"body": _adf_text(payload["text"])},
        )

    def _op_update_checklist(self, payload: dict[str, Any]) -> Any:
        issue = self._op_get_issue({"issueKey": payload["issueKey"]})
        description = issue.get("fields", {}).get("description")
        updated = update_managed_checklist(description, payload["scenarios"])
        return self._request(
            "PUT",
            f"/rest/api/3/issue/{payload['issueKey']}",
            {"fields": {"description": updated}},
        )

    def _op_create_issue(self, payload: dict[str, Any]) -> Any:
        return self._request("POST", "/rest/api/3/issue", {"fields": payload})

    def _op_transition_issue(self, payload: dict[str, Any]) -> Any:
        return self._request(
            "POST",
            f"/rest/api/3/issue/{payload['issueKey']}/transitions",
            {"transition": {"id": str(payload["transitionId"])}},
        )

    def _op_link_issues(self, payload: dict[str, Any]) -> Any:
        return self._request(
            "POST",
            "/rest/api/3/issueLink",
            {
                "type": {"name": payload.get("linkType", "Relates")},
                "inwardIssue": {"key": payload["inwardIssue"]},
                "outwardIssue": {"key": payload["outwardIssue"]},
            },
        )

    def _op_create_version(self, payload: dict[str, Any]) -> Any:
        return self._request(
            "POST",
            "/rest/api/3/version",
            {
                "project": int(payload["project"]),
                "name": payload["name"],
                "description": payload.get("description", f"Release Vervit {payload['name']}"),
            },
        )

    def _op_apply_fix_version(self, payload: dict[str, Any]) -> Any:
        return self._request(
            "PUT",
            f"/rest/api/3/issue/{payload['issueKey']}",
            {"update": {"fixVersions": [{"add": {"id": str(payload["versionId"])}}]}},
        )

    def _op_release_version(self, payload: dict[str, Any]) -> Any:
        return self._request(
            "PUT",
            f"/rest/api/3/version/{payload['versionId']}",
            {
                "released": True,
                "releaseDate": payload.get("releaseDate", date.today().isoformat()),
            },
        )

    def _op_edit_issue(self, payload: dict[str, Any]) -> Any:
        return self._request(
            "PUT", f"/rest/api/3/issue/{payload['issueKey']}", {"fields": payload["fields"]}
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Planeja e executa operacoes Jira Vervit.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="Gera plano com hash.")
    plan_parser.add_argument("operation", choices=sorted(ALLOWED_OPERATIONS))
    plan_parser.add_argument("payload", help="JSON inline ou @arquivo.json")
    plan_parser.add_argument("--output")

    auto_parser = subparsers.add_parser("auto", help="Executa operacao automatica permitida.")
    auto_parser.add_argument("operation", choices=sorted(AUTOMATIC_OPERATIONS))
    auto_parser.add_argument("payload", help="JSON inline ou @arquivo.json")

    execute_parser = subparsers.add_parser("execute", help="Executa plano existente.")
    execute_parser.add_argument("plan", help="Arquivo JSON contendo operation, payload e hash.")
    execute_parser.add_argument("--confirm-hash")

    args = parser.parse_args()

    def load_payload(value: str) -> dict[str, Any]:
        if value.startswith("@"):
            return json.loads(Path(value[1:]).read_text(encoding="utf-8"))
        return json.loads(value)

    if args.command == "plan":
        result = create_operation_plan(args.operation, load_payload(args.payload))
        if args.output:
            Path(args.output).write_text(
                json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    elif args.command == "auto":
        executor = JiraExecutor.from_env()
        plan = executor.create_plan(args.operation, load_payload(args.payload))
        result = executor.execute_plan(plan)
    else:
        executor = JiraExecutor.from_env()
        plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
        result = executor.execute_plan(plan, confirmation_hash=args.confirm_hash)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
