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


def _render_prd(issue_key: str, summary: str, task_type: str, track: str, branch: str) -> str:
    type_specific = {
        "bug": "## Evidencias E Causa Raiz\n\nA investigar com systematic-debugging.",
        "feature": "## Experiencia E Regras De Negocio\n\nA refinar com brainstorming.",
        "improvement": "## Mudanca Pequena Proposta\n\nA refinar com contexto e plano compactos.",
    }[task_type]
    return f"""# {issue_key}: {summary}

## Rastreabilidade

- Jira: `{issue_key}`
- Tipo confirmado: `{task_type}`
- Trilho: `{track}`
- Branch: `{branch}`
- Status do PRD: aguardando aprovacao

## Objetivo

A confirmar a partir da descricao e dos criterios Jira.

## Escopo

### Incluido

A confirmar.

### Fora De Escopo

A confirmar.

{type_specific}

## Impactos Tecnicos

A mapear no codebase.

## Criterios De Aceitacao

A confirmar.

## Cenarios De Validacao Manual

A definir com Superpowers antes da implementacao.

## Testes Automatizados

A definir e executar com TDD para mudancas comportamentais.

## Riscos E Perguntas Abertas

A confirmar antes da aprovacao do PRD.
"""


def _render_trace(issue_key: str, branch: str) -> str:
    timestamp = datetime.now(timezone.utc).isoformat()
    return f"""# Trace {issue_key}

## {timestamp}

- Artefatos da tarefa criados.
- Branch planejada: `{branch}`.
- Nenhuma credencial, token ou anexo deve ser registrado neste arquivo.
"""


def create_task_artifacts(
    root: Path,
    *,
    issue_key: str,
    summary: str,
    task_type: str,
    track: str,
    branch: str,
) -> dict[str, str]:
    task_dir = root.resolve() / ".specs" / "jira" / issue_key
    state = new_task_state(issue_key, task_type, track, branch)
    return {
        "PRD.md": _write_new(
            task_dir / "PRD.md", _render_prd(issue_key, summary, task_type, track, branch)
        ),
        "TRACE.md": _write_new(task_dir / "TRACE.md", _render_trace(issue_key, branch)),
        "state.json": _write_new(
            task_dir / "state.json", json.dumps(state, ensure_ascii=False, indent=2)
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
