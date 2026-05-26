from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from md_judge_agent_plugin.scoring import SCORING_RESULTS_DIRNAME, build_output_dir, evaluate_workspace, initialize_scoring_bundle


class ScoringTests(unittest.TestCase):
    def test_build_output_dir_uses_agent_name_and_timestamp(self):
        output_dir = build_output_dir(
            output_root=Path("C:\\temp"),
            evaluated_agent_name="MD Test Agent",
            timestamp=datetime(2026, 5, 25, 12, 45, 30, tzinfo=timezone.utc),
        )
        self.assertEqual(output_dir.parent.name, SCORING_RESULTS_DIRNAME)
        self.assertEqual(output_dir.name, "md_test_agent_20260525_124530_scoring")

    def test_initialize_scoring_bundle_writes_expected_files(self):
        timestamp = datetime(2026, 5, 25, 12, 45, 30, tzinfo=timezone.utc)

        with tempfile.TemporaryDirectory() as tmpdir:
            written_paths = initialize_scoring_bundle(
                output_root=Path(tmpdir),
                evaluated_agent_name="MD_Test",
                task_summary="Evaluate packaging quality.",
                timestamp=timestamp,
            )

            self.assertEqual(written_paths["output_dir"].parent.name, SCORING_RESULTS_DIRNAME)
            self.assertTrue(written_paths["manifest"].exists())
            self.assertTrue(written_paths["summary"].exists())
            self.assertTrue(written_paths["notes"].exists())

            summary_payload = json.loads(written_paths["summary"].read_text(encoding="utf-8"))
            self.assertEqual(summary_payload["evaluated_agent_name"], "MD_Test")
            self.assertIsNone(summary_payload["score"])

    def test_evaluate_workspace_writes_completed_scoring_files(self):
        timestamp = datetime(2026, 5, 25, 12, 45, 30, tzinfo=timezone.utc)

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir) / "MD_Main_Agent"
            package_dir = workspace / "md_test_agent_plugin"
            agents_dir = package_dir / "agents"
            tests_dir = workspace / "tests"

            agents_dir.mkdir(parents=True)
            tests_dir.mkdir(parents=True)

            (workspace / "README.md").write_text(
                "# MD_Test Agent Plugin\n\nUse md-test-agent show and md-test-agent install.\n",
                encoding="utf-8",
            )
            (workspace / "pyproject.toml").write_text(
                "[project]\nname = \"md-test-agent-plugin\"\n\n[project.scripts]\nmd-test-agent = \"md_test_agent_plugin.cli:main\"\n",
                encoding="utf-8",
            )
            (package_dir / "cli.py").write_text(
                "def main():\n    pass\n\nCOMMANDS = ['show', 'export', 'install']\n",
                encoding="utf-8",
            )
            (package_dir / "installer.py").write_text(
                "INSTALL_PATH = '.github/agents/MD_Test.agent.md'\n",
                encoding="utf-8",
            )
            (agents_dir / "MD_Test.agent.md").write_text(
                "---\nname: MD_Test\n---\n",
                encoding="utf-8",
            )
            (tests_dir / "test_installer.py").write_text(
                "import unittest\n\nclass InstallerTests(unittest.TestCase):\n    def test_ok(self):\n        self.assertTrue(True)\n\nif __name__ == '__main__':\n    unittest.main()\n",
                encoding="utf-8",
            )

            evaluation = evaluate_workspace(
                target_workspace=workspace,
                evaluated_agent_name="MD_Main_Agent",
                output_root=Path(tmpdir),
                task_summary="Evaluate packaging quality.",
                timestamp=timestamp,
            )

            self.assertEqual(evaluation["output_dir"].parent.name, SCORING_RESULTS_DIRNAME)
            self.assertEqual(evaluation["output_dir"].name, "md_main_agent_20260525_124530_scoring")
            self.assertTrue(evaluation["summary"].exists())
            self.assertTrue(evaluation["notes"].exists())

            summary_payload = json.loads(evaluation["summary"].read_text(encoding="utf-8"))
            self.assertEqual(summary_payload["evaluated_agent_alias"], "MD_Test")
            self.assertGreaterEqual(summary_payload["score"], 7)
            self.assertTrue(summary_payload["passed"])


if __name__ == "__main__":
    unittest.main()
