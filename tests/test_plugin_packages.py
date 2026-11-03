import json
import shutil
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from scripts.validate_repository import SCHEMA, check_plugin, check_skills
from scripts.sync_plugins import sync_plugins

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {
    'unif-engineering-skills': ['unif-architecture-design', 'unif-code-delivery'],
    'unif-rn-skills': ['unif-rn-dev', 'unif-rn-test', 'unif-rn-review'],
    'unif-harmony-skills': ['unif-harmony-dev', 'unif-harmony-test', 'unif-harmony-review'],
    'unif-python-skills': ['unif-python-dev', 'unif-python-test', 'unif-python-review'],
    'unif-library-skills': ['unif-' + name for name in
        ('amap', 'camera', 'chat', 'design', 'files', 'hms-scan', 'icons', 'logger', 'oss', 'speech', 'umeng')],
}


class PluginPackageTests(unittest.TestCase):
    def test_marketplace_has_exactly_five_groups(self):
        market = json.loads((ROOT / '.agents/plugins/marketplace.json').read_text())
        self.assertEqual({p['name']: p['source']['path'] for p in market['plugins']},
                         {name: './plugins/' + name for name in GROUPS})

    def test_every_plugin_survives_isolated_install(self):
        validator = Draft202012Validator(json.loads(SCHEMA.read_text()))
        for name, skills in GROUPS.items():
            with self.subTest(plugin=name), tempfile.TemporaryDirectory() as directory:
                isolated = Path(directory) / name
                shutil.copytree(ROOT / 'plugins' / name, isolated)
                self.assertEqual(check_plugin(isolated, validator)['name'], name)
                self.assertEqual(check_skills(isolated), len(skills))
                self.assertEqual({p.name for p in (isolated / 'skills').iterdir()}, set(skills))
                self.assertFalse(any(p.is_symlink() for p in isolated.rglob('*')))

    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        for name in ('skills', 'assets', 'plugins'):
            shutil.copytree(ROOT / name, root / name)
        shutil.copyfile(ROOT / 'plugin.json', root / 'plugin.json')
        if (ROOT / 'LICENSE').exists():
            shutil.copyfile(ROOT / 'LICENSE', root / 'LICENSE')
        return root

    def test_check_detects_stale_skill_content(self):
        root = self.fixture()
        target = root / 'plugins/unif-library-skills/skills/unif-icons/SKILL.md'
        target.write_text(target.read_text() + '\nstale\n')
        with self.assertRaises(ValueError):
            sync_plugins(root, check=True)
        sync_plugins(root)
        sync_plugins(root, check=True)

    def test_unknown_plugin_file_is_preserved_and_rejected(self):
        root = self.fixture()
        path = root / 'plugins/unif-rn-skills/custom.txt'
        path.write_text('user change')
        with self.assertRaises(ValueError):
            sync_plugins(root)
        self.assertEqual(path.read_text(), 'user change')

    def test_symlink_cannot_escape_isolated_plugin(self):
        root = self.fixture()
        path = root / 'plugins/unif-rn-skills/skills/unif-rn-dev/SKILL.md'
        path.unlink()
        path.symlink_to(ROOT / 'skills/unif-rn-dev/SKILL.md')
        with self.assertRaises(ValueError):
            sync_plugins(root, check=True)

    def test_root_source_files_reject_symlinks_without_touching_plugins(self):
        for name in ('plugin.json', 'LICENSE'):
            for broken in (False, True):
                for check in (False, True):
                    with self.subTest(source=name, broken=broken, check=check):
                        root = self.fixture()
                        with tempfile.TemporaryDirectory() as directory:
                            outside = Path(directory) / name
                            if not broken:
                                content = (root / 'plugin.json').read_bytes() if name == 'plugin.json' else b'outside license'
                                outside.write_bytes(content)
                            source = root / name
                            source.unlink(missing_ok=True)
                            source.symlink_to(outside)
                            before = {str(p.relative_to(root)): p.read_bytes()
                                      for p in (root / 'plugins').rglob('*') if p.is_file()}
                            with self.assertRaises(ValueError):
                                sync_plugins(root, check=check)
                            after = {str(p.relative_to(root)): p.read_bytes()
                                     for p in (root / 'plugins').rglob('*') if p.is_file()}
                            self.assertEqual(after, before)

    def test_root_source_files_must_be_regular_files(self):
        for name in ('plugin.json', 'LICENSE'):
            with self.subTest(source=name):
                root = self.fixture()
                source = root / name
                source.unlink(missing_ok=True)
                source.mkdir()
                with self.assertRaises(ValueError):
                    sync_plugins(root)


if __name__ == '__main__':
    unittest.main()
