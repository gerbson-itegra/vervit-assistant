from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

try:
    from .workflow_guard import new_task_state
except ImportError:
    from workflow_guard import new_task_state


def _write_new(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return "unchanged"
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return "written"


def _render_issue(issue_key: str, summary: str, task_type: str, track: str) -> str:
    return json.dumps(
        {
            "issueKey": issue_key,
            "summary": summary,
            "type": task_type,
            "track": track,
            "createdAt": datetime.now(timezone.utc).isoformat(),
        },
        ensure_ascii=False,
        indent=2,
    )


def _render_prd(issue_key: str, summary: str, task_type: str, track: str, branch: str) -> str:
    type_specific = {
        "bug": "## Evidencias E Causa Raiz",
        "feature": "## Experiencia E Regras De Negocio",
        "improvement": "## Mudanca Proposta",
    }[task_type]
    return f"""# {issue_key}: {summary}

## Rastreabilidade

- Jira/tipo/trilho: `{issue_key}` / `{task_type}` / `{track}`
- Branch: `{branch}`; PRD aguardando aprovacao

## Objetivo

A confirmar.

{type_specific}

## Escopo E Criterios

A confirmar.

## Impactos E Riscos

A confirmar.

## Cenarios De Validacao Manual

A definir antes da implementacao.

## Testes Automatizados

A definir para mudancas comportamentais.
"""


def _render_trace(issue_key: str, branch: str) -> str:
    timestamp = datetime.now(timezone.utc).isoformat()
    return f"""# Trace {issue_key}

## {timestamp}

- Artefatos da tarefa criados.
- Branch planejada: `{branch}`.
- Nenhuma credencial, token ou anexo deve ser registrado neste arquivo.
"""


def _flat_path(docs_dir: Path, issue_key: str, suffix: str) -> Path:
    return docs_dir / f"{issue_key}{suffix}"


def create_task_artifacts(
    root: Path,
    *,
    issue_key: str,
    summary: str,
    task_type: str,
    track: str,
    branch: str,
) -> dict[str, str]:
    docs_dir = root.resolve() / "docs"
    state = new_task_state(issue_key, task_type, track, branch)
    return {
        f"{issue_key}_issue.json": _write_new(
            _flat_path(docs_dir, issue_key, "_issue.json"),
            _render_issue(issue_key, summary, task_type, track),
        ),
        f"{issue_key}_PRD.md": _write_new(
            _flat_path(docs_dir, issue_key, "_PRD.md"),
            _render_prd(issue_key, summary, task_type, track, branch),
        ),
        f"{issue_key}_TRACE.md": _write_new(
            _flat_path(docs_dir, issue_key, "_TRACE.md"),
            _render_trace(issue_key, branch),
        ),
        f"{issue_key}_state.json": _write_new(
            _flat_path(docs_dir, issue_key, "_state.json"),
            json.dumps(state, ensure_ascii=False, indent=2),
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria artefatos rastreaveis de tarefa Jira.")
    parser.add_argument("issue_key")
    parser.add_argument("summary")
    parser.add_argument("task_type", choices=["bug", "feature", "improvement"])
    parser.add_argument("track", choices=["hotfix", "planned"])
    parser.add_argument("branch")
    parser.add_argument("--target", default=".")
    args = parser.parse_args()
    results = create_task_artifacts(
        Path(args.target),
        issue_key=args.issue_key,
        summary=args.summary,
        task_type=args.task_type,
        track=args.track,
        branch=args.branch,
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
