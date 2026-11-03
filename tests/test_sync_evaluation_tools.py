import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


MODULE = Path(__file__).resolve().parents[1] / 'scripts/sync_evaluation_tools.py'
spec = importlib.util.spec_from_file_location('sync_evaluation_tools', MODULE)
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class EvaluationToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / 'uni'
        self.target = Path(self.temp.name) / 'unif'
        for root, name in [(self.source, 'uni-skills'), (self.target, 'unif-portal-dev-skills')]:
            root.mkdir()
            (root / 'plugin.json').write_text(json.dumps({'name': name}))
        for name in sync.FILES:
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('source: ' + name)

    def snapshot(self):
        return {str(p.relative_to(self.target)): p.read_bytes()
                for p in self.target.rglob('*') if p.is_file()}

    def test_independent_verification_and_explicit_upgrade(self):
        sync.sync_evaluation_tools(self.source, self.target)
        sync.check_evaluation_tools(self.target)
        self.assertIsNone(sync.check_evaluation_tools(self.source))
        before = self.snapshot()
        sync.sync_evaluation_tools(self.source, self.target, check=True)
        self.assertEqual(before, self.snapshot())
        (self.source / sync.FILES[0]).write_text('upgraded')
        with self.assertRaises(ValueError):
            sync.sync_evaluation_tools(self.source, self.target, check=True)
        self.assertEqual(before, self.snapshot())
        sync.sync_evaluation_tools(self.source, self.target)
        sync.check_evaluation_tools(self.target)

    def test_refuses_local_changes_without_overwriting_other_files(self):
        sync.sync_evaluation_tools(self.source, self.target)
        (self.target / sync.FILES[-1]).write_text('local work')
        before = self.snapshot()
        with self.assertRaises(ValueError):
            sync.sync_evaluation_tools(self.source, self.target)
        self.assertEqual(before, self.snapshot())

    def test_refuses_unmanaged_target_and_symlink(self):
        path = self.target / sync.FILES[0]
        path.parent.mkdir(parents=True)
        path.write_text('unmanaged')
        before = self.snapshot()
        with self.assertRaises(ValueError):
            sync.sync_evaluation_tools(self.source, self.target)
        self.assertEqual(before, self.snapshot())
        path.unlink()
        path.symlink_to(self.source / sync.FILES[0])
        with self.assertRaises(ValueError):
            sync.sync_evaluation_tools(self.source, self.target)

    def test_missing_or_forged_provenance_fails(self):
        with self.assertRaises((OSError, ValueError)):
            sync.check_evaluation_tools(self.target)
        sync.sync_evaluation_tools(self.source, self.target)
        path = self.target / sync.RECORD
        record = json.loads(path.read_text())
        record['files']['other.py'] = '0' * 64
        path.write_text(json.dumps(record))
        with self.assertRaises(ValueError):
            sync.check_evaluation_tools(self.target)

    def test_missing_source_does_not_write_partial_update(self):
        sync.sync_evaluation_tools(self.source, self.target)
        before = self.snapshot()
        (self.source / sync.FILES[-1]).unlink()
        with self.assertRaises((OSError, ValueError)):
            sync.sync_evaluation_tools(self.source, self.target)
        self.assertEqual(before, self.snapshot())

    def test_wrong_source_repository_is_rejected(self):
        (self.source / 'plugin.json').write_text('{"name":"unrelated"}')
        with self.assertRaises(ValueError):
            sync.sync_evaluation_tools(self.source, self.target)

    def test_current_repository_adopted_tools_are_consistent(self):
        sync.check_evaluation_tools(Path(__file__).resolve().parents[1])


if __name__ == '__main__':
    unittest.main()
