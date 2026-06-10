from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping


JIRA_ENV_NAMES = ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN")


def load_vervit_env(
    root: Path, env: Mapping[str, str] | None = None
) -> dict[str, str]:
    loaded = dict(os.environ if env is None else env)
    path = root.resolve() / ".env.vervit.local"
    if not path.exists():
        return loaded

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if name in JIRA_ENV_NAMES and name not in loaded:
            loaded[name] = value.strip().strip("'\"")
    return loaded
