from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def load_creds(target: Path | None = None) -> dict[str, str]:
    root = target.resolve() if target else Path.cwd()
    local_env = root / ".env.vervit.local"
    env = dict(os.environ)

    if local_env.exists():
        for raw_line in local_env.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            if k in {"JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"} and k not in env:
                env[k] = v.strip().strip("'\"")

    missing = [k for k in ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN") if not env.get(k)]
    if missing:
        print(f"Erro: variaveis Jira ausentes: {', '.join(missing)}", file=sys.stderr)
        print("Defina em .env.vervit.local ou em environment.", file=sys.stderr)
        sys.exit(1)

    return env


def _request(env: dict[str, str], path: str, *, method: str = "GET", body: str | None = None) -> dict:
    base = env["JIRA_BASE_URL"].rstrip("/")
    url = f"{base}{path}"
    token = base64.b64encode(f"{env['JIRA_EMAIL']}:{env['JIRA_API_TOKEN']}".encode()).decode()

    headers = {
        "Authorization": f"Basic {token}",
        "Accept": "application/json",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"

    req = Request(url, data=body.encode() if body else None, headers=headers, method=method)
    try:
        with urlopen(req) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except HTTPError as e:
        detail = e.read().decode()
        print(f"Erro HTTP {e.code}: {detail}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"Erro de conexao: {e.reason}", file=sys.stderr)
        sys.exit(1)


def list_issues(*, project: str | None = None, board: int | None = None) -> None:
    env = load_creds()
    if board is not None:
        data = _request(env, f"/rest/agile/1.0/board/{board}/issue?maxResults=50")
    elif project:
        jql = f"project={project}+ORDER+BY+created+DESC"
        data = _request(env, f"/rest/api/3/search?jql={jql}&maxResults=50")
    else:
        data = _request(env, "/rest/api/3/project")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def get_issue(issue_key: str) -> None:
    env = load_creds()
    data = _request(env, f"/rest/api/3/issue/{issue_key}")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def create_issue(*, project: str, summary: str, issue_type: str) -> None:
    type_map = {"bug": "Bug", "feature": "Story", "improvement": "Story"}
    env = load_creds()
    payload = {
        "fields": {
            "project": {"key": project},
            "summary": summary,
            "issuetype": {"name": type_map.get(issue_type, "Story")},
        }
    }
    result = _request(env, "/rest/api/3/issue", method="POST", body=json.dumps(payload))
    print(json.dumps(result, ensure_ascii=False, indent=2))


def transition_issue(issue_key: str, to: str) -> None:
    env = load_creds()
    transitions = _request(env, f"/rest/api/3/issue/{issue_key}/transitions")
    target_id = None
    for t in transitions.get("transitions", []):
        if t.get("name", "").lower() == to.lower():
            target_id = t["id"]
            break
    if not target_id:
        available = [t["name"] for t in transitions.get("transitions", [])]
        print(f"Transicao '{to}' nao encontrada. Disponiveis: {available}", file=sys.stderr)
        sys.exit(1)

    result = _request(
        env,
        f"/rest/api/3/issue/{issue_key}/transitions",
        method="POST",
        body=json.dumps({"transition": {"id": target_id}}),
    )
    print(json.dumps(result or {"status": "ok", "transition": to}, ensure_ascii=False, indent=2))


def comment_issue(issue_key: str, text: str) -> None:
    env = load_creds()
    body = {
        "body": {
            "content": [
                {
                    "content": [{"text": text, "type": "text"}],
                    "type": "paragraph",
                }
            ]
        }
    }
    result = _request(env, f"/rest/api/3/issue/{issue_key}/comment", method="POST", body=json.dumps(body))
    print(json.dumps(result, ensure_ascii=False, indent=2))
