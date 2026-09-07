import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_architecture.py"
SOURCE = "# 平台架构\n\n规则必须保留。\n\n- [领域](domains/example/ARCHITECTURE.md)：领域入口。\n"

class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.source = self.root / "source.md"
        self.source.write_text(SOURCE, encoding="utf-8")
        self.script = self.root / "package/scripts/sync_architecture.py"
        self.script.parent.mkdir(parents=True)
        if SCRIPT.exists():
            shutil.copy2(SCRIPT, self.script)
        self.reference = self.root / "package/skills/architecture-design/references"

    def run_sync(self, *args):
        return subprocess.run(
            [sys.executable, str(self.script), "--source", str(self.source), *args],
            capture_output=True, text=True,
        )

    def test_generate_preserves_rules_and_makes_relative_link_portable(self):
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.reference / "platform-architecture.md").read_text(encoding="utf-8")
        self.assertIn("规则必须保留。", text)
        self.assertIn("领域：领域入口。", text)
        self.assertNotIn("](domains/", text)
        self.assertNotIn(str(self.root), text)
        self.assertEqual(self.run_sync("--check").returncode, 0)

    def test_check_detects_snapshot_edit_without_overwriting_it(self):
        self.assertEqual(self.run_sync().returncode, 0)
        target = self.reference / "platform-architecture.md"
        target.write_text("被改写的规则", encoding="utf-8")
        result = self.run_sync("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_text(encoding="utf-8"), "被改写的规则")

    def test_check_detects_source_change(self):
        self.assertEqual(self.run_sync().returncode, 0)
        self.source.write_text(SOURCE + "\n新增规则。\n", encoding="utf-8")
        self.assertNotEqual(self.run_sync("--check").returncode, 0)

    def test_check_detects_source_record_corruption(self):
        self.assertEqual(self.run_sync().returncode, 0)
        (self.reference / "source.json").write_text("{}", encoding="utf-8")
        self.assertNotEqual(self.run_sync("--check").returncode, 0)

if __name__ == "__main__":
    unittest.main()

