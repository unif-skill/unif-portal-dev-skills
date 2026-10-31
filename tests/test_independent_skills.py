import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.validate_repository import check_skills


ROOT = Path(__file__).resolve().parents[1]
PLATFORMS = ('rn', 'harmony', 'python')
STAGES = ('dev', 'test', 'review')
EXPECTED_SKILLS = {
    'unif-architecture-design', 'unif-code-delivery',
    'unif-icons', 'unif-design', 'unif-chat', 'unif-camera', 'unif-hms-scan', 'unif-umeng',
    *(f'unif-{platform}-{stage}' for platform in PLATFORMS for stage in STAGES),
}


class IndependentSkillTests(unittest.TestCase):
    def test_platform_entries_replace_the_three_mixed_entries(self):
        self.assertEqual({p.name for p in (ROOT / 'skills').iterdir() if p.is_dir()}, EXPECTED_SKILLS)

    def test_each_platform_bundles_only_its_own_canonical_sources(self):
        source_prefixes = {
            'rn': ('PORTAL_',),
            'harmony': ('HARMONY_', 'libraries/harmony-'),
            'python': ('PYTHON_',),
        }
        for platform in PLATFORMS:
            for stage in STAGES:
                name = f'unif-{platform}-{stage}'
                with self.subTest(skill=name):
                    reference = ROOT / 'skills' / name / 'references'
                    data = json.loads((reference / 'source.json').read_text())
                    self.assertIn('ARCHITECTURE.md', data['sources'])
                    self.assertGreater(len(data['sources']), 1)
                    for source in data['sources']:
                        self.assertTrue(source == 'ARCHITECTURE.md' or source.startswith(source_prefixes[platform]), source)
                    for topic in ('state', 'contracts', 'verification'):
                        self.assertTrue((reference / 'common' / f'{topic}.md').is_file())

    def test_every_complete_skill_works_without_siblings_or_root_tools(self):
        for source in sorted((ROOT / 'skills').iterdir()):
            if not source.is_dir():
                continue
            with self.subTest(skill=source.name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                target = root / 'skills' / source.name
                shutil.copytree(source, target, symlinks=True)
                self.assertEqual(check_skills(root), 1)
                self.assertTrue((target / 'agents/openai.yaml').is_file())
                self.assertFalse((root / 'scripts').exists())
                self.assertEqual(len(list((root / 'skills').iterdir())), 1)

    def test_stage_rules_are_bundled_with_verifiable_canonical_selections(self):
        required = {
            'unif-rn-dev': ('common/state.md', 'common/contracts.md', 'common/verification.md', 'rn/testing.md'),
            'unif-harmony-dev': ('common/state.md', 'common/contracts.md', 'common/verification.md', 'harmony/testing.md'),
            'unif-python-dev': ('common/state.md', 'common/verification.md'),
            'unif-rn-test': ('common/composition.md', 'common/state.md', 'common/contracts.md', 'common/verification.md', 'rn/testing.md'),
            'unif-harmony-test': ('common/composition.md', 'common/state.md', 'common/contracts.md', 'common/verification.md', 'harmony/testing.md'),
            'unif-python-test': ('common/composition.md', 'common/state.md', 'common/contracts.md', 'common/verification.md', 'python/validation.md'),
            'unif-rn-review': ('common/composition.md', 'common/state.md', 'common/contracts.md', 'common/verification.md', 'rn/ui.md'),
            'unif-harmony-review': ('common/composition.md', 'common/state.md', 'common/contracts.md', 'common/verification.md', 'harmony/state.md'),
            'unif-python-review': ('common/composition.md', 'common/state.md', 'common/contracts.md', 'common/verification.md', 'python/lifecycle.md'),
            'unif-code-delivery': ('common/contracts.md', 'common/verification.md', 'rn/testing.md', 'harmony/testing.md', 'python/validation.md'),
        }
        common_hashes = set()
        for name, topics in required.items():
            reference = ROOT / 'skills' / name / 'references'
            data = json.loads((reference / 'source.json').read_text())
            common_hashes.add(data['sources']['ARCHITECTURE.md']['sha256'])
            for topic in topics:
                with self.subTest(skill=name, topic=topic):
                    record = data['files'][topic]
                    self.assertEqual(hashlib.sha256((reference / topic).read_bytes()).hexdigest(), record['sha256'])
                    self.assertTrue(record['sections'])
        self.assertEqual(len(common_hashes), 1)

    def test_organization_profile_is_available_to_standalone_delivery(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / 'skills/unif-code-delivery'
            shutil.copytree(ROOT / 'skills/unif-code-delivery', target)
            profile = target / 'assets/organization.json'
            data = json.loads(profile.read_text())
            self.assertEqual(data['releaseAppId'], 3890760)
            self.assertEqual(data['owner'], 'unif-design')
            self.assertEqual(data['pagesURL'].format(repo='react-native-example'), 'https://unif-design.github.io/react-native-example/')
            self.assertEqual(check_skills(root), 1)
            data['privateKey'] = 'FAKE_SECRET'
            profile.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'organization'):
                check_skills(root)

    def test_malformed_or_sensitive_organization_data_is_rejected(self):
        for field, value in (
            ('schemaVersion', True),
            ('obsoleteFiles', [{}, {}, {}]),
            ('security', {'codeqlDefaultSetup': 'not-configured', 'dependabotSecurityUpdates': 'disabled', 'privateVulnerabilityReporting': 1}),
            ('releaseAppId', 'FAKE_SECRET'),
            ('repositorySettings', {'privateKey': 'FAKE_SECRET'}),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                target = root / 'skills/unif-code-delivery'
                shutil.copytree(ROOT / 'skills/unif-code-delivery', target)
                profile = target / 'assets/organization.json'
                data = json.loads(profile.read_text())
                data[field] = value
                profile.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    check_skills(root)
