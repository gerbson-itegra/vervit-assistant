from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlsplit, urlunsplit

try:
    from .detect_project import detect_project
    from .vervit_env import load_vervit_env
except ImportError:
    from detect_project import detect_project
    from vervit_env import load_vervit_env


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = PLUGIN_ROOT / "assets" / "templates"
SUPERPOWERS_REQUIRED_SKILLS = [
    "brainstorming",
    "writing-plans",
    "systematic-debugging",
    "test-driven-development",
    "verification-before-completion",
]
DEFAULT_SKILL_SOURCES = {
    "superpowers": "https://github.com/obra/superpowers.git",
}


def read_template(relative_path: str) -> str:
    path = TEMPLATE_ROOT / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def safe_write(path: Path, content: str, *, force: bool = False) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = content.rstrip() + "\n"
    if force or not path.exists():
        path.write_text(normalized, encoding="utf-8")
        return "written"
    current = path.read_text(encoding="utf-8", errors="ignore")
    if current == normalized:
        return "unchanged"
    suggested = path.with_name(f"{path.stem}.vervit-suggested{path.suffix}")
    suggested.write_text(normalized, encoding="utf-8")
    return f"suggested:{suggested}"


def ensure_gitignore_entry(path: Path, entry: str) -> str:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if entry in {line.strip() for line in current.splitlines()}:
        return "unchanged"
    path.write_text(current.rstrip() + f"\n{entry}\n", encoding="utf-8")
    return "written"


def default_skill_search_roots(
    env: Mapping[str, str] | None = None,
    *,
    project_assistant_root: Path | None = None,
) -> list[Path]:
    env = os.environ if env is None else env
    codex_home = Path(env["CODEX_HOME"]) if env.get("CODEX_HOME") else Path.home() / ".codex"
    roots: list[Path] = [
        codex_home / "skills",
        codex_home / "plugins" / "cache",
        PLUGIN_ROOT / "skills",
    ]
    if project_assistant_root is not None:
        roots.insert(0, project_assistant_root / "vervit")
        roots.insert(0, project_assistant_root / "superpowers")
    return roots


def find_skill_paths(
    skill_name: str, *, search_roots: Sequence[Path] | None = None
) -> list[Path]:
    roots = default_skill_search_roots() if search_roots is None else list(search_roots)
    seen: set[Path] = set()
    found: list[Path] = []
    for root in roots:
        try:
            resolved = root.resolve()
        except OSError:
            continue
        if resolved in seen or not resolved.exists():
            continue
        seen.add(resolved)
        candidates = [
            resolved / skill_name / "SKILL.md",
            resolved / "skills" / skill_name / "SKILL.md",
        ]
        candidates.extend(resolved.glob(f"*/skills/{skill_name}/SKILL.md"))
        candidates.extend(resolved.glob(f"*/*/skills/{skill_name}/SKILL.md"))
        candidates.extend(resolved.glob(f"*/*/*/skills/{skill_name}/SKILL.md"))
        candidates.extend(resolved.glob(f"*/references/{skill_name}/SKILL.md"))
        candidates.extend(resolved.glob(f"*/vervit/{skill_name}/SKILL.md"))
        candidates.extend(resolved.glob(f"*/superpowers/{skill_name}/SKILL.md"))
        for candidate in candidates:
            if candidate.exists():
                candidate = candidate.resolve()
                if candidate not in found:
                    found.append(candidate)
    return found


def detect_superpowers(
    *, search_roots: Sequence[Path] | None = None
) -> dict[str, Any]:
    skills = {
        name: [str(path) for path in find_skill_paths(name, search_roots=search_roots)]
        for name in SUPERPOWERS_REQUIRED_SKILLS
    }
    missing = [name for name, paths in skills.items() if not paths]
    return {
        "status": "ready" if not missing else "incomplete",
        "requiredSkills": list(SUPERPOWERS_REQUIRED_SKILLS),
        "missingSkills": missing,
        "skills": skills,
    }


def detect_tlc_spec_driven(
    *, search_roots: Sequence[Path] | None = None
) -> dict[str, Any]:
    paths = find_skill_paths("tlc-spec-driven", search_roots=search_roots)
    if paths:
        return {
            "status": "available",
            "mode": "optional",
            "skill": "tlc-spec-driven",
            "paths": [str(path) for path in paths],
            "usage": "Sob demanda para docs estruturado, mapeamento brownfield, requisitos rastreaveis, quick tasks e retomada de trabalho.",
        }
    return {
        "status": "pending",
        "mode": "optional",
        "skill": "tlc-spec-driven",
        "reason": "Skill TLC nao encontrada no ambiente local durante o onboarding.",
    }


def detect_jira_rest(env: Mapping[str, str] | None = None) -> dict[str, Any]:
    env = os.environ if env is None else env
    variables = ["JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"]
    missing = [name for name in variables if not env.get(name)]
    if missing:
        return {
            "status": "pending",
            "missingEnvironmentVariables": missing,
            "secretsRecorded": False,
        }
    return {
        "status": "configured",
        "environmentVariablesPresent": variables,
        "secretsRecorded": False,
    }


def detect_atlassian(env: Mapping[str, str] | None = None) -> dict[str, Any]:
    env = os.environ if env is None else env
    rest_variables = {"JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"}
    markers = sorted(
        name
        for name, value in env.items()
        if value
        and name not in rest_variables
        and (
            name.startswith("ATLASSIAN_")
            or name.startswith("ROVO_")
            or name.startswith("MCP_ATLASSIAN")
        )
    )
    connector = {
        "status": "exposed" if markers else "not_exposed",
        "environmentMarkers": markers,
        "authenticated": "unknown",
    }
    rest = detect_jira_rest(env)
    return {
        "status": "available"
        if connector["status"] == "exposed" or rest["status"] == "configured"
        else "pending",
        "connector": connector,
        "rest": rest,
    }


def run_git(args: Sequence[str], *, cwd: Path | None = None) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def comparable_source(source: str) -> str:
    candidate = Path(source)
    if candidate.exists():
        return str(candidate.resolve()).lower()
    return source.rstrip("/").removesuffix(".git").lower()


def sanitize_source(source: str) -> str:
    parsed = urlsplit(source)
    if not parsed.scheme or not parsed.hostname:
        return source
    host = parsed.hostname
    if parsed.port:
        host = f"{host}:{parsed.port}"
    return urlunsplit((parsed.scheme, host, parsed.path, parsed.query, parsed.fragment))


def publish_skills(
    checkout: Path, *, codex_home: Path | None = None,
    destination_root: Path | None = None,
    source_name: str, source: str
) -> tuple[list[str], list[str]]:
    skills_root = checkout / "skills"
    if not skills_root.exists():
        skills_root = checkout
    installed: list[str] = []
    blocked: list[str] = []
    if destination_root is None:
        destination_root = Path(codex_home) / "skills"  # type: ignore[arg-type]
    destination_root.mkdir(parents=True, exist_ok=True)
    for skill_path in sorted(skills_root.iterdir()):
        if not skill_path.is_dir() or not (skill_path / "SKILL.md").exists():
            continue
        destination = destination_root / skill_path.name
        marker = destination / ".vervit-skill-source.json"
        if destination.exists() and not marker.exists():
            blocked.append(skill_path.name)
            continue
        if destination.exists():
            try:
                managed_by = json.loads(marker.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                blocked.append(skill_path.name)
                continue
            if managed_by.get("sourceName") != source_name:
                blocked.append(skill_path.name)
                continue
            shutil.rmtree(destination)
        shutil.copytree(skill_path, destination)
        marker.write_text(
            json.dumps(
                {
                    "sourceName": source_name,
                    "source": sanitize_source(source),
                    "checkout": str(checkout),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        installed.append(skill_path.name)
    return installed, blocked


def sync_skill_sources(
    sources: Mapping[str, str], *, codex_home: Path | None = None
) -> dict[str, dict[str, Any]]:
    codex_home = (
        Path(os.environ["CODEX_HOME"])
        if codex_home is None and os.environ.get("CODEX_HOME")
        else codex_home or Path.home() / ".codex"
    )
    destination_root = Path(codex_home) / "skills" / "sources"
    destination_root.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict[str, Any]] = {}
    for name, source in sources.items():
        destination = destination_root / name
        result: dict[str, Any] = {
            "source": sanitize_source(source),
            "path": str(destination),
        }
        try:
            if not destination.exists():
                run_git(["clone", source, str(destination)])
                result.update(status="ok", action="cloned")
            elif not (destination / ".git").exists():
                result.update(status="blocked", action="none", reason="not_git_checkout")
                results[name] = result
                continue
            elif run_git(["status", "--porcelain"], cwd=destination):
                result.update(status="blocked", action="none", reason="dirty_checkout")
                results[name] = result
                continue
            else:
                origin = run_git(["remote", "get-url", "origin"], cwd=destination)
                result["origin"] = origin
                if comparable_source(origin) != comparable_source(source):
                    result.update(status="blocked", action="none", reason="origin_mismatch")
                    results[name] = result
                    continue
                before = run_git(["rev-parse", "HEAD"], cwd=destination)
                run_git(["pull", "--ff-only"], cwd=destination)
                after = run_git(["rev-parse", "HEAD"], cwd=destination)
                result.update(
                    status="ok",
                    action="updated" if before != after else "unchanged",
                )
            result["commit"] = run_git(["rev-parse", "HEAD"], cwd=destination)
            installed, blocked = publish_skills(
                destination,
                codex_home=Path(codex_home),
                source_name=name,
                source=source,
            )
            result["installedSkills"] = installed
            result["blockedSkills"] = blocked
        except (OSError, subprocess.CalledProcessError) as exc:
            result.update(
                status="failed",
                action="none",
                error=str(exc).replace(source, sanitize_source(source)),
            )
        results[name] = result
    return results


def detect_dependencies(
    *,
    env: Mapping[str, str] | None = None,
    skill_search_roots: Sequence[Path] | None = None,
    source_sync: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    sources_extracted: dict[str, Any] = {}
    if source_sync:
        if "sources" in source_sync:
            sources_extracted = dict(source_sync["sources"])
        else:
            sources_extracted = dict(source_sync)
    return {
        "superpowers": detect_superpowers(search_roots=skill_search_roots),
        "tlc": detect_tlc_spec_driven(search_roots=skill_search_roots),
        "atlassian": detect_atlassian(env),
        "skillSources": sources_extracted,
    }


def render_stack(detected: dict[str, Any]) -> str:
    scripts = detected.get("scripts", {})
    deps = detected.get("dependencies_detected", [])
    markers = detected.get("markers", {})
    lines = [
        "# Stack",
        "",
        "## Detectado",
        "",
        f"- Raiz: `{detected.get('root')}`",
        f"- Package manager: `{detected.get('package_manager') or 'nao detectado'}`",
        f"- Package name: `{detected.get('package_name') or 'nao detectado'}`",
        f"- Dependencias/frameworks destacados: {', '.join(deps) if deps else 'nao detectado'}",
        "",
        "## Marcadores",
        "",
    ]
    for key, value in sorted(markers.items()):
        lines.append(f"- {key}: {'sim' if value else 'nao'}")
    lines.extend(["", "## Scripts", ""])
    if scripts:
        for name, command in sorted(scripts.items()):
            lines.append(f"- `{name}`: `{command}`")
    else:
        lines.append("- Nenhum script detectado.")
    lines.extend(["", "## Revisao Humana", "", "Confirme as inferencias antes de usar este arquivo como fonte de verdade."])
    return "\n".join(lines)


def render_structure(detected: dict[str, Any]) -> str:
    dirs = detected.get("top_level_directories", [])
    lines = ["# Estrutura", "", "## Diretorios Principais", ""]
    if dirs:
        for name in dirs:
            lines.append(f"- `{name}/`: revisar responsabilidade durante o mapeamento detalhado.")
    else:
        lines.append("- Nenhum diretorio principal detectado.")
    lines.extend(["", "## Observacao", "", "Este arquivo foi criado por varredura inicial. Refine com evidencias ao trabalhar no projeto."])
    return "\n".join(lines)


def render_testing(detected: dict[str, Any]) -> str:
    scripts = detected.get("scripts", {})
    preferred = ["lint", "format:check", "test", "test:coverage", "build", "test:e2e", "test:bdd"]
    lines = ["# Testes", "", "## Comandos Detectados", ""]
    found = False
    for name in preferred:
        if name in scripts:
            found = True
            lines.append(f"- `{name}`: `{scripts[name]}`")
    if not found:
        lines.append("- Nenhum comando padrao de verificacao foi detectado.")
    lines.extend(
        [
            "",
            "## Politica",
            "",
            "- Feature grande: teste proporcional por camada e verificacao final.",
            "- Melhoria pequena: menor comando confiavel para o escopo.",
            "- Bug fix: teste de regressao quando viavel e verificacao do sintoma original.",
            "- Toda mudanca comportamental: TDD com teste falhando antes da implementacao.",
            "- Antes de integrar tarefa Jira: checklist manual completo e testes automatizados aprovados.",
            "- Antes de publicar release: regressao geral focada nas tarefas e impactos acumulados.",
        ]
    )
    return "\n".join(lines)


def render_architecture(detected: dict[str, Any]) -> str:
    markers = detected.get("markers", {})
    lines = ["# Arquitetura", "", "## Visao Inicial", ""]
    if markers.get("package_json"):
        lines.append("- Projeto com manifesto Node/JavaScript detectado em `package.json`.")
    if markers.get("vite"):
        lines.append("- Vite detectado.")
    if markers.get("next"):
        lines.append("- Next.js detectado.")
    if markers.get("supabase"):
        lines.append("- Diretorio `supabase/` detectado.")
    if len(lines) == 4:
        lines.append("- Arquitetura nao inferida automaticamente.")
    lines.extend(["", "## Proximo Mapeamento", "", "Registrar modulos, fronteiras, fluxo de dados, autenticacao e persistencia com referencias a arquivos concretos."])
    return "\n".join(lines)


def render_conventions() -> str:
    return """# Convencoes

## Trabalho Com Codex

- Responder em portugues do Brasil por padrao.
- Ler `vervit-assistant/AGENTS.md` e `vervit-assistant/agent-profile.md` no inicio de cada trabalho.
- Preservar trabalho local do usuario.
- Nao fazer commit, push, deploy ou migracao remota sem pedido explicito.

## Fluxos

- Atividade Jira: iniciar por `vervit-assistant-main`.
- Feature grande: Superpowers completo conforme complexidade.
- Melhoria pequena: Superpowers simplificado e verificacao proporcional.
- Bug fix: systematic-debugging antes de corrigir.
- Hotfix: `main` -> `hotfix/KEY-slug` -> `main` -> tag patch -> sincronizar `release`.
- Release planejada: tarefas em `release`, regressao geral, merge em `main`, tag e sincronizacao.
"""


def render_integrations(detected: dict[str, Any], dependencies: dict[str, Any]) -> str:
    markers = detected.get("markers", {})
    lines = ["# Integracoes", "", "## Detectado", ""]
    if markers.get("supabase"):
        lines.append("- Supabase: diretorio `supabase/` detectado.")
    if markers.get("github_actions"):
        lines.append("- GitHub Actions: `.github/workflows/` detectado.")
    if markers.get("docker"):
        lines.append("- Docker: arquivo Docker ou Compose detectado.")
    if len(lines) == 4:
        lines.append("- Nenhuma integracao foi detectada automaticamente.")
    atlassian = dependencies["atlassian"]
    lines.extend(
        [
            "",
            "## Prontidao Vervit",
            "",
            f"- Superpowers: {dependencies['superpowers']['status']}",
            f"- TLC Spec-Driven: {dependencies['tlc']['status']} (opcional)",
            f"- Atlassian connector: {atlassian['connector']['status']}",
            f"- Jira REST: {atlassian['rest']['status']}",
            "- Segredos: somente variaveis de ambiente; nunca registrar valores.",
        ]
    )
    if dependencies["skillSources"]:
        lines.extend(["", "## Fontes De Skills", ""])
        for name, result in sorted(dependencies["skillSources"].items()):
            lines.append(
                f"- {name}: {result.get('status')} / {result.get('action')} / `{result.get('source')}`"
            )
    return "\n".join(lines)


def render_concerns() -> str:
    return """# Pontos De Atencao

## Riscos Iniciais

- Documentacao gerada por onboarding precisa de revisao humana.
- Jira pode estar pendente ate Atlassian Rovo estar instalado e autenticado.
- Jira REST exige credenciais em variaveis de ambiente e permissoes adequadas.
- Operacoes Jira sensiveis, merges, pushes e tags exigem confirmacao explicita.
- Areas sem testes detectados devem receber verificacao proporcional quando forem alteradas.
"""


def render_onboarding_state(
    detected: dict[str, Any],
    results: dict[str, str],
    dependencies: dict[str, Any],
) -> str:
    jira_ready = dependencies["atlassian"]["rest"]["status"] == "configured"
    pending = [] if jira_ready else ["configureJira"]
    payload = {
        "generatedBy": "vervit-assistant",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "projectRoot": detected.get("root"),
        "dependencies": dependencies,
        "jira": dependencies["atlassian"],
        "tlc": dependencies["tlc"],
        "detected": detected,
        "files": results,
        "firstRun": {
            "required": bool(pending),
            "pending": pending,
            "availableActions": [
                "configureJira",
                "listJiraIssues",
                "mapCodebase",
                "startFeature",
                "startBugOrHotfix",
            ],
        },
        "workflows": {
            "largeFeature": "Superpowers completo com brainstorming, plano formal quando necessario, TDD quando aplicavel e verificacao final",
            "smallImprovement": "Superpowers simplificado + verificacao proporcional",
            "bugFix": "systematic-debugging + causa raiz + regressao quando viavel",
            "main": "vervit-assistant-main coordena Jira, PRD, checklist, implementacao e entrega",
            "hotfix": "main -> hotfix/KEY-slug -> main -> tag patch -> sincronizar release",
            "plannedRelease": "release recebe tarefas; regressao geral; release -> main -> tag -> sincronizar release",
            "tlcOptional": "TLC Spec-Driven sob demanda para docs estruturado, mapeamento brownfield, quick tasks e continuidade de trabalho.",
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _symlink_skills(
    skills_dir: Path, codex_skills_dir: Path
) -> dict[str, str]:
    result: dict[str, str] = {}
    if not skills_dir.exists():
        return result
    codex_skills_dir.mkdir(parents=True, exist_ok=True)
    for entry in skills_dir.iterdir():
        if not entry.is_dir():
            continue
        link = codex_skills_dir / entry.name
        if link.exists() and link.is_symlink():
            link.unlink()
        elif link.exists():
            continue
        try:
            os.symlink(str(entry.resolve()), str(link),
                       target_is_directory=True)
            result[entry.name] = "linked"
        except OSError:
            try:
                import subprocess
                subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(link), str(entry.resolve())],
                    check=True, capture_output=True, text=True,
                )
                result[entry.name] = "linked"
            except (OSError, subprocess.CalledProcessError):
                result[entry.name] = "failed"
    return result


def install_local_skills(
    target: Path,
    sources: Mapping[str, str],
    *,
    codex_home: Path | None = None,
) -> dict[str, Any]:
    assistant_dir = target.resolve() / "vervit-assistant"
    vervit_dir = assistant_dir / "vervit"
    superpowers_dir = assistant_dir / "superpowers"
    vervit_dir.mkdir(parents=True, exist_ok=True)
    superpowers_dir.mkdir(parents=True, exist_ok=True)

    if codex_home is None:
        codex_home = (
            Path(os.environ["CODEX_HOME"])
            if os.environ.get("CODEX_HOME")
            else Path.home() / ".codex"
        )

    results: dict[str, Any] = {
        "assistant_dir": str(assistant_dir),
        "plugin_skills": {},
        "sources": {},
        "symlinks": {},
    }

    for plugin_skill in sorted(PLUGIN_ROOT.joinpath("skills").iterdir()):
        if not plugin_skill.is_dir() or not (plugin_skill / "SKILL.md").exists():
            continue
        dest = vervit_dir / plugin_skill.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(plugin_skill, dest)
        results["plugin_skills"][plugin_skill.name] = "installed"

    for name, source in sources.items():
        source_dir = assistant_dir / "sources" / name
        result: dict[str, Any] = {
            "source": sanitize_source(source),
            "path": str(source_dir),
        }
        try:
            if not source_dir.exists():
                run_git(["clone", source, str(source_dir)])
                result.update(status="ok", action="cloned")
            elif not (source_dir / ".git").exists():
                result["status"] = "blocked"
                result["action"] = "none"
                result["reason"] = "not_git_checkout"
                results["sources"][name] = result
                continue
            elif run_git(["status", "--porcelain"], cwd=source_dir):
                result.update(status="blocked", action="none", reason="dirty_checkout")
                results["sources"][name] = result
                continue
            else:
                origin = run_git(["remote", "get-url", "origin"], cwd=source_dir)
                result["origin"] = origin
                if comparable_source(origin) != comparable_source(source):
                    result.update(status="blocked", action="none", reason="origin_mismatch")
                    results["sources"][name] = result
                    continue
                before = run_git(["rev-parse", "HEAD"], cwd=source_dir)
                run_git(["pull", "--ff-only"], cwd=source_dir)
                after = run_git(["rev-parse", "HEAD"], cwd=source_dir)
                result.update(
                    status="ok",
                    action="updated" if before != after else "unchanged",
                )
            result["commit"] = run_git(["rev-parse", "HEAD"], cwd=source_dir)
            installed, blocked = publish_skills(
                source_dir,
                destination_root=superpowers_dir,
                source_name=name,
                source=source,
            )
            result["installedSkills"] = installed
            result["blockedSkills"] = blocked
        except (OSError, subprocess.CalledProcessError) as exc:
            result.update(
                status="failed",
                action="none",
                error=str(exc).replace(source, sanitize_source(source)),
            )
        results["sources"][name] = result

    codex_skills_dir = codex_home / "skills"
    symlinks: dict[str, str] = {}
    for skills_root in (vervit_dir, superpowers_dir):
        symlinks.update(_symlink_skills(skills_root, codex_skills_dir))
    results["symlinks"] = symlinks

    return results


def initialize_project(
    target: Path,
    *,
    force: bool = False,
    install_skills: bool = False,
    skill_sources: Mapping[str, str] | None = None,
    codex_home: Path | None = None,
    env: Mapping[str, str] | None = None,
    skill_search_roots: Sequence[Path] | None = None,
) -> dict[str, str]:
    target = target.resolve()
    detected = detect_project(target)
    effective_env = load_vervit_env(target, env)
    sources = {**DEFAULT_SKILL_SOURCES, **dict(skill_sources or {})}

    assistant_root = target / "vervit-assistant"
    source_sync: dict[str, Any] = {}
    if install_skills:
        source_sync = install_local_skills(target, sources, codex_home=codex_home)
        source_sync["installation"] = "local"

    effective_roots = list(skill_search_roots) if skill_search_roots is not None else []
    if codex_home is not None:
        effective_roots.extend([
            codex_home / "skills",
            codex_home / "plugins" / "cache",
        ])
    effective_roots.extend([
        assistant_root / "vervit",
        assistant_root / "superpowers",
        PLUGIN_ROOT / "skills",
    ])
    dependencies = detect_dependencies(
        env=effective_env,
        skill_search_roots=effective_roots,
        source_sync=source_sync,
    )
    files: dict[str, str] = {}
    files[".gitignore"] = ensure_gitignore_entry(
        target / ".gitignore", ".env.vervit.local"
    )
    files[".gitignore:env-example"] = ensure_gitignore_entry(
        target / ".gitignore", "!.env.vervit.example"
    )

    static_templates = {
        "vervit-assistant/AGENTS.md": "AGENTS.md",
        "vervit-assistant/config.json": "config.json",
        "vervit-assistant/agent-profile.md": "agent-profile.md",
        "docs/README.md": "docs/README.md",
        ".env.vervit.example": ".env.vervit.example",
    }
    for destination, template in static_templates.items():
        files[destination] = safe_write(target / destination, read_template(template), force=force)

    generated = {
        "docs/_codebase/STACK.md": render_stack(detected),
        "docs/_codebase/ARCHITECTURE.md": render_architecture(detected),
        "docs/_codebase/CONVENTIONS.md": render_conventions(),
        "docs/_codebase/STRUCTURE.md": render_structure(detected),
        "docs/_codebase/TESTING.md": render_testing(detected),
        "docs/_codebase/INTEGRATIONS.md": render_integrations(detected, dependencies),
        "docs/_codebase/CONCERNS.md": render_concerns(),
    }
    for destination, content in generated.items():
        files[destination] = safe_write(target / destination, content, force=force)

    files["vervit-assistant/state.json"] = safe_write(
        target / "vervit-assistant" / "state.json",
        render_onboarding_state(detected, files, dependencies),
        force=True,
    )
    return files


def parse_skill_source(value: str) -> tuple[str, str]:
    name, separator, source = value.partition("=")
    if not separator or not name.strip() or not source.strip():
        raise argparse.ArgumentTypeError("skill source must use NAME=URL")
    return name.strip(), source.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a project with Vervit Assistant standards.")
    parser.add_argument("--target", default=".", help="Project root to initialize.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files instead of creating suggested files.")
    parser.add_argument(
        "--install-skills",
        action="store_true",
        help="Clone or fast-forward configured skill sources under CODEX_HOME.",
    )
    parser.add_argument(
        "--skill-source",
        action="append",
        default=[],
        type=parse_skill_source,
        metavar="NAME=URL",
        help="Add or override a Git source used by --install-skills.",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()
    results = initialize_project(
        target,
        force=args.force,
        install_skills=args.install_skills,
        skill_sources=dict(args.skill_source),
    )
    print(json.dumps({"target": str(target), "files": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
