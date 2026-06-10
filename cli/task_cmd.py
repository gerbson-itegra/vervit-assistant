from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from scripts.task_artifacts import create_task_artifacts
    from scripts.workflow_guard import can_close_task, release_ready
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts.task_artifacts import create_task_artifacts
    from scripts.workflow_guard import can_close_task, release_ready


def start(
    issue_key: str,
    *,
    summary: str,
    task_type: str,
    track: str = "planned",
    target: Path | None = None,
) -> None:
    root = target.resolve() if target else Path.cwd()
    branch = f"{track}/{issue_key.lower()}-{summary.split()[0].lower() if summary else 'task'}"
    results = create_task_artifacts(
        root,
        issue_key=issue_key,
        summary=summary,
        task_type=task_type,
        track=track,
        branch=branch,
    )
    print(json.dumps({"artifacts": results}, ensure_ascii=False, indent=2))


def status(
    issue_key: str,
    *,
    target: Path | None = None,
) -> None:
    root = target.resolve() if target else Path.cwd()
    state_path = root / "docs" / f"{issue_key}_state.json"
    if not state_path.exists():
        print(f"Artefato nao encontrado: {state_path}", file=sys.stderr)
        sys.exit(1)
    state = json.loads(state_path.read_text(encoding="utf-8"))
    gates = {
        "prdApproved": state.get("prdApproved", False),
        "manualChecklistComplete": state.get("manualChecklistComplete", False),
        "automatedTestsPassed": state.get("automatedTestsPassed", False),
        "mergedTo": state.get("mergedTo"),
    }
    try:
        closable = can_close_task(state)
    except Exception as e:
        closable = False
        gates["blocker"] = str(e)
    gates["canClose"] = closable
    print(json.dumps(gates, ensure_ascii=False, indent=2))
