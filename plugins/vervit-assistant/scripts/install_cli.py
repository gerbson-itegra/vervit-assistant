"""Ensure `vervit` CLI is on PATH, installing via pip editable if needed."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def _vervit_on_path() -> bool:
    return shutil.which("vervit") is not None


def _pip_install(*args: str) -> bool:
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", *args, str(PLUGIN_ROOT)],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def install_cli() -> bool:
    if _vervit_on_path():
        return False

    print("Instalando vervit CLI...")

    if _pip_install("-e"):
        print("vervit CLI instalado com sucesso (pip install -e).")
        return True

    print("pip install -e falhou, tentando com --no-build-isolation...")
    if _pip_install("-e", "--no-build-isolation"):
        print("vervit CLI instalado com sucesso (no-build-isolation).")
        return True

    print("pip install -e falhou, tentando upgrade do pip...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        check=False,
        capture_output=True,
    )
    if _pip_install("-e"):
        print("vervit CLI instalado com sucesso (apos upgrade pip).")
        return True

    print(
        "Nao foi possivel instalar o CLI vervit globalmente.\n"
        'Use o script direto: set PYTHONPATH=<plugin> && python -m cli <comando>\n'
        "Ou instale manualmente: pip install -e <plugin>"
    )
    return False


if __name__ == "__main__":
    installed = install_cli()
    if installed:
        print("vervit CLI instalado com sucesso.")
