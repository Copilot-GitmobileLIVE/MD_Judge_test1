from __future__ import annotations

from importlib.resources import files
from pathlib import Path


AGENT_NAME = "MD_Judge"
AGENT_FILENAME = f"{AGENT_NAME}.agent.md"


def load_agent_text() -> str:
    return files("md_judge_agent_plugin.agents").joinpath(AGENT_FILENAME).read_text(encoding="utf-8")


def export_agent(output_path: Path, force: bool = False) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not force:
        raise FileExistsError(
            f"Refusing to overwrite existing file: {output_path}. Use --force to replace it."
        )

    output_path.write_text(load_agent_text(), encoding="utf-8")
    return output_path


def install_agent(target_dir: Path, force: bool = False) -> Path:
    install_path = target_dir / ".github" / "agents" / AGENT_FILENAME
    return export_agent(install_path, force=force)
