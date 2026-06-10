"""Ensure `vervit` CLI is on PATH, installing via pip editable if needed."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def _vervit_on_path() -> bool:
    return shutil.which("vervit") is not None


def install_cli() -> bool:
    if _vervit_on_path():
        return False
    print("Instalando vervit CLI (pip install -e) ...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", str(PLUGIN_ROOT)],
        check=True,
    )
    return True


if __name__ == "__main__":
    installed = install_cli()
    if installed:
        print("vervit CLI instalado com sucesso.")
