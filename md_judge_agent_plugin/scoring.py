from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9_-]+")
DEFAULT_RUBRIC = {
    "task_fit": 2,
    "correctness_and_completeness": 4,
    "reasoning_and_evidence": 2,
    "markdown_or_packaging_quality": 1,
    "safety_and_limitations_handling": 1,
}


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
    return output_root / f"{sanitize_agent_name(evaluated_agent_name)}_{format_timestamp(timestamp)}_scoring"


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
