import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_repository import validate_repository


class RepositoryValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write_json('plugin.json', {
            '$schema': 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
            'name': 'example',
            'extensions': {'com.openai': {'interface': {'logo': './assets/logo.png'}}},
        })
        self.write('assets/logo.png', b'image fixture')
        self.write_json('.agents/plugins/marketplace.json', {
            'name': 'example-market',
            'plugins': [{
                'name': 'example',
                'source': {'source': 'local', 'path': './'},
                'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'},
                'category': 'Productivity',
            }],
        })
        self.write('skills/example/SKILL.md',
                   '---\nname: example\ndescription: Review example contracts.\n---\n'
                   '[Reference][ref]\n\n[ref]: references/guide.md\n'
                   '```md\n[not a reference](missing.md)\n```\n')
        self.write('skills/example/references/guide.md', '# Guide\n')
        self.write('skills/example/agents/openai.yaml',
                   'interface:\n  icon_small: ./assets/icon.png\n')
        self.write('skills/example/assets/icon.png', b'image fixture')
        self.write('evals/example/runs/one/output.md', 'result\n')
        self.write_json('evals/example/runs/one/manifest.json', {
            'files': {'output.md': {
                'sha256': hashlib.sha256(b'result\n').hexdigest(),
                'utf8Bytes': 7,
            }},
        })

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if isinstance(content, bytes) else content.encode())

    def write_json(self, name, content):
        self.write(name, json.dumps(content))

    def edit_json(self, name, edit):
        content = json.loads((self.root / name).read_text())
        edit(content)
        self.write_json(name, content)

    def assert_invalid(self, diagnostic):
        with self.assertRaisesRegex(ValueError, diagnostic):
            validate_repository(self.root)

    def test_valid_package_is_read_only(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        validate_repository(self.root)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_rejects_unknown_plugin_field(self):
        self.edit_json('plugin.json', lambda d: d.update({'unexpected': True}))
        self.assert_invalid('plugin.json')

    def test_rejects_missing_marketplace(self):
        (self.root / '.agents/plugins/marketplace.json').unlink()
        self.assert_invalid('marketplace.json')

    def test_rejects_marketplace_name_mismatch(self):
        self.edit_json('.agents/plugins/marketplace.json',
                       lambda d: d['plugins'][0].update({'name': 'other'}))
        self.assert_invalid('marketplace.json')

    def test_rejects_invalid_marketplace_policy(self):
        self.edit_json('.agents/plugins/marketplace.json',
                       lambda d: d['plugins'][0]['policy'].update({'installation': 'TYPO'}))
        self.assert_invalid('marketplace.json')

    def test_rejects_invalid_skill_metadata(self):
        self.write('skills/example/SKILL.md', '---\nname: other\n---\nText\n')
        self.assert_invalid('skills/example')

    def test_rejects_missing_reference_style_target(self):
        (self.root / 'skills/example/references/guide.md').unlink()
        self.assert_invalid('guide.md')

    def test_rejects_external_skill_file_reference(self):
        self.write('skills/example/SKILL.md',
                   '---\nname: example\ndescription: Example.\n---\n[Logo](../../assets/logo.png)')
        self.assert_invalid('logo.png')

    def test_rejects_missing_plugin_logo(self):
        (self.root / 'assets/logo.png').unlink()
        self.assert_invalid('logo.png')

    def test_rejects_missing_skill_icon(self):
        (self.root / 'skills/example/assets/icon.png').unlink()
        self.assert_invalid('icon.png')

    def test_rejects_symlink_outside_skill(self):
        icon = self.root / 'skills/example/assets/icon.png'
        icon.unlink()
        icon.symlink_to(self.root / 'assets/logo.png')
        self.assert_invalid('icon.png')

    def test_rejects_modified_evaluation_output(self):
        self.write('evals/example/runs/one/output.md', 'edited\n')
        self.assert_invalid('output.md')

    def test_rejects_missing_evaluation_manifest(self):
        (self.root / 'evals/example/runs/one/manifest.json').unlink()
        self.assert_invalid('manifest.json')

    def test_rejects_empty_evaluation_manifest(self):
        self.write_json('evals/example/runs/one/manifest.json', {'files': {}})
        self.assert_invalid('manifest.json')

    def test_rejects_manifest_path_outside_run(self):
        self.write_json('evals/example/runs/one/manifest.json', {
            'files': {'../../../../assets/logo.png': {
                'sha256': hashlib.sha256(b'image fixture').hexdigest(),
            }},
        })
        self.assert_invalid('logo.png')


if __name__ == '__main__':
    unittest.main()
