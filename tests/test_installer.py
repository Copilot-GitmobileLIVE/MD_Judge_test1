from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from md_judge_agent_plugin.installer import AGENT_FILENAME, export_agent, install_agent, load_agent_text


class InstallerTests(unittest.TestCase):
    def test_load_agent_text_has_frontmatter(self):
        content = load_agent_text()
        self.assertIn("name: MD_Judge", content)
        self.assertTrue(content.startswith("---"))

    def test_export_agent_writes_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / AGENT_FILENAME
            written_path = export_agent(output_path)

            self.assertEqual(written_path, output_path)
            self.assertEqual(output_path.read_text(encoding="utf-8"), load_agent_text())

    def test_install_agent_uses_workspace_layout(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            installed_path = install_agent(workspace)

            self.assertEqual(installed_path, workspace / ".github" / "agents" / AGENT_FILENAME)
            self.assertTrue(installed_path.exists())


if __name__ == "__main__":
    unittest.main()
