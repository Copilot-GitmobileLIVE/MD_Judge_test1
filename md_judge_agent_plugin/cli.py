from __future__ import annotations

import argparse
from pathlib import Path

from .installer import AGENT_NAME, export_agent, install_agent, load_agent_text
from .scoring import evaluate_workspace, initialize_scoring_bundle


def _absolute_path(path: Path) -> Path:
    return path.resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package, export, install, and scaffold scoring for the MD_Judge custom agent."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("show", help="Print the packaged agent definition.")

    export_parser = subparsers.add_parser("export", help="Write the packaged agent file to a path.")
    export_parser.add_argument("--output", required=True, help="Output path for the exported agent file.")
    export_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output file if it already exists.",
    )

    install_parser = subparsers.add_parser(
        "install",
        help="Install the agent into a target workspace under .github/agents/.",
    )
    install_parser.add_argument(
        "--target-dir",
        required=True,
        help="Workspace root where the agent should be installed.",
    )
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing installed agent file.",
    )

    init_score_parser = subparsers.add_parser(
        "init-score",
        help="Create a timestamped scoring folder for an evaluated agent.",
    )
    init_score_parser.add_argument(
        "--evaluated-agent-name",
        required=True,
        help="Name of the agent or workspace being evaluated, for example MD_Main_Agent or MD_Test.",
    )
    init_score_parser.add_argument(
        "--output-root",
        default=".",
        help="Directory under which the scoring folder should be created.",
    )
    init_score_parser.add_argument(
        "--task-summary",
        default="",
        help="Optional one-line description of the task being evaluated.",
    )
    init_score_parser.add_argument(
        "--force",
        action="store_true",
        help="Allow reuse of an existing scoring folder path when it already exists.",
    )

    evaluate_parser = subparsers.add_parser(
        "evaluate",
        help="Run workspace checks, execute tests, and write completed scoring files.",
    )
    evaluate_parser.add_argument(
        "--target-workspace",
        required=True,
        help="Workspace root to evaluate, for example C:\\path\\to\\MD_Main_Agent.",
    )
    evaluate_parser.add_argument(
        "--evaluated-agent-name",
        required=True,
        help="Name of the agent or workspace being evaluated, for example MD_Main_Agent.",
    )
    evaluate_parser.add_argument(
        "--output-root",
        default=".",
        help="Directory under which the scoring folder should be created.",
    )
    evaluate_parser.add_argument(
        "--task-summary",
        default="",
        help="Optional one-line description of the evaluation scope.",
    )
    evaluate_parser.add_argument(
        "--force",
        action="store_true",
        help="Allow reuse of an existing scoring folder path when it already exists.",
    )

    test_and_evaluate_parser = subparsers.add_parser(
        "test-and-evaluate",
        help="Run target workspace tests and write completed scoring files in one command.",
    )
    test_and_evaluate_parser.add_argument(
        "--target-workspace",
        required=True,
        help="Workspace root to evaluate, for example C:\\path\\to\\MD_Main_Agent.",
    )
    test_and_evaluate_parser.add_argument(
        "--evaluated-agent-name",
        required=True,
        help="Name of the agent or workspace being evaluated, for example MD_Main_Agent.",
    )
    test_and_evaluate_parser.add_argument(
        "--output-root",
        default=".",
        help="Directory under which the scoring folder should be created.",
    )
    test_and_evaluate_parser.add_argument(
        "--task-summary",
        default="",
        help="Optional one-line description of the evaluation scope.",
    )
    test_and_evaluate_parser.add_argument(
        "--force",
        action="store_true",
        help="Allow reuse of an existing scoring folder path when it already exists.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "show":
        print(load_agent_text())
        return

    if args.command == "export":
        output_path = export_agent(Path(args.output), force=args.force)
        print(f"Exported {AGENT_NAME} to {_absolute_path(output_path)}")
        return

    if args.command == "install":
        installed_path = install_agent(Path(args.target_dir), force=args.force)
        print(f"Installed {AGENT_NAME} to {_absolute_path(installed_path)}")
        return

    if args.command == "init-score":
        written_paths = initialize_scoring_bundle(
            output_root=Path(args.output_root),
            evaluated_agent_name=args.evaluated_agent_name,
            task_summary=args.task_summary,
            force=args.force,
        )
        print(f"Initialized scoring folder for {args.evaluated_agent_name}")
        print(f"Output directory: {_absolute_path(written_paths['output_dir'])}")
        print(f"Manifest: {_absolute_path(written_paths['manifest'])}")
        print(f"Summary: {_absolute_path(written_paths['summary'])}")
        print(f"Notes: {_absolute_path(written_paths['notes'])}")
        return

    if args.command in {"evaluate", "test-and-evaluate"}:
        evaluation = evaluate_workspace(
            target_workspace=Path(args.target_workspace),
            evaluated_agent_name=args.evaluated_agent_name,
            output_root=Path(args.output_root),
            task_summary=args.task_summary,
            force=args.force,
        )
        print(f"Evaluated {args.evaluated_agent_name}")
        print(f"Output directory: {_absolute_path(evaluation['output_dir'])}")
        print(f"Score: {evaluation['summary_payload']['score']}")
        print(f"Passed: {evaluation['summary_payload']['passed']}")
        print(f"Manifest: {_absolute_path(evaluation['manifest'])}")
        print(f"Summary: {_absolute_path(evaluation['summary'])}")
        print(f"Notes: {_absolute_path(evaluation['notes'])}")
        return

    parser.error(f"Unsupported command: {args.command}")
