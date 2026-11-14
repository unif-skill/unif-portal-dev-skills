import hashlib
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import cast

from scripts.sync_architecture import TopicRecord

from scripts.validate_repository import check_skills


ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / 'plugins'
PLATFORMS = ('rn', 'harmony', 'python')
STAGES = ('dev', 'test', 'review')
EXPECTED_SKILLS = {
    'unif-architecture-design', 'unif-code-delivery', 'unif-platform-rules',
    'unif-icons', 'unif-design', 'unif-chat', 'unif-camera', 'unif-hms-scan', 'unif-umeng',
    'unif-amap', 'unif-files', 'unif-logger', 'unif-oss', 'unif-speech',
    *(f'unif-{platform}-{stage}' for platform in PLATFORMS for stage in STAGES),
}


class IndependentSkillTests(unittest.TestCase):
    def test_platform_entries_replace_the_three_mixed_entries(self) -> None:
        self.assertEqual({p.parent.name for p in PLUGINS.glob('*/skills/*/SKILL.md')}, EXPECTED_SKILLS)

    def test_platform_rules_have_one_owner(self) -> None:
        owners = {p.parents[1].name: p for p in PLUGINS.glob('*/skills/*/references/source.json')}
        self.assertEqual(set(owners), {
            'unif-platform-rules', 'unif-architecture-design',
            *(f'unif-{platform}-dev' for platform in PLATFORMS),
            *(f'unif-{library}' for library in ('camera', 'chat', 'design', 'hms-scan', 'icons', 'umeng')),
        })
        topics: set[tuple[str, str]] = set()
        for name, manifest in owners.items():
            records = cast(dict[str, dict[str, TopicRecord]], json.loads(manifest.read_text()))['files']
            if name == 'unif-platform-rules':
                self.assertEqual(set(records), {
                    'architecture/scope.md', 'architecture/responsibilities.md', 'architecture/composition.md',
                    'architecture/state.md', 'architecture/contracts.md', 'architecture/verification.md',
                })
            for topic, data in records.items():
                content = (manifest.parent / topic).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), data['sha256'], topic)
                for section in data['sections']:
                    key = section['source'], section['heading']
                    self.assertNotIn(key, topics, (name, topic))
                    topics.add(key)

    def test_specialist_topics_resolve_from_the_named_rules_skill(self) -> None:
        owner = PLUGINS / 'unif-platform-rules/skills/unif-platform-rules'
        stages = ['unif-architecture-design', 'unif-code-delivery',
                  *(f'unif-{platform}-{stage}' for platform in PLATFORMS for stage in STAGES)]
        for name in stages:
            consumer = next(PLUGINS.glob(f'*/skills/{name}/SKILL.md'))
            with self.subTest(skill=name):
                body = consumer.read_text()
                self.assertIn('$unif-platform-rules', body)
                references = list(re.finditer(r'`(references/[^ `#]+\.md)(?:#([^`]+))?`', body))
                self.assertTrue(references, name)
                for match in references:
                    topic, anchor = match[1], match[2]
                    text = (owner / topic).read_text()
                    if anchor:
                        headings = [line.lstrip('# ').strip().lower() for line in text.splitlines()
                                    if line.startswith('#')]
                        self.assertIn(anchor, [re.sub(r'[^\w -]', '', h).replace(' ', '-') for h in headings],
                                      f'{name}: {topic}#{anchor}')

    def test_organization_profile_is_available_to_standalone_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / 'skills/unif-code-delivery'
            _ = shutil.copytree(PLUGINS / 'unif-engineering-skills/skills/unif-code-delivery', target)
            profile = target / 'assets/organization.json'
            data = cast(dict[str, object], json.loads(profile.read_text()))
            self.assertEqual(data['releaseAppId'], 3890760)
            self.assertEqual(data['owner'], 'unif-design')
            self.assertEqual(str(data['pagesURL']).format(repo='react-native-example'), 'https://unif-design.github.io/react-native-example/')
            self.assertEqual(check_skills(root), 1)
            data['privateKey'] = 'FAKE_SECRET'
            _ = profile.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'organization'):
                _ = check_skills(root)

    def test_malformed_or_sensitive_organization_data_is_rejected(self) -> None:
        invalid_files: list[dict[str, object]] = [{}, {}, {}]
        samples: tuple[tuple[str, object], ...] = (
            ('schemaVersion', True),
            ('obsoleteFiles', invalid_files),
            ('security', {'codeqlDefaultSetup': 'not-configured', 'dependabotSecurityUpdates': 'disabled', 'privateVulnerabilityReporting': 1}),
            ('releaseAppId', 'FAKE_SECRET'),
            ('repositorySettings', {'privateKey': 'FAKE_SECRET'}),
        )
        for field, value in samples:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                target = root / 'skills/unif-code-delivery'
                _ = shutil.copytree(PLUGINS / 'unif-engineering-skills/skills/unif-code-delivery', target)
                profile = target / 'assets/organization.json'
                data = cast(dict[str, object], json.loads(profile.read_text()))
                data[field] = value
                _ = profile.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    _ = check_skills(root)
