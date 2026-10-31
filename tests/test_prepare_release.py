import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.prepare_release import prepare


class PrepareReleaseTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        self.remote = base / 'remote.git'
        self.root = base / 'checkout'
        subprocess.run(['git', 'init', '--bare', str(self.remote)], check=True, capture_output=True)
        self.root.mkdir()
        self.git('init', '--initial-branch=main')
        self.git('config', 'user.name', 'Release Test')
        self.git('config', 'user.email', 'release@example.test')
        self.git('remote', 'add', 'origin', str(self.remote))
        self.manifest = self.root / 'plugin.json'
        self.manifest.write_text(json.dumps({'name': 'fixture', 'version': '0.3.3'}, indent=2) + '\n')
        (self.root / 'skill.md').write_text('published skill\n')
        self.commit('initial')
        self.git('tag', 'v0.3.3')
        self.git('push', 'origin', 'main', '--tags')
        (self.root / 'skill.md').write_text('improved skill\n')
        self.source = self.commit('fix: improve skill')
        self.git('push', 'origin', 'main')
        self.context = {
            'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'push',
            'GITHUB_REF': 'refs/heads/main', 'GITHUB_SHA': self.source,
        }
        self.validated = []

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, check=True,
                              text=True, capture_output=True).stdout.strip()

    def commit(self, message):
        self.git('add', '.')
        self.git('commit', '-m', message)
        return self.git('rev-parse', 'HEAD')

    def remote_head(self):
        return self.git('ls-remote', 'origin', 'refs/heads/main').split()[0]

    def validate(self, root, *, release_tag):
        self.assertEqual(root, self.root)
        self.assertEqual(release_tag, 'v' + json.loads(self.manifest.read_text())['version'])
        self.validated.append(release_tag)

    def run_prepare(self, validate=None):
        return prepare(self.root, self.context, validate or self.validate)

    def test_published_version_is_incremented_validated_and_written_back_to_main(self):
        result = self.run_prepare()
        self.assertEqual(result['status'], 'ready')
        self.assertEqual(result['version'], '0.3.4')
        self.assertEqual(result['commit'], self.remote_head())
        self.assertNotEqual(result['commit'], self.source)
        self.assertEqual(self.git('rev-parse', 'HEAD^'), self.source)
        self.assertEqual(self.git('diff', '--name-only', 'HEAD^', 'HEAD'), 'plugin.json')
        self.assertEqual(json.loads(self.manifest.read_text()), {'name': 'fixture', 'version': '0.3.4'})
        self.assertEqual(self.validated, ['v0.3.4'])
        self.assertEqual(self.git('status', '--porcelain'), '')
        self.assertNotIn('v0.3.4', self.git('tag', '--list').splitlines())

    def test_rerun_after_writeback_recovers_same_commit_without_another_increment(self):
        first = self.run_prepare()
        self.git('checkout', '--detach', self.source)
        second = self.run_prepare()
        self.assertEqual(second, first)
        self.assertEqual(self.remote_head(), first['commit'])
        self.assertEqual(self.validated, ['v0.3.4', 'v0.3.4'])

    def test_recovery_cannot_publish_behind_a_newer_existing_tag(self):
        first = self.run_prepare()
        self.git('tag', 'v0.4.0')
        self.git('push', 'origin', 'v0.4.0')
        self.git('checkout', '--detach', self.source)
        with self.assertRaisesRegex(ValueError, '版本'):
            self.run_prepare()
        self.assertEqual(self.remote_head(), first['commit'])

    def test_already_tagged_current_commit_is_reused_for_release_recovery(self):
        first = self.run_prepare()
        self.git('tag', 'v0.3.4')
        self.git('push', 'origin', 'v0.3.4')
        self.context['GITHUB_SHA'] = first['commit']
        second = self.run_prepare()
        self.assertEqual(second, first)
        self.assertEqual(json.loads(self.manifest.read_text())['version'], '0.3.4')

    def test_explicit_unreleased_zero_major_version_is_preserved(self):
        self.manifest.write_text(json.dumps({'name': 'fixture', 'version': '0.4.0'}) + '\n')
        source = self.commit('feat: new capability')
        self.git('push', 'origin', 'main')
        self.context['GITHUB_SHA'] = source
        result = self.run_prepare()
        self.assertEqual(result, {'status': 'ready', 'version': '0.4.0', 'commit': source})

    def test_explicit_unreleased_one_major_version_is_preserved(self):
        self.manifest.write_text(json.dumps({'name': 'fixture', 'version': '1.0.0'}) + '\n')
        source = self.commit('prepare authorized major')
        self.git('push', 'origin', 'main')
        self.context['GITHUB_SHA'] = source
        result = self.run_prepare()
        self.assertEqual(result, {'status': 'ready', 'version': '1.0.0', 'commit': source})

    def test_patch_increment_does_not_roll_over_to_minor_or_major(self):
        self.manifest.write_text(json.dumps({'name': 'fixture', 'version': '1.99.99'}) + '\n')
        self.commit('release previous version')
        self.git('tag', 'v1.99.99')
        (self.root / 'skill.md').write_text('next improvement\n')
        self.context['GITHUB_SHA'] = self.commit('fix: next improvement')
        self.git('push', 'origin', 'main', '--tags')
        self.assertEqual(self.run_prepare()['version'], '1.99.100')

    def test_unapproved_major_is_rejected_before_writeback(self):
        self.manifest.write_text(json.dumps({'name': 'fixture', 'version': '2.0.0'}) + '\n')
        self.context['GITHUB_SHA'] = self.commit('unapproved major')
        self.git('push', 'origin', 'main')
        before = self.remote_head()
        with self.assertRaisesRegex(ValueError, '主版本'):
            self.run_prepare()
        self.assertEqual(self.remote_head(), before)
        self.assertEqual(self.validated, [])

    def test_superseded_source_does_not_change_files_or_remote(self):
        (self.root / 'skill.md').write_text('concurrent improvement\n')
        newer = self.commit('fix: concurrent change')
        self.git('push', 'origin', 'main')
        self.git('checkout', '--detach', self.source)
        before = self.manifest.read_bytes()
        self.assertEqual(self.run_prepare()['status'], 'superseded')
        self.assertEqual(self.remote_head(), newer)
        self.assertEqual(self.manifest.read_bytes(), before)
        self.assertEqual(self.validated, [])

    def test_validation_failure_never_commits_or_pushes_candidate(self):
        def reject(*args, **kwargs):
            raise ValueError('invalid release candidate')
        with self.assertRaisesRegex(ValueError, 'invalid release candidate'):
            self.run_prepare(reject)
        self.assertEqual(self.remote_head(), self.source)
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.source)

    def test_concurrent_push_during_validation_is_not_overwritten(self):
        concurrent = []

        def advance(*args, **kwargs):
            tree = self.git('rev-parse', f'{self.source}^{{tree}}')
            newer = self.git('commit-tree', tree, '-p', self.source, '-m', 'concurrent commit')
            self.git('push', 'origin', f'{newer}:refs/heads/main')
            concurrent.append(newer)

        with self.assertRaises(RuntimeError):
            self.run_prepare(advance)
        self.assertEqual(self.remote_head(), concurrent[0])

    def test_recovery_rejects_a_commit_with_additional_changes(self):
        self.manifest.write_text(json.dumps({'name': 'fixture', 'version': '0.3.4'}) + '\n')
        (self.root / 'skill.md').write_text('unexpected unvalidated change\n')
        message = f'chore: 发布技能版本 0.3.4 [skip ci]\n\nRelease-Source: {self.source}'
        newer = self.commit(message)
        self.git('push', 'origin', 'main')
        self.git('checkout', '--detach', self.source)
        with self.assertRaisesRegex(ValueError, '发布提交'):
            self.run_prepare()
        self.assertEqual(self.remote_head(), newer)

    def test_dirty_checkout_is_rejected_before_any_writeback(self):
        (self.root / 'skill.md').write_text('uncommitted\n')
        with self.assertRaisesRegex(ValueError, '工作区'):
            self.run_prepare()
        self.assertEqual(self.remote_head(), self.source)

    def test_version_behind_known_tags_is_rejected(self):
        self.git('tag', 'v0.4.0')
        with self.assertRaisesRegex(ValueError, '版本'):
            self.run_prepare()
        self.assertEqual(self.remote_head(), self.source)

    def test_non_push_or_non_main_invocation_is_read_only(self):
        for field, value in [('GITHUB_EVENT_NAME', 'pull_request'), ('GITHUB_EVENT_NAME', 'workflow_dispatch'),
                             ('GITHUB_REF', 'refs/tags/v0.3.3'), ('GITHUB_ACTIONS', 'false')]:
            with self.subTest(field=field, value=value):
                context = {**self.context, field: value}
                self.assertEqual(prepare(self.root, context, self.validate)['status'], 'not-main-push')
        self.assertEqual(self.validated, [])
        self.assertEqual(self.remote_head(), self.source)


if __name__ == '__main__':
    unittest.main()
