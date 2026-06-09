from __future__ import annotations

import json
from typing import Any


TASK_TYPES = {"bug", "feature", "improvement"}
TRACKS = {"hotfix", "planned"}


class WorkflowGateError(ValueError):
    """Raised when a Vervit workflow tries to cross an incomplete gate."""


def superpowers_flow(task_type: str, *, behavioral_change: bool = True) -> list[str]:
    task_type = task_type.lower()
    if task_type not in TASK_TYPES:
        raise WorkflowGateError(f"Tipo de tarefa desconhecido: {task_type}")
    if task_type == "bug":
        return [
            "superpowers:systematic-debugging",
            "superpowers:test-driven-development",
            "superpowers:requesting-code-review",
            "superpowers:verification-before-completion",
        ]
    if task_type == "feature":
        return [
            "superpowers:brainstorming",
            "superpowers:writing-plans",
            "superpowers:test-driven-development",
            "superpowers:requesting-code-review",
            "superpowers:verification-before-completion",
        ]
    flow = ["superpowers:brainstorming"]
    if behavioral_change:
        flow.append("superpowers:test-driven-development")
    flow.extend(
        [
            "superpowers:requesting-code-review",
            "superpowers:verification-before-completion",
        ]
    )
    return flow


def _require(state: dict[str, Any], required: dict[str, Any], context: str) -> None:
    pending = [
        key
        for key, expected in required.items()
        if state.get(key) != expected
    ]
    if pending:
        raise WorkflowGateError(f"{context} bloqueado: " + ", ".join(pending))


def can_close_task(state: dict[str, Any]) -> bool:
    track = state.get("track")
    if track not in TRACKS:
        raise WorkflowGateError(f"Trilho de entrega desconhecido: {track}")
    target = "main" if track == "hotfix" else "release"
    _require(
        state,
        {
            "prdApproved": True,
            "manualChecklistComplete": True,
            "automatedTestsPassed": True,
            "mergedTo": target,
        },
        "Fechamento da tarefa",
    )
    return True


def release_ready(state: dict[str, Any]) -> bool:
    _require(
        state,
        {
            "scopeFrozen": True,
            "fixVersionCreated": True,
            "generalRegressionComplete": True,
            "automatedTestsPassed": True,
            "releaseNotesComplete": True,
            "mainReleaseSynchronized": True,
        },
        "Publicacao da release",
    )
    return True


def new_task_state(
    issue_key: str, task_type: str, track: str, branch: str
) -> dict[str, Any]:
    if task_type not in TASK_TYPES or track not in TRACKS:
        raise WorkflowGateError("Tipo de tarefa ou trilho invalido.")
    return {
        "schemaVersion": 1,
        "issueKey": issue_key,
        "taskType": task_type,
        "track": track,
        "branch": branch,
        "prdApproved": False,
        "manualChecklistComplete": False,
        "automatedTestsPassed": False,
        "mergedTo": None,
        "superpowersFlow": superpowers_flow(task_type),
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Seleciona o fluxo Superpowers Vervit.")
    parser.add_argument("task_type", choices=sorted(TASK_TYPES))
    parser.add_argument("--non-behavioral", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            {
                "flow": superpowers_flow(
                    args.task_type, behavioral_change=not args.non_behavioral
                )
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
