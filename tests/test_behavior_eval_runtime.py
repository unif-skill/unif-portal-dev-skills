"""Request retries must preserve frozen inputs, trace evidence and global limits."""

import io
import hashlib
import json
import threading
import tempfile
import unittest
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from email.message import Message as Headers
from pathlib import Path
from unittest.mock import patch

from scripts import behavior_eval as evaluator
from scripts import sync_evaluation_tools as sync


ENV = {'SKILL_EVAL_ENABLED': 'true', 'SKILL_EVAL_MODEL': 'test-model',
       'SKILL_EVAL_MAX_REQUESTS': '100', 'UNIF_MODEL_API_KEY': 'synthetic-test-key',
       'UNIF_MODEL_BASE_URL': 'https://example.invalid/v1'}


def client(**extra: str) -> evaluator.ChatCompletionsClient:
    return evaluator.ChatCompletionsClient(evaluator.configuration(ENV | extra))


def response(text: str = 'answer', finish_reason: str = 'stop') -> evaluator.Response:
    return {'model': 'test-model', 'choices': [{'finish_reason': finish_reason,
            'message': {'role': 'assistant', 'content': text}}],
            'usage': {'prompt_tokens': 20, 'completion_tokens': 5, 'total_tokens': 25}}


def failure(status: int = 503) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(ENV['UNIF_MODEL_BASE_URL'] + '/chat/completions', status,
        'unsafe body must not enter trace', Headers(), io.BytesIO(b'private response body'))


def fake_http(replies: Sequence[evaluator.Response | Exception], requests: list[urllib.request.Request],
              timeouts: list[int]) -> Callable[..., io.BytesIO]:
    remaining = iter(replies)

    def send(request: urllib.request.Request, timeout: int) -> io.BytesIO:
        requests.append(request)
        timeouts.append(timeout)
        item = next(remaining)
        if isinstance(item, Exception):
            raise item
        return io.BytesIO(json.dumps(item).encode())
    return send


class TransportTests(unittest.TestCase):
    def test_retry_preserves_request_and_usage_evidence(self) -> None:
        api = client()
        requests: list[urllib.request.Request] = []
        timeouts: list[int] = []
        delays: list[float] = []
        unavailable = failure()
        case: evaluator.Case = {'id': 'sample-discovery', 'skill': 'sample', 'mode': 'discovery_positive',
            'prompt': 'Select the sample skill.', 'source': 'evals/example.md', 'rubric': ['Select sample.'],
            'fixtures': {}, 'required_skills': ['sample'], 'forbidden_skills': []}
        replies = [unavailable, response('{"selected_skills":["sample"],"reason":"Matches."}')]
        with patch('urllib.request.urlopen', side_effect=fake_http(replies, requests, timeouts)), patch(
                'scripts.behavior_eval.time.sleep', side_effect=delays.append):
            result = evaluator.evaluate_sample(api, case, {}, [{'name': 'sample', 'description': 'Use sample.'}], 'sha')
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['scores'], [True])
        self.assertEqual(api.requests_used, 2)
        self.assertEqual(delays, [1])
        self.assertEqual(requests[0].data, requests[1].data)
        self.assertEqual(result['usage'], {'prompt_tokens': 20, 'completion_tokens': 5, 'total_tokens': 25})
        self.assertFalse(result['usage_complete'])
        trace = result['api_trace']
        self.assertEqual([row.get('attempt') for row in trace], [1, 2])
        self.assertEqual(trace[0].get('error'), 'HTTP 503')
        self.assertIn('response', trace[1])
        self.assertNotIn('private response body', json.dumps(trace))
        self.assertNotIn('synthetic-test-key', json.dumps(trace))
        self.assertNotIn('unsafe body', json.dumps(trace))
        self.assertTrue(unavailable.closed)
        self.assertIsNone(api.transport_error)

    def test_two_retries_succeed_and_exhaustion_stops_later_calls(self) -> None:
        for succeeds in (True, False):
            with self.subTest(succeeds=succeeds):
                api = client()
                requests: list[urllib.request.Request] = []
                delays: list[float] = []
                trace: list[evaluator.ApiTrace] = []
                replies: list[evaluator.Response | Exception] = [failure(), failure(), response() if succeeds else failure()]
                with patch('urllib.request.urlopen', side_effect=fake_http(replies, requests, [])), patch(
                        'scripts.behavior_eval.time.sleep', side_effect=delays.append):
                    if succeeds:
                        self.assertEqual(evaluator.response_text(api.request([{'role': 'user', 'content': 'task'}], trace)), 'answer')
                    else:
                        with self.assertRaisesRegex(evaluator.EvalError, 'API 传输失败：HTTP 503'):
                            _ = api.request([{'role': 'user', 'content': 'task'}], trace)
                        with self.assertRaisesRegex(evaluator.EvalError, '先前 API 传输失败'):
                            _ = api.request([{'role': 'user', 'content': 'task'}], [])
                self.assertEqual(api.requests_used, 3)
                self.assertEqual(len(requests), 3)
                self.assertEqual(len(trace), 3)
                self.assertEqual(delays, [1, 2])

    def test_configured_backoff_remains_bounded(self) -> None:
        api = client(SKILL_EVAL_RETRY_BASE_SECONDS='15', SKILL_EVAL_MAX_WORKERS='1')
        requests: list[urllib.request.Request] = []
        delays: list[float] = []
        with patch('urllib.request.urlopen', side_effect=fake_http([failure(), failure(), response()], requests, [])), patch(
                'scripts.behavior_eval.time.sleep', side_effect=delays.append):
            _ = api.request([{'role': 'user', 'content': 'task'}], [])
        self.assertEqual(delays, [15, 30])
        self.assertEqual(api.requests_used, 3)
        self.assertEqual(api.config['max_workers'], 1)
        for value in ('0', '31'):
            with self.subTest(value=value), self.assertRaises(evaluator.EvalError):
                _ = client(SKILL_EVAL_RETRY_BASE_SECONDS=value)

    def test_retry_cannot_exceed_remaining_budget(self) -> None:
        api = client(SKILL_EVAL_MAX_REQUESTS='1')
        requests: list[urllib.request.Request] = []
        with patch('urllib.request.urlopen', side_effect=fake_http([failure()], requests, [])), patch(
                'scripts.behavior_eval.time.sleep'):
            with self.assertRaisesRegex(evaluator.EvalError, '预算已耗尽'):
                _ = api.request([{'role': 'user', 'content': 'task'}], [])
        self.assertEqual(api.requests_used, 1)
        self.assertEqual(len(requests), 1)

    def test_concurrent_retries_share_the_atomic_budget(self) -> None:
        api = client(SKILL_EVAL_MAX_REQUESTS='3')
        barrier, lock = threading.Barrier(2), threading.Lock()
        calls = 0

        def send(request: urllib.request.Request, timeout: int) -> io.BytesIO:
            nonlocal calls
            self.assertEqual(request.full_url, ENV['UNIF_MODEL_BASE_URL'] + '/chat/completions')
            self.assertGreater(timeout, 0)
            with lock:
                calls += 1
                first = calls <= 2
            if first:
                _ = barrier.wait(timeout=2)
            raise failure()

        def request_once(index: int) -> str:
            try:
                _ = api.request([{'role': 'user', 'content': str(index)}], [])
                return 'unexpected success'
            except evaluator.EvalError as exc:
                return str(exc)

        with patch('urllib.request.urlopen', side_effect=send), patch('scripts.behavior_eval.time.sleep'), ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(request_once, range(2)))
        self.assertEqual(calls, 3)
        self.assertEqual(api.requests_used, 3)
        self.assertTrue(all('预算已耗尽' in result for result in outcomes))

    def test_another_workers_permanent_failure_prevents_retry(self) -> None:
        api = client()
        requests: list[urllib.request.Request] = []

        def during_backoff(delay: float) -> None:
            self.assertEqual(delay, 1)
            with self.assertRaisesRegex(evaluator.EvalError, 'API 传输失败：HTTP 401'):
                _ = api.request([{'role': 'user', 'content': 'other worker'}], [])

        with patch('urllib.request.urlopen', side_effect=fake_http([failure(), failure(401)], requests, [])), patch(
                'scripts.behavior_eval.time.sleep', side_effect=during_backoff):
            with self.assertRaisesRegex(evaluator.EvalError, '先前 API 传输失败，本次停止调用：HTTP 401'):
                _ = api.request([{'role': 'user', 'content': 'task'}], [])
        self.assertEqual(len(requests), 2)
        self.assertEqual(api.requests_used, 2)

    def test_truncation_and_permanent_failures_are_not_retried(self) -> None:
        for item in (response('partial', 'length'), failure(401), failure(429), failure(500), TimeoutError()):
            with self.subTest(item=type(item).__name__):
                api = client()
                requests: list[urllib.request.Request] = []
                delays: list[float] = []
                with patch('urllib.request.urlopen', side_effect=fake_http([item], requests, [])), patch(
                        'scripts.behavior_eval.time.sleep', side_effect=delays.append):
                    with self.assertRaises(evaluator.EvalError):
                        _ = api.request([{'role': 'user', 'content': 'task'}], [])
                self.assertEqual(len(requests), 1)
                self.assertEqual(delays, [])

    def test_output_and_timeout_configuration_reaches_http_request(self) -> None:
        api = client(SKILL_EVAL_MAX_OUTPUT_TOKENS='16384', SKILL_EVAL_TIMEOUT_SECONDS='300')
        requests: list[urllib.request.Request] = []
        timeouts: list[int] = []
        with patch('urllib.request.urlopen', side_effect=fake_http([response()], requests, timeouts)):
            _ = api.request([{'role': 'user', 'content': 'task'}], [])
        data = requests[0].data
        if not isinstance(data, bytes):
            self.fail('HTTP request has no serialized payload')
        payload = evaluator.load_json(data)
        if not evaluator.is_object(payload):
            self.fail('HTTP request payload is not an object')
        self.assertEqual(payload['max_tokens'], 16384)
        self.assertEqual(timeouts, [300])
        for extra in ({'SKILL_EVAL_TIMEOUT_SECONDS': '301'}, {'SKILL_EVAL_TIMEOUT_SECONDS': '0'},
                      {'SKILL_EVAL_MAX_OUTPUT_TOKENS': '16385'}, {'SKILL_EVAL_MAX_OUTPUT_TOKENS': '127'}):
            with self.subTest(extra=extra), self.assertRaises(evaluator.EvalError):
                _ = client(**extra)


def legacy_adoption(root: Path) -> tuple[Path, Path]:
    source, target = root / 'source', root / 'target'
    for path, name in ((source, 'uni-skills'), (target, 'unif-portal-dev-skills')):
        path.mkdir()
        _ = (path / 'plugin.json').write_text(json.dumps({'name': name}))
    digests: dict[str, str] = {}
    for name in sync.FILES:
        source_file = source / name
        source_file.parent.mkdir(parents=True, exist_ok=True)
        _ = source_file.write_text('new source ' + name)
    for name in sync.PREVIOUS_FILES:
        target_file = target / name
        target_file.parent.mkdir(parents=True, exist_ok=True)
        content = ('published source ' + name).encode()
        _ = target_file.write_bytes(content)
        digests[name] = hashlib.sha256(content).hexdigest()
    _ = (target / sync.RECORD).write_text(json.dumps({'formatVersion': 1, 'source': sync.SOURCE, 'files': digests}))
    return source, target


def files_snapshot(root: Path) -> dict[str, bytes]:
    return {str(path.relative_to(root)): path.read_bytes() for path in root.rglob('*') if path.is_file()}


class RuntimeAdoptionTests(unittest.TestCase):
    def test_published_five_file_record_requires_explicit_upgrade(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source, target = legacy_adoption(Path(temporary))
            with self.assertRaises(ValueError):
                _ = sync.check_evaluation_tools(target)
            before = files_snapshot(target)
            with self.assertRaises(ValueError):
                sync.sync_evaluation_tools(source, target, check=True)
            self.assertEqual(before, files_snapshot(target))
            sync.sync_evaluation_tools(source, target)
            record = sync.check_evaluation_tools(target)
            if record is None:
                self.fail('Consumer adoption record is missing')
            self.assertEqual(set(record['files']), set(sync.FILES))
            for name in sync.FILES:
                self.assertEqual((target / name).read_bytes(), (source / name).read_bytes())
            sync.sync_evaluation_tools(source, target, check=True)

    def test_upgrade_preserves_unmanaged_or_modified_files(self) -> None:
        for filename in ('tests/test_behavior_eval_runtime.py', sync.PREVIOUS_FILES[0]):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temporary:
                source, target = legacy_adoption(Path(temporary))
                _ = (target / filename).write_text('user work')
                before = files_snapshot(target)
                with self.assertRaises(ValueError):
                    sync.sync_evaluation_tools(source, target)
                self.assertEqual(before, files_snapshot(target))


if __name__ == '__main__':
    _ = unittest.main()
