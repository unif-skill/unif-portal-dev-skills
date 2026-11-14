import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import TypedDict, cast

from jsonschema import Draft202012Validator
from scripts.validate_repository import SCHEMA, check_plugin, check_skills, validate_repository

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {
    'unif-platform-rules': ['unif-platform-rules'],
    'unif-engineering-skills': ['unif-architecture-design', 'unif-code-delivery'],
    'unif-react-native-skills': ['unif-rn-dev', 'unif-rn-test', 'unif-rn-review'],
    'unif-harmony-skills': ['unif-harmony-dev', 'unif-harmony-test', 'unif-harmony-review'],
    'unif-python-skills': ['unif-python-dev', 'unif-python-test', 'unif-python-review'],
    **{f'unif-{name}': [f'unif-{name}'] for name in
       ('amap', 'camera', 'chat', 'design', 'files', 'hms-scan', 'icons', 'logger', 'oss', 'speech', 'umeng')},
}


class MarketSource(TypedDict):
    path: str


class InstallPolicy(TypedDict):
    installation: str


class MarketPlugin(TypedDict):
    name: str
    source: MarketSource
    policy: InstallPolicy


class PluginPackageTests(unittest.TestCase):
    def test_marketplace_defaults_to_platform_rules_and_offers_individual_libraries(self):
        entries = cast(list[MarketPlugin], json.loads((ROOT / '.agents/plugins/marketplace.json').read_text())['plugins'])
        self.assertEqual({p['name']: p['source']['path'] for p in entries},
                         {name: './plugins/' + name for name in GROUPS})
        for entry in entries:
            expected = 'INSTALLED_BY_DEFAULT' if entry['name'] == 'unif-platform-rules' else 'AVAILABLE'
            self.assertEqual(entry['policy']['installation'], expected, entry['name'])

    def test_every_plugin_survives_isolated_install(self):
        validator = Draft202012Validator(cast(dict[str, object], json.loads(SCHEMA.read_text())))
        for name, skills in GROUPS.items():
            with self.subTest(plugin=name), tempfile.TemporaryDirectory() as directory:
                isolated = Path(directory) / name
                _ = shutil.copytree(ROOT / 'plugins' / name, isolated)
                self.assertEqual(check_plugin(isolated, validator)['name'], name)
                self.assertEqual(check_skills(isolated, standalone=False), len(skills))
                self.assertEqual({p.name for p in (isolated / 'skills').iterdir()}, set(skills))
                self.assertFalse(any(p.is_symlink() for p in isolated.rglob('*')))

    def fixture(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        for name in ('assets', 'plugins', '.agents'):
            _ = shutil.copytree(ROOT / name, root / name)
        _ = shutil.copyfile(ROOT / 'plugin.json', root / 'plugin.json')
        return root

    def test_business_plugin_files_are_maintained_in_place(self) -> None:
        root = self.fixture()
        plugin = root / 'plugins/unif-react-native-skills'
        content = plugin / 'guide.md'
        _ = content.write_text('RN guide')
        skill = plugin / 'skills/unif-rn-dev/SKILL.md'
        _ = skill.write_text(skill.read_text() + '\n[Guide](../../guide.md)\n')
        self.assertEqual(validate_repository(root), (23, 0, 0))
        self.assertEqual(content.read_text(), 'RN guide')

    def test_root_skills_would_duplicate_sources(self) -> None:
        root = self.fixture()
        (root / 'skills').mkdir()
        with self.assertRaisesRegex(ValueError, '重复入口'):
            _ = validate_repository(root)

    def test_duplicate_skill_in_another_plugin_is_rejected(self) -> None:
        root = self.fixture()
        skill = 'unif-amap'
        _ = shutil.copytree(root / 'plugins' / skill / 'skills' / skill,
                            root / 'plugins/unif-engineering-skills/skills' / skill)
        with self.assertRaisesRegex(ValueError, '其他插件提供'):
            _ = validate_repository(root)

    def test_plugin_version_matches_release_version(self) -> None:
        root = self.fixture()
        path = root / 'plugins/unif-react-native-skills/plugin.json'
        data = cast(dict[str, object], json.loads(path.read_text()))
        data['version'] = '0.1.2'
        _ = path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, '版本'):
            _ = validate_repository(root)

    def test_distributed_source_must_have_one_version_and_cover_each_line_once(self) -> None:
        root = self.fixture()
        content = '<!-- 此文件由 scripts/sync_architecture.py 生成 -->\n\n属主章节。\n'
        def record(skill: str, start: int, end: int, source_hash: str) -> None:
            topic = next((root / 'plugins').glob('*/skills/' + skill))
            directory = topic / 'references'
            directory.mkdir(exist_ok=True)
            assert not (directory / 'source.json').exists()
            _ = (directory / 'shared-example.md').write_text(content)
            section = {'heading': 'section-' + str(start), 'lines': [start, end]}
            manifest = {
                'formatVersion': 2,
                'sources': {'EXAMPLE.md': {'source': 'canonical/EXAMPLE.md', 'sha256': source_hash,
                                            'lines': 4, 'selectedSections': [section]}},
                'files': {'shared-example.md': {'sha256': hashlib.sha256(content.encode()).hexdigest(),
                                               'sections': [{**section, 'source': 'EXAMPLE.md'}]}},
            }
            _ = (directory / 'source.json').write_text(json.dumps(manifest))

        record('unif-amap', 1, 2, 'c' * 64)
        second = root / 'plugins/unif-engineering-skills/skills/unif-code-delivery/references/source.json'
        for start, digest, diagnostic in ((1, 'c', '重复'), (4, 'c', '缺失'), (3, 'd', '版本')):
            with self.subTest(start=start, digest=digest):
                record('unif-code-delivery', start, 4, digest * 64)
                with self.assertRaisesRegex(ValueError, diagnostic):
                    _ = validate_repository(root)
                second.unlink()
        record('unif-code-delivery', 3, 4, 'c' * 64)
        self.assertEqual(validate_repository(root), (23, 0, 0))

    def test_unlisted_package_is_rejected(self) -> None:
        root = self.fixture()
        (root / 'plugins/other').mkdir()
        with self.assertRaisesRegex(ValueError, '市场入口'):
            _ = validate_repository(root)

    def test_relative_reference_may_not_enter_another_plugin(self) -> None:
        root = self.fixture()
        skill = root / 'plugins/unif-react-native-skills/skills/unif-rn-dev/SKILL.md'
        _ = skill.write_text(skill.read_text() + '\n[Foreign](../../../unif-platform-rules/plugin.json)\n')
        with self.assertRaisesRegex(ValueError, '越出'):
            _ = validate_repository(root)

    def test_unreferenced_asset_symlink_is_rejected(self) -> None:
        root = self.fixture()
        path = root / 'plugins/unif-react-native-skills/unexpected-link'
        path.symlink_to(root / 'assets/logo.png')
        with self.assertRaisesRegex(ValueError, 'unexpected-link'):
            _ = validate_repository(root)

    def test_root_manifest_and_optional_license_must_be_regular_files(self) -> None:
        for name in ('plugin.json', 'LICENSE'):
            with self.subTest(source=name):
                root = self.fixture()
                path = root / name
                path.unlink(missing_ok=True)
                path.symlink_to(root / 'missing')
                with self.assertRaisesRegex(ValueError, '普通文件'):
                    _ = validate_repository(root)
                path.unlink()
                path.mkdir()
                with self.assertRaisesRegex(ValueError, '普通文件'):
                    _ = validate_repository(root)


if __name__ == '__main__':
    _ = unittest.main()
