from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from scripts.init_project import initialize_project
    from scripts.migrate_project import migrate_project
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts.init_project import initialize_project  # type: ignore[import-untyped]
    from scripts.migrate_project import migrate_project  # type: ignore[import-untyped]


def init_project(
    *,
    target: Path | None = None,
    force: bool = False,
    install_skills: bool = False,
) -> None:
    root = target.resolve() if target else Path.cwd()

    result: dict[str, object] = {"target": str(root)}

    result["migration"] = migrate_project(root, dry_run=False)

    result["files"] = initialize_project(
        root,
        force=force,
        install_skills=install_skills,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
