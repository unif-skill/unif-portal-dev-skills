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


class ProgressTests(unittest.TestCase):
    def test_live_pairs_precede_later_requests_and_preserve_results(self) -> None:
        case: evaluator.Case = {'id': 'sample-discovery', 'skill': 'sample', 'mode': 'discovery_positive',
            'prompt': 'Select sample.', 'source': 'evals/example.md', 'rubric': ['Select sample.'],
            'fixtures': {}, 'required_skills': ['sample'], 'forbidden_skills': []}
        with patch('scripts.behavior_eval.resolve_commit', return_value='a' * 40), patch(
                'scripts.behavior_eval.git', return_value=b''):
            snapshot = evaluator.Snapshot('.', 'HEAD')
        plan: evaluator.Plan = {'formatVersion': 1, 'repo': str(snapshot.repo), 'base': 'a' * 40,
            'head': 'a' * 40, 'mode': 'smoke', 'case_ids': [case['id']], 'repeats': 1, 'suite_sha256': 'b' * 64}
        observations: list[tuple[evaluator.CaseReport, list[bytes | None]]] = []
        for enabled in (False, True):
            progress = evaluator.Progress(enabled, 2)
            api = evaluator.ChatCompletionsClient(evaluator.configuration(ENV), progress)
            logs = io.StringIO()
            sent: list[bytes | None] = []
            with tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary)

                def send(request: urllib.request.Request, timeout: int) -> io.BytesIO:
                    self.assertGreater(timeout, 0)
                    if len(sent) == 2 and enabled:
                        self.assertIn('已处理 1/2', logs.getvalue())
                        self.assertTrue((output / 'traces/sample-discovery/1-after.json').is_file())
                    data = request.data
                    if not isinstance(data, bytes):
                        self.fail("Request payload must be serialized bytes")
                    sent.append(data)
                    return io.BytesIO(json.dumps(response('{"selected_skills":["sample"],"reason":"Matches."}')).encode())

                reports: list[evaluator.CaseReport] = []
                with patch('sys.stderr', logs), patch('urllib.request.urlopen', side_effect=send), patch.object(
                        evaluator.Snapshot, 'skill_files', return_value={'skills/sample/SKILL.md': b'skill'}):
                    for _ in range(2):
                        report: evaluator.CaseReport = {'id': case['id'], 'skill': case['skill'], 'mode': case['mode'],
                            'source': case['source'], 'rubric': case['rubric'], 'status': 'insufficient',
                            'expected_pairs': 1, 'failures': [], 'traces': []}
                        reports.append(evaluator.evaluate_case(report, case, api, {'before': snapshot, 'after': snapshot},
                            {variant: [{'name': 'sample', 'description': 'Select sample.'}] for variant in ('before', 'after')},
                            plan, output, 'harness'))
                        self.assertEqual(report.get('completed_pairs'), 1)
                        self.assertEqual(report['failures'], [])
                observations.append((reports[-1], sent))
            if enabled:
                self.assertIn('已处理 2/2', logs.getvalue())
                self.assertIn('题目 sample-discovery 结束：证据不足', logs.getvalue())
                self.assertIn('单对观察，非最终结论', logs.getvalue())
            else:
                self.assertEqual(logs.getvalue(), '')
        self.assertEqual(observations[0], observations[1])

    def test_concurrent_progress_counts_each_pair_once(self) -> None:
        logs = io.StringIO()
        progress = evaluator.Progress(True, 30)
        comparison: evaluator.Comparison = {'status': 'insufficient', 'completed_pairs': 1,
            'expected_pairs': 1, 'criteria': [], 'observed_wins': 0, 'observed_losses': 0}

        def finish(index: int) -> None:
            progress.pair_finished('sample', index, comparison, 1)

        with patch('sys.stderr', logs), ThreadPoolExecutor(max_workers=3) as pool:
            _ = list(pool.map(finish, range(30)))
        self.assertEqual(progress.processed_pairs, 30)
        self.assertEqual(progress.completed_pairs, 30)
        self.assertEqual(len(logs.getvalue().splitlines()), 30)
        self.assertIn('已处理 30/30', logs.getvalue())

    def test_incomparable_pairs_do_not_claim_zero_differences(self) -> None:
        before: evaluator.ComparableSample = {'status': 'complete', 'scores': [True],
            'actual_models': {'answer': ['model-a']}, 'case_sha256': 'same-case'}
        for status in ('complete', 'error'):
            candidate: evaluator.ComparableSample = {'status': status, 'scores': [True],
                'actual_models': {'answer': ['model-b']}, 'case_sha256': 'same-case'}
            comparison = evaluator.compare_results([(before, candidate)], 1)
            logs = io.StringIO()
            with patch('sys.stderr', logs):
                evaluator.Progress(True, 1).pair_finished('sample', 1, comparison, 0)
            self.assertIn('不可比较', logs.getvalue())
            self.assertNotIn('观察上升/下降 0/0', logs.getvalue())

    def test_actual_errors_exclude_stop_notices_and_logs_exclude_payloads(self) -> None:
        logs = io.StringIO()
        api = evaluator.ChatCompletionsClient(evaluator.configuration(ENV), evaluator.Progress(True, 1))
        with patch('sys.stderr', logs), patch('urllib.request.urlopen', side_effect=fake_http(
                [failure(), failure(), failure()], [], [])), patch('scripts.behavior_eval.time.sleep'):
            for _ in range(4):
                with self.assertRaises(evaluator.EvalError):
                    _ = api.request([{'role': 'user', 'content': 'secret prompt'}], [])
        self.assertEqual(api.request_errors, {'HTTP 503': 3})
        self.assertEqual(api.requests_used, 3)
        self.assertEqual(logs.getvalue().count('传输失败 HTTP 503'), 3)
        for secret in ('secret prompt', 'private response body', 'synthetic-test-key', 'example.invalid'):
            self.assertNotIn(secret, logs.getvalue())

    def test_closed_log_stream_does_not_change_http_result(self) -> None:
        logs = io.StringIO()
        logs.close()
        api = evaluator.ChatCompletionsClient(evaluator.configuration(ENV), evaluator.Progress(True, 1))
        with patch('sys.stderr', logs), patch('urllib.request.urlopen', side_effect=fake_http([response()], [], [])):
            self.assertEqual(api.request([{'role': 'user', 'content': 'task'}], []), response())

    def test_repeated_errors_group_only_in_markdown(self) -> None:
        error = '先前 API 传输失败，本次停止调用：HTTP 503'
        failures: list[evaluator.Failure] = [{'error': error, 'variant': 'after', 'repeat': i,
            'trace': f'traces/sample/{i}-after.json'} for i in range(1, 4)]
        case: evaluator.CaseReport = {'id': 'sample', 'skill': 'sample', 'mode': 'application',
            'source': 'example', 'rubric': [], 'status': 'insufficient', 'expected_pairs': 3,
            'failures': failures, 'traces': []}
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            evaluator.write_report(output, {'status': 'insufficient', 'cases': [case], 'request_errors': {'HTTP 503': 3}})
            markdown = (output / 'summary.md').read_text()
            raw = (output / 'summary.json').read_text()
        self.assertEqual(markdown.count(error), 1)
        self.assertEqual(raw.count(error), 3)
        self.assertIn('共 3 个样本提示', markdown)
        self.assertIn('实际请求传输错误', markdown)


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


class PluginLayoutTests(unittest.TestCase):
    def test_old_and_direct_package_layouts_expose_the_same_virtual_skill_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _ = evaluator.git(root, 'init', '-q')
            _ = evaluator.git(root, 'config', 'user.name', 'Test')
            _ = evaluator.git(root, 'config', 'user.email', 'test@example.invalid')

            def put(path: str, body: str) -> None:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                _ = target.write_text(body, encoding='utf-8')

            def save() -> str:
                _ = evaluator.git(root, 'add', '.')
                _ = evaluator.git(root, 'commit', '-qm', 'layout')
                return evaluator.resolve_commit(root, 'HEAD')

            def market(*names: str) -> None:
                entries = [{'name': name, 'source': {'source': 'local', 'path': './plugins/' + name}}
                           for name in names]
                put(evaluator.MARKETPLACE_PATH, json.dumps({'plugins': entries}))

            cases: list[dict[str, object]] = []
            for skill in ('dev', 'review', 'other'):
                put(f'skills/{skill}/SKILL.md',
                    f'---\nname: {skill}\ndescription: applies to {skill}\n---\n')
                for mode in evaluator.CASE_MODES:
                    cases.append({'id': f'{skill}-{mode}', 'skill': skill, 'mode': mode, 'prompt': 'test',
                                  'fixtures': {}, 'source': 'fixture', 'rubric': ['correct'],
                                  'required_skills': [skill] if mode == 'discovery_positive' else [],
                                  'forbidden_skills': [skill] if mode == 'discovery_negative' else []})
            put(evaluator.SUITE_PATH, json.dumps({'formatVersion': 1, 'cases': cases}))
            market('one', 'two')
            put('plugins/one/skills/review/SKILL.md', 'historical mirror')
            old = save()
            baseline = evaluator.Snapshot(root, old)
            self.assertEqual(baseline.skill_dir('review'), 'skills/review')
            for skill, package in (('dev', 'one'), ('review', 'one'), ('other', 'two')):
                name = f'plugins/{package}/skills/{skill}/SKILL.md'
                put(name, (root / f'skills/{skill}/SKILL.md').read_text())
            _ = evaluator.git(root, 'rm', '-qr', 'skills')
            review_entry = 'plugins/one/skills/review/SKILL.md'
            with (root / review_entry).open('a', encoding='utf-8') as stream:
                _ = stream.write('[shared](../dev/references/state.md#x)')
            put('plugins/one/skills/dev/references/private.md', 'not requested')
            shared = 'plugins/one/skills/dev/references/state.md'
            put(shared, 'provided')
            candidate = save()
            self.assertEqual(len(evaluator.validate(root)), 9)
            self.assertEqual(len(evaluator.create_plan(root, old, candidate, 'smoke', 'push')['case_ids']), 9)
            snapshot = evaluator.Snapshot(root, candidate)
            self.assertEqual(snapshot.skill_names(), ['dev', 'other', 'review'])
            files = snapshot.skill_files('review')
            self.assertEqual(set(files), {'skills/review/SKILL.md', 'skills/dev/references/state.md'})
            sandbox = evaluator.ReadOnlyFiles('review', files, {})
            self.assertEqual(sandbox.call('read_file', {'path': 'skills/dev/references/state.md'})['content'], 'provided')
            with self.assertRaises(evaluator.EvalError):
                _ = sandbox.call('read_file', {'path': 'skills/dev/references/private.md'})
            put(shared, 'updated')
            changed = save()
            selected = evaluator.create_plan(root, candidate, changed, 'smoke', 'push')['case_ids']
            self.assertEqual(set(selected), {f'{name}-{mode}' for name in ('dev', 'review') for mode in evaluator.CASE_MODES})
            with (root / review_entry).open('a', encoding='utf-8') as stream:
                _ = stream.write('[bad](../other/references/bad.md)')
            with self.assertRaisesRegex(evaluator.EvalError, '同一插件'):
                _ = evaluator.validate(root)
            with self.assertRaisesRegex(evaluator.EvalError, '同一插件'):
                _ = evaluator.Snapshot(root, save()).skill_files('review')
            put('plugins/two/skills/dev/SKILL.md', 'duplicate')
            with self.assertRaisesRegex(evaluator.EvalError, '同名技能'):
                _ = evaluator.validate(root)
            with self.assertRaisesRegex(evaluator.EvalError, '同名技能'):
                _ = evaluator.Snapshot(root, save()).skill_names()


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
