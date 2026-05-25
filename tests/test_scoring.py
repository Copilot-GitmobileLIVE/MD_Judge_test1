from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from md_judge_agent_plugin.scoring import build_output_dir, initialize_scoring_bundle


class ScoringTests(unittest.TestCase):
    def test_build_output_dir_uses_agent_name_and_timestamp(self):
        output_dir = build_output_dir(
            output_root=Path("C:\\temp"),
            evaluated_agent_name="MD Test Agent",
            timestamp=datetime(2026, 5, 25, 12, 45, 30, tzinfo=timezone.utc),
        )
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

            self.assertTrue(written_paths["manifest"].exists())
            self.assertTrue(written_paths["summary"].exists())
            self.assertTrue(written_paths["notes"].exists())

            summary_payload = json.loads(written_paths["summary"].read_text(encoding="utf-8"))
            self.assertEqual(summary_payload["evaluated_agent_name"], "MD_Test")
            self.assertIsNone(summary_payload["score"])


if __name__ == "__main__":
    unittest.main()
