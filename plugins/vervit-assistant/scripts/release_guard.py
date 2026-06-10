from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable


SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
ISSUE_KEY_RE = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")
TASK_TYPES = {"bug", "feature", "improvement"}
DELIVERY_TRACKS = {"hotfix", "planned"}


class ReleasePolicyError(ValueError):
    """Raised when an operation violates the Vervit release policy."""


@dataclass(frozen=True, order=True)
class SemVer:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: str) -> "SemVer":
        match = SEMVER_RE.fullmatch(value)
        if not match:
            raise ReleasePolicyError(
                f"Versao invalida: {value!r}. Use o formato Jira X.Y.Z."
            )
        return cls(*(int(part) for part in match.groups()))

    def bump(self, level: str) -> "SemVer":
        if level == "major":
            return SemVer(self.major + 1, 0, 0)
        if level == "minor":
            return SemVer(self.major, self.minor + 1, 0)
        if level == "patch":
            return SemVer(self.major, self.minor, self.patch + 1)
        raise ReleasePolicyError(f"Incremento SemVer desconhecido: {level}")

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def required_bump(
    task_types: Iterable[str], *, breaking: bool = False, hotfix: bool = False
) -> str:
    normalized = {task_type.lower() for task_type in task_types}
    unknown = normalized - TASK_TYPES
    if unknown:
        raise ReleasePolicyError(f"Tipos de tarefa desconhecidos: {sorted(unknown)}")
    if not normalized:
        raise ReleasePolicyError("Uma release precisa conter ao menos uma tarefa.")
    if hotfix:
        return "patch"
    if breaking:
        return "major"
    if "feature" in normalized:
        return "minor"
    return "patch"


def calculate_next_version(
    current_version: str,
    task_types: Iterable[str],
    *,
    breaking: bool = False,
    hotfix: bool = False,
) -> str:
    current = SemVer.parse(current_version)
    return str(current.bump(required_bump(task_types, breaking=breaking, hotfix=hotfix)))


def validate_requested_version(
    current_version: str,
    requested_version: str,
    task_types: Iterable[str],
    existing_tags: Iterable[str],
    *,
    breaking: bool = False,
    hotfix: bool = False,
) -> bool:
    expected = calculate_next_version(
        current_version, task_types, breaking=breaking, hotfix=hotfix
    )
    if requested_version != expected:
        raise ReleasePolicyError(
            f"Versao incompativel. Esperada {expected}; recebida {requested_version}."
        )
    tag = f"v{requested_version}"
    if tag in set(existing_tags):
        raise ReleasePolicyError(f"A tag {tag} ja existe.")
    return True


def latest_version_from_tags(tags: Iterable[str]) -> str:
    versions = []
    for tag in tags:
        if tag.startswith("v") and SEMVER_RE.fullmatch(tag[1:]):
            versions.append(SemVer.parse(tag[1:]))
    if not versions:
        return "0.0.0"
    return str(max(versions))


def _slugify(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", ascii_value.lower())).strip(
        "-"
    )


def branch_name(issue_key: str, summary: str, task_type: str, track: str) -> str:
    task_type = task_type.lower()
    track = track.lower()
    if not ISSUE_KEY_RE.fullmatch(issue_key):
        raise ReleasePolicyError(f"Chave Jira invalida: {issue_key}")
    if task_type not in TASK_TYPES:
        raise ReleasePolicyError(f"Tipo de tarefa invalido: {task_type}")
    if track not in DELIVERY_TRACKS:
        raise ReleasePolicyError(f"Trilho de entrega invalido: {track}")
    slug = _slugify(summary)
    if not slug:
        raise ReleasePolicyError("O resumo Jira precisa gerar um slug nao vazio.")
    prefix = "hotfix" if track == "hotfix" else task_type
    return f"{prefix}/{issue_key}-{slug[:64].rstrip('-')}"


def integration_gate(
    *,
    worktree_clean: bool,
    automated_tests_passed: bool,
    manual_checklist_complete: bool,
    release_notes_complete: bool,
    branch_synchronized: bool,
) -> bool:
    checks = {
        "worktree limpa": worktree_clean,
        "testes automatizados": automated_tests_passed,
        "checklist manual": manual_checklist_complete,
        "release notes": release_notes_complete,
        "branch sincronizada": branch_synchronized,
    }
    pending = [name for name, complete in checks.items() if not complete]
    if pending:
        raise ReleasePolicyError("Integracao bloqueada: " + ", ".join(pending))
    return True


def build_delivery_actions(
    *, track: str, task_branch: str, main_branch: str = "main", release_branch: str = "release"
) -> list[dict[str, str]]:
    if track == "hotfix":
        return [
            {"action": "merge_no_ff", "source": task_branch, "target": main_branch},
            {"action": "tag_release", "source": main_branch, "target": main_branch},
            {"action": "merge_no_ff", "source": main_branch, "target": release_branch},
        ]
    if track == "planned":
        return [
            {"action": "merge_no_ff", "source": task_branch, "target": release_branch}
        ]
    raise ReleasePolicyError(f"Trilho de entrega invalido: {track}")


def build_release_publication_actions(
    version: str, *, main_branch: str = "main", release_branch: str = "release"
) -> list[dict[str, str]]:
    SemVer.parse(version)
    return [
        {"action": "merge_no_ff", "source": release_branch, "target": main_branch},
        {"action": "tag_release", "source": main_branch, "tag": f"v{version}"},
        {"action": "merge_no_ff", "source": main_branch, "target": release_branch},
    ]


def ensure_single_active_release(active_release_keys: Iterable[str]) -> bool:
    releases = [key for key in active_release_keys if key]
    if len(releases) > 1:
        raise ReleasePolicyError(
            "Somente uma release planejada pode estar ativa: " + ", ".join(releases)
        )
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida a politica de releases Vervit.")
    parser.add_argument("current_version")
    parser.add_argument("task_types", nargs="+", choices=sorted(TASK_TYPES))
    parser.add_argument("--breaking", action="store_true")
    parser.add_argument("--hotfix", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            {
                "nextVersion": calculate_next_version(
                    args.current_version,
                    args.task_types,
                    breaking=args.breaking,
                    hotfix=args.hotfix,
                )
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
