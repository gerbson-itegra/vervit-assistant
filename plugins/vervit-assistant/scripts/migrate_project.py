from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


OLD_MARKERS = [
    ".agents/main-agent.md",
    ".agents/vervit-assistant.json",
    ".specs/codebase/STACK.md",
]

OLD_AGENTS = ".agents"
OLD_SPECS = ".specs"
OLD_ROOT_AGENTS = "AGENTS.md"

NEW_VERVIT = "vervit-assistant"
NEW_DOCS = "docs"
NEW_CODEBASE = "docs/_codebase"


def detect_old_structure(root: Path) -> bool:
    return any((root / m).exists() for m in OLD_MARKERS)


def _backup(path: Path) -> None:
    if path.exists():
        backup = path.with_name(f"{path.name}.bak")
        if not backup.exists():
            shutil.copy2(path, backup)


def _safe_write(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return "unchanged"
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return "written"


def _move_file(src: Path, dst: Path) -> str | None:
    if not src.exists():
        return None
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return "exists"
    shutil.move(str(src), str(dst))
    return "moved"


def _copy_file(src: Path, dst: Path) -> str | None:
    if not src.exists():
        return None
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return "exists"
    _backup(src)
    shutil.copy2(str(src), str(dst))
    return "copied"


def migrate_project(root: Path, *, dry_run: bool = False) -> dict[str, Any]:
    root = root.resolve()
    detected = detect_old_structure(root)
    result: dict[str, Any] = {
        "root": str(root),
        "oldStructureDetected": detected,
        "actions": [] if dry_run else None,
        "applied": [],
        "errors": [],
    }

    if not detected:
        result["status"] = "no_old_structure"
        return result

    actions: list[str] = []

    def plan(description: str, apply_fn=None):
        actions.append(description)
        if not dry_run and apply_fn is not None:
            try:
                outcome = apply_fn()
                result["applied"].append(f"{description}: {outcome}")
            except Exception as e:
                result["errors"].append(f"{description}: {e}")

    # 1. AGENTS.md root → vervit-assistant/AGENTS.md
    old_agents = root / OLD_ROOT_AGENTS
    new_agents = root / NEW_VERVIT / "AGENTS.md"
    if old_agents.exists():
        plan("AGENTS.md → vervit-assistant/AGENTS.md", lambda: _copy_file(old_agents, new_agents))

    # 2. .agents/main-agent.md → vervit-assistant/agent-profile.md
    old_profile = root / OLD_AGENTS / "main-agent.md"
    new_profile = root / NEW_VERVIT / "agent-profile.md"
    if old_profile.exists():
        plan("agent profile → vervit-assistant/agent-profile.md", lambda: _copy_file(old_profile, new_profile))

    # 3. .agents/vervit-assistant.json → vervit-assistant/config.json
    old_config = root / OLD_AGENTS / "vervit-assistant.json"
    new_config = root / NEW_VERVIT / "config.json"
    if old_config.exists():
        plan("config → vervit-assistant/config.json", lambda: _copy_file(old_config, new_config))

    # 4. .agents/vervit-onboarding.json → vervit-assistant/state.json
    old_state = root / OLD_AGENTS / "vervit-onboarding.json"
    new_state = root / NEW_VERVIT / "state.json"
    if old_state.exists():
        plan("onboarding state → vervit-assistant/state.json", lambda: _copy_file(old_state, new_state))

    # 5. .specs/codebase/* → docs/_codebase/
    old_codebase = root / OLD_SPECS / "codebase"
    new_codebase = root / NEW_CODEBASE
    if old_codebase.exists():
        for file in sorted(old_codebase.iterdir()):
            if file.is_file():
                dst = new_codebase / file.name
                plan(f"{file.relative_to(root)} → {dst.relative_to(root)}",
                     lambda src=file, d=dst: _move_file(src, d))

    # 6. .specs/jira/<KEY>/ → docs/<KEY>_*.md/json (flat)
    old_jira = root / OLD_SPECS / "jira"
    if old_jira.exists():
        for task_dir in sorted(old_jira.iterdir()):
            if not task_dir.is_dir():
                continue
            key = task_dir.name
            if key.startswith("."):
                continue
            for old_name, suffix in [("PRD.md", "_PRD.md"), ("TRACE.md", "_TRACE.md"), ("state.json", "_state.json")]:
                src = task_dir / old_name
                dst = root / NEW_DOCS / f"{key}{suffix}"
                if src.exists():
                    plan(f"{src.relative_to(root)} → {dst.relative_to(root)}",
                         lambda s=src, d=dst: _move_file(s, d))

    # 7. Create docs/README.md
    new_readme = root / NEW_DOCS / "README.md"
    if not new_readme.exists():
        readme_content = (
            "# Documentacao Vervit\n\n"
            "## Estrutura\n\n"
            "- `_codebase/`: documentacao estrutural do sistema.\n"
            "- `<KEY>_issue.json`: dados da issue Jira.\n"
            "- `<KEY>_PRD.md`: requisitos e criterios da tarefa.\n"
            "- `<KEY>_TRACE.md`: decisoes, operacoes, testes e provedores.\n"
            "- `<KEY>_state.json`: gates estruturados da tarefa.\n\n"
            "Nunca registre credenciais, tokens, anexos ou dados binarios nestes arquivos.\n"
        )
        plan("criar docs/README.md",
             lambda: _safe_write(new_readme, readme_content))

    # 8. Update AGENTS.md to reference new paths
    if new_agents.exists():
        plan("atualizar referencias em vervit-assistant/AGENTS.md", lambda: _update_agents_refs(new_agents))

    # 9. Delete old .agents/ and .specs/
    for old_dir_name in [OLD_AGENTS, OLD_SPECS]:
        old_dir = root / old_dir_name
        if old_dir.exists():
            plan(f"remover {old_dir_name}/", lambda d=old_dir: _remove_dir(d))

    # 10. Delete root AGENTS.md (content is now in vervit-assistant/)
    if old_agents.exists():
        plan(f"remover {OLD_ROOT_AGENTS} da raiz", lambda: old_agents.unlink(missing_ok=True))

    if dry_run:
        result["actions"] = actions
        result["status"] = "dry_run"
    else:
        result["status"] = "migrated" if not result["errors"] else "partial"

    return result


def _update_agents_refs(agents_path: Path) -> str:
    content = agents_path.read_text(encoding="utf-8")
    old_refs = {
        ".agents/main-agent.md": "vervit-assistant/agent-profile.md",
        ".agents/vervit-assistant.json": "vervit-assistant/config.json",
    }
    updated = content
    for old_ref, new_ref in old_refs.items():
        updated = updated.replace(old_ref, new_ref)
    if updated != content:
        _backup(agents_path)
        agents_path.write_text(updated, encoding="utf-8")
        return "updated"
    return "unchanged"


def _remove_dir(d: Path) -> str:
    if d.exists():
        shutil.rmtree(d)
        return "removed"
    return "not_found"


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Migrar projeto Vervit da estrutura antiga para a nova.")
    parser.add_argument("--target", default=".", help="Raiz do projeto")
    parser.add_argument("--apply", action="store_true", help="Executar migracao (padrao: dry-run)")
    args = parser.parse_args()

    root = Path(args.target).resolve()
    result = migrate_project(root, dry_run=not args.apply)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
