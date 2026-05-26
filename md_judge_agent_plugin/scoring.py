from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9_-]+")
SCORING_RESULTS_DIRNAME = "Scoring_Results"
DEFAULT_RUBRIC = {
    "task_fit": 2,
    "correctness_and_completeness": 4,
    "reasoning_and_evidence": 2,
    "markdown_or_packaging_quality": 1,
    "safety_and_limitations_handling": 1,
}
PASS_THRESHOLD = 7


def sanitize_agent_name(agent_name: str) -> str:
    cleaned = SAFE_NAME_RE.sub("_", agent_name.strip().lower()).strip("_")
    return cleaned or "evaluated_agent"


def format_timestamp(timestamp: datetime | None = None) -> str:
    value = timestamp or datetime.now(timezone.utc)
    return value.strftime("%Y%m%d_%H%M%S")


def build_output_dir(
    *,
    output_root: Path,
    evaluated_agent_name: str,
    timestamp: datetime | None = None,
) -> Path:
    scoring_root = output_root / SCORING_RESULTS_DIRNAME
    return scoring_root / f"{sanitize_agent_name(evaluated_agent_name)}_{format_timestamp(timestamp)}_scoring"


def initialize_scoring_bundle(
    *,
    output_root: Path,
    evaluated_agent_name: str,
    task_summary: str = "",
    timestamp: datetime | None = None,
    force: bool = False,
) -> dict[str, Path]:
    timestamp_value = timestamp or datetime.now(timezone.utc)
    output_dir = build_output_dir(
        output_root=output_root,
        evaluated_agent_name=evaluated_agent_name,
        timestamp=timestamp_value,
    )

    if output_dir.exists() and any(output_dir.iterdir()) and not force:
        raise FileExistsError(
            f"Refusing to overwrite existing scoring folder: {output_dir}. Use --force to reuse it."
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "manifest.json"
    summary_path = output_dir / "scoring_summary.json"
    notes_path = output_dir / "scoring_notes.md"

    manifest_payload = {
        "evaluated_agent_name": evaluated_agent_name,
        "scoring_folder": str(output_dir),
        "created_at": timestamp_value.isoformat(),
        "task_summary": task_summary,
        "expected_files": [
            "manifest.json",
            "scoring_summary.json",
            "scoring_notes.md",
        ],
    }
    summary_payload = {
        "evaluated_agent_name": evaluated_agent_name,
        "evaluated_at": timestamp_value.isoformat(),
        "score": None,
        "passed": None,
        "rubric_maximums": DEFAULT_RUBRIC,
        "rationale": "",
    }
    notes_template = "\n".join(
        [
            f"# {evaluated_agent_name} evaluation notes",
            "",
            f"- Evaluated agent: {evaluated_agent_name}",
            f"- Created at: {timestamp_value.isoformat()}",
            f"- Task summary: {task_summary or '(not provided)'}",
            "",
            "## Strengths",
            "",
            "- ",
            "",
            "## Weaknesses",
            "",
            "- ",
            "",
            "## Evidence reviewed",
            "",
            "- ",
            "",
            "## Recommendations",
            "",
            "- ",
        ]
    )

    manifest_path.write_text(json.dumps(manifest_payload, indent=2), encoding="utf-8")
    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    notes_path.write_text(notes_template, encoding="utf-8")

    return {
        "output_dir": output_dir,
        "manifest": manifest_path,
        "summary": summary_path,
        "notes": notes_path,
    }


def resolve_agent_alias(evaluated_agent_name: str) -> str:
    normalized = sanitize_agent_name(evaluated_agent_name)
    if normalized in {"md_main_agent", "md_test_agent", "md_test"}:
        return "MD_Test"
    return evaluated_agent_name


def _read_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _resolve_workspace_python(target_workspace: Path) -> Path:
    windows_python = target_workspace / ".venv" / "Scripts" / "python.exe"
    if windows_python.exists():
        return windows_python

    posix_python = target_workspace / ".venv" / "bin" / "python"
    if posix_python.exists():
        return posix_python

    return Path(sys.executable)


def _run_workspace_tests(target_workspace: Path) -> dict[str, object]:
    python_executable = _resolve_workspace_python(target_workspace)
    command = [str(python_executable), "-m", "unittest", "discover", "-s", "tests", "-v"]
    completed = subprocess.run(
        command,
        cwd=target_workspace,
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part).strip()
    return {
        "python_executable": str(python_executable),
        "command": " ".join(command),
        "returncode": completed.returncode,
        "success": completed.returncode == 0,
        "output": output,
    }


def evaluate_workspace(
    *,
    target_workspace: Path,
    evaluated_agent_name: str,
    output_root: Path,
    task_summary: str = "",
    timestamp: datetime | None = None,
    force: bool = False,
) -> dict[str, object]:
    timestamp_value = timestamp or datetime.now(timezone.utc)
    agent_alias = resolve_agent_alias(evaluated_agent_name)
    written_paths = initialize_scoring_bundle(
        output_root=output_root,
        evaluated_agent_name=evaluated_agent_name,
        task_summary=task_summary,
        timestamp=timestamp_value,
        force=force,
    )

    readme_path = target_workspace / "README.md"
    pyproject_path = target_workspace / "pyproject.toml"
    cli_path = target_workspace / "md_test_agent_plugin" / "cli.py"
    installer_path = target_workspace / "md_test_agent_plugin" / "installer.py"
    agent_markdown_path = target_workspace / "md_test_agent_plugin" / "agents" / "MD_Test.agent.md"
    test_path = target_workspace / "tests" / "test_installer.py"

    readme_text = _read_if_exists(readme_path)
    pyproject_text = _read_if_exists(pyproject_path)
    cli_text = _read_if_exists(cli_path)
    installer_text = _read_if_exists(installer_path)
    agent_text = _read_if_exists(agent_markdown_path)
    test_text = _read_if_exists(test_path)

    file_checks = {
        "readme": readme_path.exists(),
        "pyproject": pyproject_path.exists(),
        "cli": cli_path.exists(),
        "installer": installer_path.exists(),
        "agent_markdown": agent_markdown_path.exists(),
        "tests": test_path.exists(),
    }
    test_result = _run_workspace_tests(target_workspace)

    task_fit = 2 if all(file_checks.values()) else 1 if any(file_checks.values()) else 0

    correctness = 0
    if file_checks["pyproject"] and "md-test-agent = \"md_test_agent_plugin.cli:main\"" in pyproject_text:
        correctness += 1
    if file_checks["cli"] and all(command in cli_text for command in ["show", "export", "install"]):
        correctness += 1
    if file_checks["installer"] and ".github" in installer_text and "MD_Test.agent.md" in installer_text:
        correctness += 1
    if test_result["success"]:
        correctness += 1

    evidence_items = []
    for label, path, present in [
        ("README", readme_path, file_checks["readme"]),
        ("pyproject", pyproject_path, file_checks["pyproject"]),
        ("CLI", cli_path, file_checks["cli"]),
        ("installer", installer_path, file_checks["installer"]),
        ("agent markdown", agent_markdown_path, file_checks["agent_markdown"]),
        ("tests", test_path, file_checks["tests"]),
    ]:
        if present:
            evidence_items.append(f"{label}: {path}")

    evidence_items.append(f"Test command: {test_result['command']}")
    if test_result["output"]:
        evidence_items.append("Test output captured from unittest discovery")

    reasoning = 2 if len(evidence_items) >= 5 and test_result["success"] else 1 if len(evidence_items) >= 3 else 0
    markdown_quality = 1 if file_checks["readme"] and file_checks["agent_markdown"] and agent_text.startswith("---") else 0
    safety = 1

    rubric_scores = {
        "task_fit": task_fit,
        "correctness_and_completeness": correctness,
        "reasoning_and_evidence": reasoning,
        "markdown_or_packaging_quality": markdown_quality,
        "safety_and_limitations_handling": safety,
    }
    total_score = sum(rubric_scores.values())
    passed = total_score >= PASS_THRESHOLD

    strengths = []
    weaknesses = []
    recommendations = []

    if correctness >= 3:
        strengths.append("The workspace preserves a coherent packaging surface across pyproject metadata, CLI, installer, and bundled agent markdown.")
    if test_result["success"]:
        strengths.append("The workspace test suite passed through unittest discovery, which provides executable evidence for the packaged behavior.")
    if file_checks["readme"] and "md-test-agent" in readme_text:
        strengths.append("The README documents the main console commands for end users.")

    if not test_result["success"]:
        weaknesses.append("The workspace test suite did not complete successfully, which reduces confidence in the packaged behavior.")
    if "md-test-agent = \"md_test_agent_plugin.cli:main\"" not in pyproject_text:
        weaknesses.append("The expected md-test-agent console script entry point was not found in pyproject.toml.")
    if "--force" not in test_text:
        weaknesses.append("Installer overwrite behavior is not covered in tests.")
    if "build" not in test_text.lower():
        weaknesses.append("There is no packaging artifact test covering built wheels or sdists.")

    recommendations.append("Add a CLI smoke test that verifies md-test-agent show returns frontmatter with name: MD_Test.")
    recommendations.append("Add a packaging test that builds a wheel and verifies MD_Test.agent.md is present in the built artifact.")
    recommendations.append("Add an installer overwrite-behavior test for the force flag and existing-file failure path.")

    manifest_payload = {
        "evaluated_agent_name": evaluated_agent_name,
        "evaluated_agent_alias": agent_alias,
        "scoring_folder": written_paths["output_dir"].name,
        "created_at": timestamp_value.isoformat(),
        "task_summary": task_summary,
        "reviewed_evidence": evidence_items,
        "expected_files": [
            "manifest.json",
            "scoring_summary.json",
            "scoring_notes.md",
        ],
    }
    summary_payload = {
        "evaluated_agent_name": evaluated_agent_name,
        "evaluated_agent_alias": agent_alias,
        "evaluated_at": timestamp_value.isoformat(),
        "score": total_score,
        "passed": passed,
        "pass_threshold": PASS_THRESHOLD,
        "rubric_maximums": DEFAULT_RUBRIC,
        "rubric_scores": rubric_scores,
        "rationale": (
            f"{evaluated_agent_name} scored {total_score}/{sum(DEFAULT_RUBRIC.values())}. "
            "The score is based on repository packaging checks plus a unittest discovery run in the target workspace."
        ),
    }
    notes_text = "\n".join(
        [
            f"# {evaluated_agent_name} evaluation notes",
            "",
            f"- Evaluated agent: {evaluated_agent_name}",
            f"- Source agent alias: {agent_alias}",
            f"- Created at: {timestamp_value.isoformat()}",
            f"- Task summary: {task_summary or '(not provided)'}",
            f"- Total score: {total_score}/{sum(DEFAULT_RUBRIC.values())}",
            f"- Result: {'Pass' if passed else 'Fail'}",
            "",
            "## Strengths",
            "",
            *(f"- {item}" for item in strengths),
            "",
            "## Weaknesses",
            "",
            *(f"- {item}" for item in weaknesses),
            "",
            "## Evidence reviewed",
            "",
            *(f"- {item}" for item in evidence_items),
            "",
            "## Recommendations",
            "",
            *(f"- {item}" for item in recommendations),
        ]
    )

    written_paths["manifest"].write_text(json.dumps(manifest_payload, indent=2), encoding="utf-8")
    written_paths["summary"].write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    written_paths["notes"].write_text(notes_text, encoding="utf-8")

    return {
        **written_paths,
        "manifest_payload": manifest_payload,
        "summary_payload": summary_payload,
        "test_result": test_result,
    }
