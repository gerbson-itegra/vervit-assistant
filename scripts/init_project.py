from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .detect_project import detect_project
except ImportError:
    from detect_project import detect_project


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = PLUGIN_ROOT / "assets" / "templates"


def read_template(relative_path: str) -> str:
    return (TEMPLATE_ROOT / relative_path).read_text(encoding="utf-8")


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


def detect_tlc_spec_driven() -> dict[str, Any]:
    search_roots = [
        Path(os.environ["CODEX_HOME"]) / "skills" if os.environ.get("CODEX_HOME") else None,
        Path.home() / ".codex" / "skills",
        PLUGIN_ROOT / "skills",
    ]
    seen: set[Path] = set()
    for root in search_roots:
        if root is None:
            continue
        try:
            resolved = root.resolve()
        except OSError:
            continue
        if resolved in seen or not resolved.exists():
            continue
        seen.add(resolved)
        direct = resolved / "tlc-spec-driven" / "SKILL.md"
        if direct.exists():
            return {
                "status": "available",
                "mode": "optional",
                "skill": "tlc-spec-driven",
                "path": str(direct),
                "usage": "Sob demanda para .specs estruturado, mapeamento brownfield, requisitos rastreaveis, quick tasks e retomada de trabalho.",
            }
        for candidate in resolved.glob("*/references/tlc-spec-driven/SKILL.md"):
            if candidate.exists():
                return {
                    "status": "available",
                    "mode": "optional",
                    "skill": "tlc-spec-driven",
                    "path": str(candidate),
                    "usage": "Sob demanda para .specs estruturado, mapeamento brownfield, requisitos rastreaveis, quick tasks e retomada de trabalho.",
                }
    return {
        "status": "pending",
        "mode": "optional",
        "skill": "tlc-spec-driven",
        "reason": "Skill TLC nao encontrada no ambiente local durante o onboarding.",
    }


def detect_jira_rest() -> dict[str, Any]:
    variables = ["JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"]
    missing = [name for name in variables if not os.environ.get(name)]
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
- Ler `AGENTS.md` e `.agents/main-agent.md` no inicio de cada trabalho.
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


def render_integrations(detected: dict[str, Any], jira_status: str) -> str:
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
    jira_rest = detect_jira_rest()
    lines.extend(
        [
            "",
            "## Jira",
            "",
            f"- Atlassian/Rovo: {jira_status}",
            f"- Executor REST: {jira_rest['status']}",
            "- Segredos: somente variaveis de ambiente; nunca registrar valores.",
        ]
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


def render_onboarding_state(detected: dict[str, Any], results: dict[str, str]) -> str:
    payload = {
        "generatedBy": "vervit-assistant",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "projectRoot": detected.get("root"),
        "jira": {
            "status": "pending",
            "reason": "Atlassian Rovo deve ser verificado pelo agente durante o onboarding.",
            "restExecutor": detect_jira_rest(),
        },
        "tlc": detect_tlc_spec_driven(),
        "detected": detected,
        "files": results,
        "workflows": {
            "largeFeature": "Superpowers completo com brainstorming, plano formal quando necessario, TDD quando aplicavel e verificacao final",
            "smallImprovement": "Superpowers simplificado + verificacao proporcional",
            "bugFix": "systematic-debugging + causa raiz + regressao quando viavel",
            "main": "vervit-assistant-main coordena Jira, PRD, checklist, implementacao e entrega",
            "hotfix": "main -> hotfix/KEY-slug -> main -> tag patch -> sincronizar release",
            "plannedRelease": "release recebe tarefas; regressao geral; release -> main -> tag -> sincronizar release",
            "tlcOptional": "TLC Spec-Driven sob demanda para Specify/Design/Tasks/Execute, mapeamento brownfield, quick tasks e continuidade de trabalho.",
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def initialize_project(target: Path, *, force: bool = False) -> dict[str, str]:
    target = target.resolve()
    detected = detect_project(target)
    jira_status = "pendente; continuar onboarding sem bloquear"
    files: dict[str, str] = {}

    static_templates = {
        "AGENTS.md": "AGENTS.md",
        ".agents/main-agent.md": ".agents/main-agent.md",
        ".agents/vervit-assistant.json": ".agents/vervit-assistant.json",
        ".specs/project/PROJECT.md": ".specs/project/PROJECT.md",
        ".specs/project/ROADMAP.md": ".specs/project/ROADMAP.md",
        ".specs/project/STATE.md": ".specs/project/STATE.md",
        ".specs/releases/NEXT/RELEASE.md": ".specs/releases/NEXT/RELEASE.md",
        ".specs/releases/NEXT/TRACE.md": ".specs/releases/NEXT/TRACE.md",
        ".specs/releases/NEXT/state.json": ".specs/releases/NEXT/state.json",
        ".specs/jira/README.md": ".specs/jira/README.md",
        ".specs/releases/README.md": ".specs/releases/README.md",
    }
    for destination, template in static_templates.items():
        files[destination] = safe_write(target / destination, read_template(template), force=force)

    generated = {
        ".specs/codebase/STACK.md": render_stack(detected),
        ".specs/codebase/ARCHITECTURE.md": render_architecture(detected),
        ".specs/codebase/CONVENTIONS.md": render_conventions(),
        ".specs/codebase/STRUCTURE.md": render_structure(detected),
        ".specs/codebase/TESTING.md": render_testing(detected),
        ".specs/codebase/INTEGRATIONS.md": render_integrations(detected, jira_status),
        ".specs/codebase/CONCERNS.md": render_concerns(),
    }
    for destination, content in generated.items():
        files[destination] = safe_write(target / destination, content, force=force)

    files[".agents/vervit-onboarding.json"] = safe_write(
        target / ".agents" / "vervit-onboarding.json",
        render_onboarding_state(detected, files),
        force=True,
    )
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a project with Vervit Assistant standards.")
    parser.add_argument("--target", default=".", help="Project root to initialize.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files instead of creating suggested files.")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    results = initialize_project(target, force=args.force)
    print(json.dumps({"target": str(target), "files": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
