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
            'version': '0.0.1',
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

    def assert_invalid(self, diagnostic, **options):
        with self.assertRaisesRegex(ValueError, diagnostic):
            validate_repository(self.root, **options)

    def test_default_validation_does_not_depend_on_local_evaluation_artifacts(self):
        (self.root / 'evals/example/runs/one/manifest.json').unlink()
        self.assertEqual(validate_repository(self.root), (1, 0, 0))

    def test_local_evaluation_validation_is_explicit(self):
        self.assertEqual(validate_repository(self.root, include_evals=True), (1, 1, 1))

    def generated_references(self):
        content = '<!-- 此文件由 scripts/sync_architecture.py 生成 -->\n\n# Guide\n'
        self.write('skills/example/references/guide.md', content)
        self.write_json('skills/example/references/source.json', {
            'formatVersion': 2,
            'sources': {'SOURCE.md': {'source': 'canonical/SOURCE.md', 'sha256': 'a' * 64, 'lines': 3}},
            'files': {'guide.md': {
                'sha256': hashlib.sha256(content.encode()).hexdigest(),
                'sections': [{'source': 'SOURCE.md', 'heading': '', 'lines': [1, 3]}],
            }},
        })

    def test_generated_material_is_verifiable_without_canonical_checkout(self):
        self.generated_references()
        validate_repository(self.root)

    def test_rejects_edited_generated_material(self):
        self.generated_references()
        self.write('skills/example/references/guide.md', '# Changed\n')
        self.assert_invalid('guide.md')

    def test_rejects_missing_generated_source_record(self):
        self.generated_references()
        (self.root / 'skills/example/references/source.json').unlink()
        self.assert_invalid('source.json')

    def test_rejects_omitted_source_sections(self):
        self.generated_references()
        self.edit_json('skills/example/references/source.json',
                       lambda d: d['files']['guide.md']['sections'][0].update({'lines': [1, 2]}))
        self.assert_invalid('SOURCE.md')

    def test_rejects_duplicate_source_sections(self):
        self.generated_references()
        self.edit_json('skills/example/references/source.json',
                       lambda d: d['files']['guide.md']['sections'].append(
                           {'source': 'SOURCE.md', 'heading': '', 'lines': [1, 3]}))
        self.assert_invalid('SOURCE.md')

    def test_rejects_unknown_source(self):
        self.generated_references()
        self.edit_json('skills/example/references/source.json',
                       lambda d: d['files']['guide.md']['sections'][0].update({'source': 'MISSING.md'}))
        self.assert_invalid('MISSING.md')

    def test_rejects_unregistered_generated_material(self):
        self.generated_references()
        self.write('skills/example/references/old.md', '<!-- 此文件由 scripts/sync_architecture.py 生成 -->\nOld\n')
        self.assert_invalid('old.md')

    def test_valid_package_is_read_only(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        validate_repository(self.root)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_rejects_unknown_plugin_field(self):
        self.edit_json('plugin.json', lambda d: d.update({'unexpected': True}))
        self.assert_invalid('plugin.json')

    def test_rejects_missing_version(self):
        self.edit_json('plugin.json', lambda d: d.pop('version'))
        self.assert_invalid('version')

    def test_rejects_non_release_version(self):
        for version in ('0.1', 'v0.0.1', '00.1.0', '0.01.0', '0.0.1+local', ''):
            with self.subTest(version=version):
                self.edit_json('plugin.json', lambda d: d.update({'version': version}))
                self.assert_invalid('version')

    def test_accepts_zero_major_upgrades(self):
        for version in ('0.0.2', '0.1.0', '0.12.34'):
            with self.subTest(version=version):
                self.edit_json('plugin.json', lambda d: d.update({'version': version}))
                validate_repository(self.root)

    def test_rejects_one_major_and_later_versions(self):
        for version in ('1.0.0', '1.2.3', '2.0.0'):
            with self.subTest(version=version):
                self.edit_json('plugin.json', lambda d: d.update({'version': version}))
                self.assert_invalid('0.x.x')

    def test_accepts_release_tag_matching_manifest(self):
        validate_repository(self.root, release_tag='v0.0.1')

    def test_rejects_release_tag_mismatch(self):
        for tag in ('v0.0.2', '0.0.1', 'v1.0.0'):
            with self.subTest(tag=tag):
                with self.assertRaisesRegex(ValueError, 'tag'):
                    validate_repository(self.root, release_tag=tag)

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
        self.assert_invalid('output.md', include_evals=True)

    def test_rejects_missing_evaluation_manifest(self):
        (self.root / 'evals/example/runs/one/manifest.json').unlink()
        self.assert_invalid('manifest.json', include_evals=True)

    def test_rejects_empty_evaluation_manifest(self):
        self.write_json('evals/example/runs/one/manifest.json', {'files': {}})
        self.assert_invalid('manifest.json', include_evals=True)

    def test_rejects_manifest_path_outside_run(self):
        self.write_json('evals/example/runs/one/manifest.json', {
            'files': {'../../../../assets/logo.png': {
                'sha256': hashlib.sha256(b'image fixture').hexdigest(),
            }},
        })
        self.assert_invalid('logo.png', include_evals=True)


if __name__ == '__main__':
    unittest.main()
