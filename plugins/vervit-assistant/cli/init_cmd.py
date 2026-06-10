from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from scripts.init_project import initialize_project
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts.init_project import initialize_project


def init_project(
    *,
    target: Path | None = None,
    force: bool = False,
    install_skills: bool = False,
) -> None:
    root = target.resolve() if target else Path.cwd()
    results = initialize_project(
        root,
        force=force,
        install_skills=install_skills,
    )
    print(json.dumps({"target": str(root), "files": results}, ensure_ascii=False, indent=2))
