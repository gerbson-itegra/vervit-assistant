"""Build the canonical marketplace package from the plugin source at repository root."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "plugins" / "vervit-assistant"
PLUGIN_PATHS = (".codex-plugin", "assets", "scripts", "skills", "cli")
PLUGIN_ROOT_FILES = ("pyproject.toml",)
BUILD_ONLY_FILES = {"build_marketplace_plugin.py", "install_plugin.ps1"}


def ignore_generated(_directory: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name == "__pycache__"
        or name in BUILD_ONLY_FILES
        or name.endswith((".pyc", ".pyo"))
    }


def build_marketplace_plugin() -> Path:
    if DESTINATION.exists():
        shutil.rmtree(DESTINATION)
    DESTINATION.mkdir(parents=True)

    for relative_path in PLUGIN_PATHS:
        source = ROOT / relative_path
        shutil.copytree(
            source,
            DESTINATION / relative_path,
            ignore=ignore_generated,
        )

    for root_file in PLUGIN_ROOT_FILES:
        source = ROOT / root_file
        if source.exists():
            shutil.copy2(source, DESTINATION / root_file)

    return DESTINATION


if __name__ == "__main__":
    print(build_marketplace_plugin())
