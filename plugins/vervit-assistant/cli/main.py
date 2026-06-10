from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="vervit", description="Vervit Assistant CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    init_p = sub.add_parser("init", help="Inicializar projeto com padrao Vervit")
    init_p.add_argument("--target", default=".", help="Raiz do projeto")
    init_p.add_argument("--force", action="store_true", help="Sobrescrever arquivos existentes")
    init_p.add_argument("--no-install-skills", action="store_true", help="Pular instalacao de skills")

    jira_p = sub.add_parser("jira", help="Operacoes Jira")
    jira_sub = jira_p.add_subparsers(dest="jira_command", required=True)

    jira_list = jira_sub.add_parser("list", help="Listar issues ou projetos")
    jira_list.add_argument("--project", help="Project key (ex: PROJ)")
    jira_list.add_argument("--board", type=int, help="Board ID")

    jira_get = jira_sub.add_parser("get", help="Obter detalhes de uma issue")
    jira_get.add_argument("issue_key", help="KEY-123")

    jira_create = jira_sub.add_parser("create", help="Criar issue")
    jira_create.add_argument("--project", required=True)
    jira_create.add_argument("--summary", required=True)
    jira_create.add_argument("--type", choices=["bug", "feature", "improvement"], default="feature")

    jira_trans = jira_sub.add_parser("transition", help="Transicionar issue")
    jira_trans.add_argument("issue_key")
    jira_trans.add_argument("--to", required=True, help="Nome da transicao (ex: 'In Progress')")

    jira_comment = jira_sub.add_parser("comment", help="Comentar issue")
    jira_comment.add_argument("issue_key")
    jira_comment.add_argument("--text", required=True)

    update_p = sub.add_parser("update", help="Migrar estrutura + baixar/atualizar skills e fontes")
    update_p.add_argument("--target", default=".", help="Raiz do projeto")
    update_p.add_argument("--dry-run", action="store_true", help="So mostrar o que seria feito")
    update_p.add_argument("--no-skills", action="store_true", help="Pular instalacao/atualizacao de skills")

    task_p = sub.add_parser("task", help="Gerenciar artefatos de tarefa")
    task_sub = task_p.add_subparsers(dest="task_command", required=True)

    task_start = task_sub.add_parser("start", help="Criar artefatos de uma nova tarefa")
    task_start.add_argument("issue_key")
    task_start.add_argument("--summary", required=True)
    task_start.add_argument("--type", choices=["bug", "feature", "improvement"], required=True)
    task_start.add_argument("--track", choices=["hotfix", "planned"], default="planned")
    task_start.add_argument("--target", default=".")

    task_status = task_sub.add_parser("status", help="Verificar gates de uma tarefa")
    task_status.add_argument("issue_key")
    task_status.add_argument("--target", default=".")

    args = parser.parse_args(argv)

    if args.command == "init":
        from .init_cmd import init_project as _init
        _init(target=Path(args.target), force=args.force, install_skills=not args.no_install_skills)
        return 0

    if args.command == "jira":
        from . import jira_cmd
        if args.jira_command == "list":
            jira_cmd.list_issues(project=args.project, board=args.board)
        elif args.jira_command == "get":
            jira_cmd.get_issue(args.issue_key)
        elif args.jira_command == "create":
            jira_cmd.create_issue(project=args.project, summary=args.summary, issue_type=args.type)
        elif args.jira_command == "transition":
            jira_cmd.transition_issue(args.issue_key, to=args.to)
        elif args.jira_command == "comment":
            jira_cmd.comment_issue(args.issue_key, text=args.text)
        return 0

    if args.command == "update":
        import json
        from scripts.migrate_project import migrate_project
        from scripts.init_project import install_local_skills, DEFAULT_SKILL_SOURCES

        target = Path(args.target).resolve()
        result: dict[str, object] = {"target": str(target)}

        if args.dry_run:
            migration = migrate_project(target, dry_run=True)
            result["migration"] = migration
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        migration = migrate_project(target, dry_run=False)
        result["migration"] = migration

        if not args.no_skills:
            result["skills"] = install_local_skills(target, DEFAULT_SKILL_SOURCES)

        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "task":
        from . import task_cmd
        if args.task_command == "start":
            task_cmd.start(args.issue_key, summary=args.summary, task_type=args.type, track=args.track, target=Path(args.target))
        elif args.task_command == "status":
            task_cmd.status(args.issue_key, target=Path(args.target))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
