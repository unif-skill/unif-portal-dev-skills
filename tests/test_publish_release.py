import io
import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from unittest.mock import patch

from scripts.publish_release import GitHub, publish

SHA = 'a' * 40
OTHER = 'b' * 40
CONTEXT = {
    'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'push',
    'GITHUB_REF': 'refs/heads/main', 'GITHUB_SHA': SHA,
}


class FakeGitHub:
    def __init__(self, responses=None, failure=None):
        self.responses = {
            'git/ref/heads/main': {'object': {'sha': SHA}},
            'releases?per_page=100&page=1': [],
        }
        self.responses.update(responses or {})
        self.failure = failure
        self.calls = []

    def get(self, path, *, missing_ok=False):
        self.calls.append(('GET', path))
        if path in self.responses:
            return self.responses[path]
        if path.startswith('commits/refs%2Ftags%2F'):
            raise HTTPError('https://api.github.com/' + path, 422, 'No commit found for SHA', {}, io.BytesIO())
        if missing_ok:
            return None
        raise AssertionError(f'unexpected GET {path}')

    def post(self, path, payload):
        self.calls.append(('POST', path, payload))
        if self.failure:
            raise self.failure
        tag = payload['tag_name']
        commit = payload['target_commitish']
        if commit == 'main':
            commit = self.responses['git/ref/heads/main']['object']['sha']
        self.responses[f'commits/refs%2Ftags%2F{tag}'] = {'sha': commit}
        self.responses[f'git/ref/tags/{tag}'] = {'object': {'type': 'commit', 'sha': commit}}
        result = {'tag_name': tag, 'draft': False, 'html_url': f'https://github.com/example/repo/releases/tag/{tag}'}
        self.responses['releases?per_page=100&page=1'] = [result]
        return result


class PublishTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.manifest = self.root / 'plugin.json'
        self.version('0.1.0')

    def version(self, value):
        self.manifest.write_text(json.dumps({'version': value}))

    def test_new_zero_major_release_targets_validated_commit_and_does_not_edit_manifest(self):
        api = FakeGitHub()
        before = self.manifest.read_bytes()
        result = publish(self.root, CONTEXT, api)
        self.assertEqual(result['status'], 'published')
        self.assertEqual(result['tag'], 'v0.1.0')
        self.assertEqual(api.calls, [
            ('GET', 'git/ref/heads/main'),
            ('GET', 'releases?per_page=100&page=1'),
            ('GET', 'git/ref/tags/v0.1.0'),
            ('POST', 'releases', {
                'tag_name': 'v0.1.0', 'target_commitish': SHA, 'name': 'v0.1.0',
                'draft': False, 'prerelease': False, 'generate_release_notes': True,
            }),
            ('GET', 'commits/refs%2Ftags%2Fv0.1.0'),
        ])
        self.assertEqual(self.manifest.read_bytes(), before)

    def test_one_major_release_uses_validated_commit(self):
        self.version('1.0.0')
        result = publish(self.root, CONTEXT, FakeGitHub())
        self.assertEqual(result['tag'], 'v1.0.0')

    def test_repeat_run_does_not_publish_again(self):
        api = FakeGitHub()
        publish(self.root, CONTEXT, api)
        self.assertEqual(publish(self.root, CONTEXT, api)['status'], 'already-published')
        self.assertEqual(sum(call[0] == 'POST' for call in api.calls), 1)

    def test_pull_request_tag_manual_dispatch_and_local_invocations_never_publish(self):
        for field, value in [('GITHUB_EVENT_NAME', 'pull_request'), ('GITHUB_EVENT_NAME', 'workflow_dispatch'),
                             ('GITHUB_REF', 'refs/tags/v0.1.0'), ('GITHUB_REF', 'refs/heads/topic'),
                             ('GITHUB_ACTIONS', 'false')]:
            with self.subTest(field=field, value=value):
                api = FakeGitHub()
                self.assertEqual(publish(self.root, {**CONTEXT, field: value}, api)['status'], 'not-main-push')
                self.assertEqual(api.calls, [])

    def test_unapproved_major_is_rejected_without_api_access(self):
        for version in ('2.0.0', '3.0.1'):
            with self.subTest(version=version):
                self.version(version)
                api = FakeGitHub()
                with self.assertRaisesRegex(ValueError, '主版本'):
                    publish(self.root, CONTEXT, api)
                self.assertEqual(api.calls, [])

    def test_generated_release_commit_is_used_instead_of_source_commit(self):
        api = FakeGitHub({'git/ref/heads/main': {'object': {'sha': OTHER}}})
        result = publish(self.root, {**CONTEXT, 'RELEASE_SHA': OTHER}, api)
        self.assertEqual(result['status'], 'published')
        posts = [call for call in api.calls if call[0] == 'POST']
        self.assertEqual(posts[0][2]['target_commitish'], OTHER)

    def test_published_release_must_still_point_to_the_validated_commit(self):
        api = FakeGitHub({
            'releases?per_page=100&page=1': [
                {'tag_name': 'v0.1.0', 'draft': False, 'html_url': 'https://example.test/release'},
            ],
            'commits/refs%2Ftags%2Fv0.1.0': {'sha': OTHER},
        })
        with self.assertRaisesRegex(ValueError, 'tag'):
            publish(self.root, CONTEXT, api)
        self.assertFalse(any(call[0] == 'POST' for call in api.calls))

    def test_invalid_version_or_commit_is_rejected_before_api_access(self):
        for version in ('0.1', '00.1.0', 'v0.1.0', '0.1.0+local', '0.1.0;bad'):
            with self.subTest(version=version):
                self.version(version)
                api = FakeGitHub()
                with self.assertRaises(ValueError):
                    publish(self.root, CONTEXT, api)
                self.assertEqual(api.calls, [])
        self.version('0.1.0')
        api = FakeGitHub()
        with self.assertRaises(ValueError):
            publish(self.root, {**CONTEXT, 'GITHUB_SHA': 'main'}, api)
        self.assertEqual(api.calls, [])

    def test_superseded_main_commit_is_not_released(self):
        api = FakeGitHub({'git/ref/heads/main': {'object': {'sha': OTHER}}})
        self.assertEqual(publish(self.root, CONTEXT, api)['status'], 'superseded')
        self.assertEqual(api.calls, [('GET', 'git/ref/heads/main')])

    def test_existing_tag_can_recover_release_only_at_the_same_commit(self):
        tag_object = {'object': {'type': 'tag', 'sha': 'c' * 40}}
        api = FakeGitHub({'git/ref/tags/v0.1.0': tag_object, 'commits/refs%2Ftags%2Fv0.1.0': {'sha': SHA}})
        self.assertEqual(publish(self.root, CONTEXT, api)['status'], 'published')
        conflict = FakeGitHub({'git/ref/tags/v0.1.0': tag_object, 'commits/refs%2Ftags%2Fv0.1.0': {'sha': OTHER}})
        with self.assertRaisesRegex(ValueError, 'tag'):
            publish(self.root, CONTEXT, conflict)
        self.assertFalse(any(call[0] == 'POST' for call in conflict.calls))

    def test_existing_draft_is_not_silently_published(self):
        api = FakeGitHub({'releases?per_page=100&page=1': [{'tag_name': 'v0.1.0', 'draft': True}]})
        with self.assertRaisesRegex(ValueError, 'draft'):
            publish(self.root, CONTEXT, api)
        self.assertFalse(any(call[0] == 'POST' for call in api.calls))

    def test_all_release_pages_are_checked_before_creating(self):
        api = FakeGitHub({
            'releases?per_page=100&page=1': [{'tag_name': f'v0.0.{n}'} for n in range(100)],
            'releases?per_page=100&page=2': [
                {'tag_name': 'v0.1.0', 'draft': False, 'html_url': 'https://github.com/example/repo/releases/tag/v0.1.0'},
            ],
            'commits/refs%2Ftags%2Fv0.1.0': {'sha': SHA},
        })
        self.assertEqual(publish(self.root, CONTEXT, api)['status'], 'already-published')
        self.assertIn(('GET', 'releases?per_page=100&page=2'), api.calls)
        self.assertFalse(any(call[0] == 'POST' for call in api.calls))

    def test_failed_publication_is_not_retried(self):
        api = FakeGitHub(failure=OSError('synthetic transport failure'))
        with self.assertRaisesRegex(OSError, 'synthetic'):
            publish(self.root, CONTEXT, api)
        self.assertEqual(sum(call[0] == 'POST' for call in api.calls), 1)

    def test_created_tag_must_resolve_to_validated_commit(self):
        class ConflictingTag(FakeGitHub):
            def post(self, path, payload):
                result = super().post(path, payload)
                self.responses['commits/refs%2Ftags%2Fv0.1.0'] = {'sha': OTHER}
                return result
        with self.assertRaisesRegex(ValueError, 'tag'):
            publish(self.root, CONTEXT, ConflictingTag())


class GitHubTransportTests(unittest.TestCase):
    @patch('scripts.publish_release.urlopen')
    def test_get_only_treats_optional_404_as_missing(self, opener):
        api = GitHub('example/repo', 'synthetic-token')
        for status, missing_ok in ((404, True), (404, False), (403, True), (500, True)):
            with self.subTest(status=status, missing_ok=missing_ok):
                body = io.BytesIO(b'{"message":"synthetic"}')
                error = HTTPError('https://api.github.com/example', status, 'synthetic', {}, body)
                self.addCleanup(error.close)
                opener.side_effect = error
                if status == 404 and missing_ok:
                    self.assertIsNone(api.get('releases/tags/v0.1.0', missing_ok=True))
                else:
                    with self.assertRaises(HTTPError):
                        api.get('releases/tags/v0.1.0', missing_ok=missing_ok)
                self.assertTrue(body.closed)

    @patch('scripts.publish_release.urlopen')
    def test_release_post_sends_authenticated_json_once(self, opener):
        opener.return_value = io.BytesIO(b'{"id":1}')
        api = GitHub('example/repo', 'synthetic-token')
        self.assertEqual(api.post('releases', {'tag_name': 'v0.1.0'}), {'id': 1})
        request = opener.call_args.args[0]
        self.assertEqual(request.full_url, 'https://api.github.com/repos/example/repo/releases')
        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.get_header('Authorization'), 'Bearer synthetic-token')
        self.assertEqual(json.loads(request.data), {'tag_name': 'v0.1.0'})
        self.assertEqual(opener.call_count, 1)


if __name__ == '__main__':
    unittest.main()
