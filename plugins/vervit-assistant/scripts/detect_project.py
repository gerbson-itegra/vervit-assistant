from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def detect_package_manager(root: Path) -> str | None:
    lockfiles = [
        ("pnpm-lock.yaml", "pnpm"),
        ("yarn.lock", "yarn"),
        ("package-lock.json", "npm"),
        ("bun.lockb", "bun"),
        ("bun.lock", "bun"),
    ]
    for filename, manager in lockfiles:
        if (root / filename).exists():
            return manager
    if (root / "package.json").exists():
        return "npm"
    return None


def list_dirs(root: Path) -> list[str]:
    ignored = {".git", "node_modules", "dist", "build", ".next", ".venv", "venv", "__pycache__"}
    dirs: list[str] = []
    for item in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if item.is_dir() and item.name not in ignored:
            dirs.append(item.name)
    return dirs[:40]


def detect_project(root: Path) -> dict[str, Any]:
    package_json = read_json(root / "package.json") if (root / "package.json").exists() else {}
    scripts = package_json.get("scripts", {}) if isinstance(package_json.get("scripts", {}), dict) else {}
    dependencies = {}
    for key in ("dependencies", "devDependencies"):
        value = package_json.get(key, {})
        if isinstance(value, dict):
            dependencies.update(value)

    markers = {
        "package_json": (root / "package.json").exists(),
        "vite": (root / "vite.config.ts").exists() or (root / "vite.config.js").exists(),
        "next": (root / "next.config.js").exists() or (root / "next.config.mjs").exists(),
        "tsconfig": (root / "tsconfig.json").exists(),
        "pyproject": (root / "pyproject.toml").exists(),
        "requirements": (root / "requirements.txt").exists(),
        "supabase": (root / "supabase").exists(),
        "docker": (root / "Dockerfile").exists() or (root / "docker-compose.yml").exists(),
        "github_actions": (root / ".github" / "workflows").exists(),
    }

    frameworks = []
    for name in ("react", "vite", "next", "vue", "svelte", "tailwindcss", "@supabase/supabase-js"):
        if name in dependencies or markers.get(name.replace("@supabase/supabase-js", "supabase"), False):
            frameworks.append(name)

    return {
        "root": str(root),
        "package_manager": detect_package_manager(root),
        "package_name": package_json.get("name"),
        "scripts": scripts,
        "dependencies_detected": sorted(frameworks),
        "markers": markers,
        "top_level_directories": list_dirs(root),
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Detect project metadata for Vervit Assistant.")
    parser.add_argument("--target", default=".", help="Project root to inspect.")
    args = parser.parse_args()

    root = Path(args.target).resolve()
    print(json.dumps(detect_project(root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
