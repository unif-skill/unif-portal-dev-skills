import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from scripts import behavior_eval as evaluator


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/behavior_eval.py'


def example_case(skill='sample', mode='application'):
    return {
        'id': f'{skill}-{mode}', 'skill': skill, 'mode': mode,
        'prompt': 'Read the given project and explain the authorized change.',
        'fixtures': {'project.txt': 'Only change the selected entry.'},
        'rubric': ['Preserves the scope.'],
        'required_skills': [skill] if mode == 'discovery_positive' else [],
        'forbidden_skills': [skill] if mode == 'discovery_negative' else [],
        'source': 'evals/existing.md#example',
    }


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        self.write('plugin.json', json.dumps({'name': 'example', 'version': '0.1.0'}))
        self.cases = []
        for skill in ('sample', 'second'):
            self.write(f'skills/{skill}/SKILL.md',
                       f'---\nname: {skill}\ndescription: Use for {skill}.\n---\nBody secret: {skill}\n')
            for mode in ('application', 'discovery_positive', 'discovery_negative'):
                self.cases.append(example_case(skill, mode))
        self.write_suite()
        self.base = self.commit('chore: baseline')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], text=True).strip()

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')

    def write_suite(self):
        self.write('evals/behavior/cases.json', json.dumps({'formatVersion': 1, 'cases': self.cases}))

    def commit(self, message):
        self.git('add', '.')
        self.git('commit', '-qm', message)
        return self.git('rev-parse', 'HEAD')

    def cli(self, *args, env=None):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.root,
                              env={} if env is None else env, capture_output=True, text=True)

    def plan(self, mode='auto', event='pull_request'):
        target = self.root / 'plan.json'
        result = self.cli('plan', '--repo', str(self.root), '--base', self.base,
                          '--head', 'HEAD', '--mode', mode, '--event', event,
                          '--output', str(target))
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return json.loads(target.read_text())

    def test_validate_accepts_self_contained_cases(self):
        result = self.cli('validate', '--root', str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_validate_requires_each_mode_for_every_skill(self):
        original = copy.deepcopy(self.cases)
        for missing_mode in ('application', 'discovery_positive', 'discovery_negative'):
            with self.subTest(missing_mode=missing_mode):
                self.cases = [case for case in original
                              if not (case['skill'] == 'sample' and case['mode'] == missing_mode)]
                self.write_suite()
                result = self.cli('validate', '--root', str(self.root))
                self.assertEqual(result.returncode, 2)
                self.assertIn(missing_mode, result.stderr)
        self.cases = [case for case in original if case['mode'] == 'discovery_positive']
        self.write_suite()
        self.assertEqual(self.cli('validate', '--root', str(self.root)).returncode, 2)

    def test_validate_rejects_traversal_duplicates_and_unknown_skills(self):
        original = copy.deepcopy(self.cases)
        mutations = [
            lambda: self.cases[0]['fixtures'].update({'../outside': 'secret'}),
            lambda: self.cases.append(copy.deepcopy(self.cases[0])),
            lambda: self.cases[0].update(skill='missing'),
            lambda: self.cases[0].update(rubric=[]),
            lambda: self.cases[1].update(forbidden_skills=['sample']),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.cases = copy.deepcopy(original)
                mutation()
                self.write_suite()
                result = self.cli('validate', '--root', str(self.root))
                self.assertEqual(result.returncode, 2)

    def test_validate_rejects_symbolic_links_inside_skill(self):
        (self.root / 'skills/sample/escape').symlink_to('/etc/hosts')
        self.assertEqual(self.cli('validate', '--root', str(self.root)).returncode, 2)

    def test_plan_selects_changed_skill_and_resolves_commits(self):
        self.write('skills/sample/references/details.md', 'New instructions')
        head = self.commit('fix: sample')
        plan = self.plan()
        self.assertEqual(plan['formatVersion'], 1)
        self.assertEqual(plan['repo'], str(self.root.resolve()))
        self.assertEqual((plan['base'], plan['head']), (self.base, head))
        self.assertEqual(plan['mode'], 'smoke')
        self.assertEqual(plan['repeats'], 1)
        self.assertEqual(set(plan['case_ids']), {case['id'] for case in self.cases[:3]})
        self.assertEqual(len(plan['suite_sha256']), 64)

    def test_plan_uses_committed_suite_and_skips_unrelated_changes(self):
        self.write('README.md', 'Only project prose')
        self.commit('docs: readme')
        self.write('evals/behavior/cases.json', 'invalid dirty worktree')
        plan = self.plan()
        self.assertEqual(plan['case_ids'], [])
        self.assertTrue(plan['skip_reason'])

    def test_distribution_changes_select_full_suite_in_smoke_mode(self):
        paths = ('plugins/sample/plugin.json', 'scripts/sync_plugins.py',
                 '.agents/plugins/marketplace.json')
        for index, path in enumerate(paths):
            with self.subTest(path=path):
                self.base = self.git('rev-parse', 'HEAD')
                self.write(path, 'distribution change')
                self.commit('fix: distribution ' + str(index))
                plan = self.plan()
                self.assertEqual(plan['mode'], 'smoke')
                self.assertEqual(set(plan['case_ids']), {case['id'] for case in self.cases})

    def test_push_feat_anywhere_in_range_selects_full_suite(self):
        self.write('skills/sample/references/details.md', 'New instructions')
        self.commit('feat(sample): new instruction')
        self.write('README.md', 'Final commit is not feat')
        self.commit('docs: explain')
        plan = self.plan(event='push')
        self.assertEqual((plan['mode'], plan['repeats']), ('full', 10))
        self.assertEqual(len(plan['case_ids']), 6)

    def test_minor_manifest_bump_selects_full_on_push_but_smoke_on_pr(self):
        self.write('plugin.json', json.dumps({'name': 'example', 'version': '0.2.0'}))
        self.commit('chore: release candidate')
        self.assertEqual(self.plan(event='push')['mode'], 'full')
        self.assertEqual(self.plan(event='pull_request')['mode'], 'smoke')
        self.assertEqual(len(self.plan(event='pull_request')['case_ids']), 6)

    def test_invalid_baseline_still_writes_plan_and_insufficient_run_artifact(self):
        target = self.root / 'invalid-plan.json'
        result = self.cli('plan', '--repo', str(self.root), '--base', '0' * 40,
                          '--head', 'HEAD', '--event', 'push', '--output', str(target))
        self.assertEqual(result.returncode, 2)
        self.assertTrue(target.exists(), 'failed planning must still leave an artifact')
        result = self.cli('run', '--plan', str(target), '--output-dir', str(self.root / 'artifacts'))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads((self.root / 'artifacts/summary.json').read_text())['status'], 'insufficient')

    def test_non_object_plan_still_writes_report(self):
        for index, plan in enumerate(([1], 'invalid', None)):
            with self.subTest(plan=plan):
                output = self.root / f'invalid-{index}'
                self.assertEqual(evaluator.run_plan(plan, output), 2)
                self.assertEqual(json.loads((output / 'summary.json').read_text())['status'], 'insufficient')

    def test_malformed_manifest_leaves_insufficient_plan(self):
        self.write('plugin.json', '[]')
        self.commit('chore: malformed manifest')
        target = self.root / 'bad-manifest.json'
        result = self.cli('plan', '--repo', str(self.root), '--base', self.base,
                          '--head', 'HEAD', '--event', 'push', '--output', str(target))
        self.assertEqual(result.returncode, 2)
        self.assertTrue(json.loads(target.read_text())['plan_error'])

    def test_eval_or_runner_or_workflow_change_selects_all_smoke_cases(self):
        for filename in ('evals/legacy.md', 'scripts/behavior_eval.py', '.github/workflows/eval.yml'):
            with self.subTest(filename=filename):
                self.write(filename, 'changed')
                self.commit('chore: evaluation')
                plan = self.plan()
                self.assertEqual((plan['mode'], len(plan['case_ids'])), ('smoke', 6))

    def test_explicit_modes_evaluate_all_cases_without_changes(self):
        for mode, repeats in (('smoke', 1), ('full', 10)):
            plan = self.plan(mode=mode, event='workflow_dispatch')
            self.assertEqual((len(plan['case_ids']), plan['repeats']), (6, repeats))

    def test_missing_configuration_writes_insufficient_report_without_network(self):
        self.plan(mode='full', event='workflow_dispatch')
        result = self.cli('run', '--plan', str(self.root / 'plan.json'),
                          '--output-dir', str(self.root / 'artifacts'))
        self.assertEqual(result.returncode, 2)
        summary = json.loads((self.root / 'artifacts/summary.json').read_text())
        self.assertEqual(summary['status'], 'insufficient')
        self.assertIn('SKILL_EVAL_ENABLED', summary['reason'])
        self.assertTrue((self.root / 'artifacts/summary.md').is_file())

    def prepare_single_skill(self):
        self.cases = [example_case(mode=mode) for mode in
                      ('application', 'discovery_positive', 'discovery_negative')]
        (self.root / 'skills/second/SKILL.md').unlink()
        self.write('skills/sample/SKILL.md',
                   '---\nname: sample\ndescription: Use for sample.\n---\nCandidate instructions\n')
        self.write_suite()
        self.commit('fix: sample instructions')
        return self.plan(mode='full', event='workflow_dispatch')

    def test_full_run_alternates_order_keeps_failures_and_writes_provenance(self):
        plan = self.prepare_single_skill()
        requests = []
        api = []
        for _ in range(20):
            api += [response(calls=[tool_call('read_file', {'path': 'skills/sample/SKILL.md'})]),
                    response('A failing sample that stays identical.'),
                    response(json.dumps({'criteria': [{'index': 0, 'passed': False, 'reason': 'Scope was not preserved.'}]}))]
        api += unchanged_discovery_responses()
        with patch.dict(os.environ, dict(ENV, SKILL_EVAL_MAX_WORKERS='1'), clear=True), patch(
                'urllib.request.urlopen', side_effect=fake_http(api, requests)):
            code = evaluator.run_plan(plan, self.root / 'results')
        self.assertEqual(code, 0)
        summary = json.loads((self.root / 'results/summary.json').read_text())
        self.assertEqual(summary['status'], 'unchanged')
        self.assertEqual(len(summary['harness_sha256']), 64)
        self.assertEqual(summary['plan']['suite_sha256'], plan['suite_sha256'])
        self.assertEqual(summary['skills']['sample']['status'], 'unchanged')
        self.assertEqual(len(summary['cases'][0]['failures']), 20)
        self.assertEqual(summary['requests_used'], 100)
        self.assertEqual(summary['usage']['total_tokens'], 2500)
        tool_contents = [json.loads(request['messages'][-1]['content'])['content'] for request in requests
                         if request['messages'][-1].get('role') == 'tool']
        self.assertIn('Body secret', tool_contents[0])
        self.assertIn('Candidate instructions', tool_contents[1])
        self.assertIn('Candidate instructions', tool_contents[2])
        self.assertIn('Body secret', tool_contents[3])
        initial_requests = [request for request in requests if 'tools' in request and len(request['messages']) == 2]
        self.assertEqual(len(initial_requests), 20)
        self.assertEqual(len(list((self.root / 'results/traces').rglob('*.json'))), 60)
        self.assertNotIn('synthetic-test-key', (self.root / 'results/summary.json').read_text())

    def test_missing_baseline_skill_makes_no_api_call_and_reports_insufficient(self):
        self.write('skills/fresh/SKILL.md', '---\nname: fresh\ndescription: Fresh skill.\n---\nNew body')
        self.cases.extend(example_case('fresh', mode) for mode in
                          ('application', 'discovery_positive', 'discovery_negative'))
        self.write_suite()
        self.commit('fix: introduce skill')
        plan = self.plan()
        plan['case_ids'] = ['fresh-application']
        with patch.dict(os.environ, ENV, clear=True), patch('urllib.request.urlopen', side_effect=AssertionError('Unexpected API')):
            code = evaluator.run_plan(plan, self.root / 'results')
        self.assertEqual(code, 2)
        report = json.loads((self.root / 'results/summary.json').read_text())
        self.assertEqual(report['cases'][0]['status'], 'insufficient')
        self.assertIn('缺少技能', report['cases'][0]['reason'])
        self.assertEqual(report['requests_used'], 0)

    def test_run_rejects_changed_plan_digest_and_symbolic_git_blob(self):
        plan = self.prepare_single_skill()
        plan['suite_sha256'] = '0' * 64
        with patch.dict(os.environ, ENV, clear=True), patch('urllib.request.urlopen', side_effect=AssertionError('Unexpected API')):
            self.assertEqual(evaluator.run_plan(plan, self.root / 'bad-digest'), 2)
        (self.root / 'skills/sample/escape').symlink_to('/etc/hosts')
        self.commit('fix: linked file')
        plan = self.plan(mode='full')
        with patch.dict(os.environ, ENV, clear=True), patch('urllib.request.urlopen', side_effect=AssertionError('Unexpected API')):
            self.assertEqual(evaluator.run_plan(plan, self.root / 'bad-link'), 2)
        report = json.loads((self.root / 'bad-link/summary.json').read_text())
        self.assertIn('符号链接', report['cases'][0]['reason'])

    def test_budget_exhaustion_is_incomplete_even_when_first_answer_is_valid(self):
        plan = self.prepare_single_skill()
        requests = []
        api = [response(calls=[tool_call('read_file', {'path': 'skills/sample/SKILL.md'})]),
               response('Answer before budget ends')]
        with patch.dict(os.environ, dict(ENV, SKILL_EVAL_MAX_REQUESTS='2', SKILL_EVAL_MAX_WORKERS='1'), clear=True), patch(
                'urllib.request.urlopen', side_effect=fake_http(api, requests)):
            self.assertEqual(evaluator.run_plan(plan, self.root / 'results'), 2)
        report = json.loads((self.root / 'results/summary.json').read_text())
        self.assertEqual(report['requests_used'], 2)
        self.assertEqual(report['cases'][0]['completed_pairs'], 0)
        self.assertEqual(len(report['cases'][0]['failures']), 20)

    def test_cases_run_concurrently_with_at_most_three_in_flight_requests(self):
        plan = self.plan(mode='smoke', event='workflow_dispatch')
        barrier, lock = threading.Barrier(3), threading.Lock()
        active = peak = first = 0

        def http(request, timeout):
            nonlocal active, peak, first
            payload = json.loads(request.data)
            with lock:
                active += 1
                peak = max(peak, active)
                first += 1
                wait = first <= 3
            if wait:
                try:
                    barrier.wait(timeout=0.5)
                except threading.BrokenBarrierError:
                    pass
            if 'tools' in payload:
                if payload['messages'][-1].get('role') == 'tool':
                    item = response('Answer')
                else:
                    entry = json.loads(payload['messages'][1]['content'])['skill_entry']
                    item = response(calls=[tool_call('read_file', {'path': entry})])
            elif 'rubric' in json.loads(payload['messages'][-1]['content']):
                item = response(json.dumps({'criteria': [{'index': 0, 'passed': True, 'reason': 'Matches.'}]}))
            else:
                item = response(json.dumps({'selected_skills': [], 'reason': 'No applicable skill.'}))
            with lock:
                active -= 1
            return io.BytesIO(json.dumps(item).encode())

        with patch.dict(os.environ, ENV, clear=True), patch('urllib.request.urlopen', side_effect=http):
            self.assertEqual(evaluator.run_plan(plan, self.root / 'results'), 2)
        self.assertGreaterEqual(peak, 2)
        self.assertLessEqual(peak, 3)

    def test_full_run_reports_direction_and_regression_exit_code(self):
        plan = self.prepare_single_skill()
        for candidate_passed, status, exit_code in ((True, 'improved', 0), (False, 'regressed', 1)):
            with self.subTest(status=status):
                api = application_responses(not candidate_passed, candidate_passed) + unchanged_discovery_responses()
                destination = self.root / status
                with patch.dict(os.environ, dict(ENV, SKILL_EVAL_MAX_WORKERS='1'), clear=True), patch(
                        'urllib.request.urlopen', side_effect=fake_http(api, [])):
                    self.assertEqual(evaluator.run_plan(plan, destination), exit_code)
                report = json.loads((destination / 'summary.json').read_text())
                self.assertEqual(report['status'], status)
                self.assertEqual(report['skills']['sample']['status'], status)
                self.assertEqual(len(report['cases'][0]['failures']), 10)

    def test_incomplete_run_preserves_local_regression_but_overall_stays_insufficient(self):
        original_plan = self.prepare_single_skill()
        for partial_selection in (False, True):
            with self.subTest(partial_selection=partial_selection):
                plan = copy.deepcopy(original_plan)
                if partial_selection:
                    plan['case_ids'] = ['sample-application']
                requests = []
                destination = self.root / f'incomplete-{partial_selection}'
                env = dict(ENV, SKILL_EVAL_MAX_WORKERS='1', SKILL_EVAL_MAX_REQUESTS='60')
                with patch.dict(os.environ, env, clear=True), patch('urllib.request.urlopen',
                        side_effect=fake_http(application_responses(True, False), requests)):
                    self.assertEqual(evaluator.run_plan(plan, destination), 2)
                report = json.loads((destination / 'summary.json').read_text())
                self.assertEqual(report['status'], 'insufficient')
                self.assertEqual(report['skills']['sample']['status'], 'insufficient')
                self.assertEqual(report['cases'][0]['status'], 'regressed')
                self.assertEqual(report['cases'][0]['completed_pairs'], 10)
                self.assertEqual(len(requests), 60)
                if not partial_selection:
                    self.assertEqual(report['cases'][1]['status'], 'insufficient')
                    self.assertTrue(any('预算' in failure.get('error', '') for failure in report['cases'][1]['failures']))


def response(text=None, calls=(), finish_reason=None, model='test-model', reasoning_content=None):
    message = {'role': 'assistant', 'content': text}
    if calls:
        message['tool_calls'] = list(calls)
    if reasoning_content is not None:
        message['reasoning_content'] = reasoning_content
    return {'id': 'chatcmpl_test', 'object': 'chat.completion', 'created': 1793664000, 'model': model,
            'choices': [{'index': 0, 'message': message,
                         'finish_reason': finish_reason or ('tool_calls' if calls else 'stop')}],
            'usage': {'prompt_tokens': 20, 'completion_tokens': 5, 'total_tokens': 25}}


def tool_call(name, arguments, call_id='call_test'):
    return {'id': call_id, 'type': 'function', 'function': {'name': name, 'arguments': json.dumps(arguments)}}


def application_responses(before_passed, after_passed):
    replies = []
    for repeat in range(10):
        order = (before_passed, after_passed) if repeat % 2 == 0 else (after_passed, before_passed)
        for passed in order:
            replies += [response(calls=[tool_call('read_file', {'path': 'skills/sample/SKILL.md'})]),
                        response('An answer'), response(json.dumps({'criteria': [
                            {'index': 0, 'passed': passed, 'reason': 'Evidence for this criterion.'}]}))]
    return replies


def unchanged_discovery_responses():
    return [response(json.dumps({'selected_skills': selected, 'reason': 'Catalog selection.'}))
            for selected in (['sample'], []) for _ in range(20)]


def fake_http(responses, requests):
    iterator = iter(responses)

    def send(request, timeout):
        requests.append(json.loads(request.data))
        item = next(iterator)
        if isinstance(item, Exception):
            raise item
        return io.BytesIO(json.dumps(item).encode())
    return send


ENV = {'SKILL_EVAL_ENABLED': 'true', 'SKILL_EVAL_MODEL': 'test-model',
       'SKILL_EVAL_MAX_REQUESTS': '100', 'UNIF_MODEL_API_KEY': 'synthetic-test-key',
       'UNIF_MODEL_BASE_URL': 'https://dashscope.aliyuncs.com/compatible-mode/v1'}


class RunnerTests(unittest.TestCase):
    def client(self, extra=None):
        return evaluator.ChatCompletionsClient(evaluator.configuration(dict(ENV, **(extra or {}))))

    def test_explicit_bailian_endpoint_and_key_use_chat_completions_without_logging_secret(self):
        captured = []

        def http(request, timeout):
            captured.append(request)
            return io.BytesIO(json.dumps(response('answer')).encode())

        client = self.client({'UNIF_MODEL_BASE_URL': ENV['UNIF_MODEL_BASE_URL'] + '/',
                              'SKILL_EVAL_MODEL': 'deepseek-v4-pro'})
        trace = []
        with patch('urllib.request.urlopen', side_effect=http):
            client.request([{'role': 'user', 'content': 'task'}], trace)
        self.assertEqual(captured[0].full_url, 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions')
        self.assertEqual(captured[0].get_header('Authorization'), 'Bearer synthetic-test-key')
        payload = json.loads(captured[0].data)
        self.assertEqual(payload['model'], 'deepseek-v4-pro')
        self.assertEqual(payload['messages'], [{'role': 'user', 'content': 'task'}])
        self.assertEqual(payload['max_tokens'], 4096)
        self.assertTrue(set(payload).isdisjoint({'input', 'store', 'include', 'reasoning', 'reasoning_effort',
                                               'max_output_tokens', 'enable_thinking'}))
        self.assertEqual(client.config['thinking'], 'provider_default')
        self.assertNotIn('synthetic-test-key', json.dumps(trace))

    def test_endpoint_must_be_explicit_https_without_embedded_credentials_or_query(self):
        invalid = ['', 'http://dashscope.aliyuncs.com/compatible-mode/v1',
                   'https://user:secret@dashscope.aliyuncs.com/v1',
                   'https://dashscope.aliyuncs.com/v1?api_key=secret',
                   'https://dashscope.aliyuncs.com/v1#fragment', 'https:///v1',
                   'https://dashscope.aliyuncs.com/\nv1']
        for base_url in invalid:
            with self.subTest(base_url=base_url), self.assertRaises(evaluator.EvalError):
                self.client({'UNIF_MODEL_BASE_URL': base_url})
        with self.assertRaises(evaluator.EvalError):
            evaluator.configuration(dict(ENV, UNIF_MODEL_API_KEY='', OPENAI_API_KEY='not-a-fallback'))

    def test_json_object_mode_still_rejects_invalid_local_grade_and_selection(self):
        for grade in ({'criteria': [{'index': 0, 'passed': 'true', 'reason': 'Wrong type.'}]},
                      {'criteria': [{'index': 0, 'passed': True, 'reason': 'Valid text.', 'extra': 1}]},
                      {'criteria': [{'index': 0, 'passed': True, 'reason': 'Valid text.'}], 'extra': 1}):
            with self.subTest(grade=grade):
                api = [response(calls=[tool_call('read_file', {'path': 'skills/sample/SKILL.md'})]),
                       response('answer'), response(json.dumps(grade))]
                with patch('urllib.request.urlopen', side_effect=fake_http(api, [])):
                    sample = evaluator.evaluate_sample(self.client(), example_case(),
                        {'skills/sample/SKILL.md': b'instructions'}, [], 'sha')
                self.assertEqual(sample['status'], 'error')
        invalid_selection = {'selected_skills': ['sample'], 'reason': 'A match.', 'extra': 1}
        with patch('urllib.request.urlopen', side_effect=fake_http([response(json.dumps(invalid_selection))], [])):
            sample = evaluator.evaluate_sample(self.client(), example_case(mode='discovery_positive'), {},
                [{'name': 'sample', 'description': 'Use sample.'}], 'sha')
        self.assertEqual(sample['status'], 'error')

    def test_application_reads_only_skill_and_fixtures_and_judges_in_fresh_context(self):
        case = example_case()
        case['rubric'] = ['SECRET RUBRIC; preserve scope.']
        requests = []
        api = [response(calls=[tool_call('read_file', {'path': 'skills/sample/SKILL.md'})]),
               response(calls=[tool_call('read_file', {'path': 'fixtures/project.txt'})]),
               response('Only change the selected entry.'),
               response(json.dumps({'criteria': [{'index': 0, 'passed': True, 'reason': 'Uses the permitted entry.'}]}))]
        with patch('urllib.request.urlopen', side_effect=fake_http(api, requests)):
            result = evaluator.evaluate_sample(self.client(), case,
                {'skills/sample/SKILL.md': b'Skill instructions'}, [], 'sample-sha')
        self.assertEqual(result['status'], 'complete')
        self.assertTrue(result['skill_loaded'])
        self.assertEqual(result['scores'], [True])
        self.assertEqual(len(result['read_trace']), 2)
        self.assertNotIn('SECRET RUBRIC', json.dumps(requests[:-1]))
        self.assertIn('SECRET RUBRIC', json.dumps(requests[-1]))
        self.assertNotIn('Skill instructions', json.dumps(requests[-1]))
        self.assertNotIn('tools', requests[-1])
        self.assertEqual(requests[-1]['response_format'], {'type': 'json_object'})
        self.assertIn('"criteria"', requests[-1]['messages'][0]['content'])
        self.assertNotIn('response_format', requests[0])
        self.assertEqual(result['usage']['prompt_tokens'], 80)
        self.assertEqual(result['usage']['completion_tokens'], 20)
        self.assertEqual(result['usage']['total_tokens'], 100)
        self.assertNotIn('synthetic-test-key', json.dumps(result))

    def test_application_requires_successful_entry_read_even_if_answer_claims_to_read_it(self):
        attempts = [[], [tool_call('list_files', {'path': 'skills/sample'})],
                    [tool_call('read_file', {'path': 'fixtures/project.txt'})],
                    [tool_call('read_file', {'path': 'skills/sample/../sample/SKILL.md'})]]
        answer = 'I read skills/sample/SKILL.md and will only change the selected entry.'
        for calls in attempts:
            with self.subTest(calls=calls):
                requests = []
                api = ([response(calls=calls)] if calls else []) + [response(answer), response(json.dumps({
                    'criteria': [{'index': 0, 'passed': True, 'reason': 'Guessed the correct answer.'}]}))]
                with patch('urllib.request.urlopen', side_effect=fake_http(api, requests)):
                    result = evaluator.evaluate_sample(self.client(), example_case(),
                        {'skills/sample/SKILL.md': b'actual instructions'}, [], 'sha')
                self.assertEqual(result['status'], 'error')
                self.assertFalse(result['skill_loaded'])
                self.assertEqual(result['answer'], answer)
                self.assertEqual(result['scores'], [])
                self.assertEqual(len(requests), 2 if calls else 1)
                self.assertFalse(any(row['role'] == 'judge' for row in result['api_trace']))

    def test_file_map_rejects_traversal_unknown_tools_and_other_skills(self):
        files = evaluator.ReadOnlyFiles('sample', {'skills/sample/SKILL.md': b'allowed'}, {'project.txt': 'fixture'})
        self.assertEqual(files.call('list_files', {'path': ''}),
                         {'files': ['fixtures/project.txt', 'skills/sample/SKILL.md']})
        for path in ('../secret', '/etc/hosts', 'skills/second/SKILL.md', 'C:\\secret', 'skills/sample/../second/SKILL.md'):
            with self.subTest(path=path), self.assertRaises(evaluator.EvalError):
                files.call('read_file', {'path': path})
        with self.assertRaises(evaluator.EvalError):
            files.call('shell', {'path': 'cat /etc/hosts'})

    def test_multiple_reads_share_one_round_and_outside_path_stays_denied(self):
        requests = []
        api = [response(calls=[tool_call('read_file', {'path': 'skills/sample/SKILL.md'}, 'skill'),
                               tool_call('read_file', {'path': 'fixtures/project.txt'}, 'fixture'),
                               tool_call('read_file', {'path': '/etc/hosts'}, 'denied')],
                        reasoning_content='Read the permitted materials before answering.'),
               response('Use the selected entry.'), response(json.dumps({'criteria': [
                   {'index': 0, 'passed': True, 'reason': 'Respects scope.'}]}))]
        with patch('urllib.request.urlopen', side_effect=fake_http(api, requests)):
            result = evaluator.evaluate_sample(self.client({'SKILL_EVAL_MAX_TURNS': '2'}), example_case(),
                {'skills/sample/SKILL.md': b'instructions'}, [], 'sha')
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(requests[0]['tools'][0]['function']['name'], 'read_file')
        assistant = next(item for item in requests[1]['messages'] if item.get('role') == 'assistant')
        self.assertEqual(assistant, api[0]['choices'][0]['message'])
        outputs = [item for item in requests[1]['messages'] if item.get('role') == 'tool']
        self.assertEqual([item['tool_call_id'] for item in outputs], ['skill', 'fixture', 'denied'])
        self.assertIn('error', json.loads(outputs[2]['content']))
        self.assertNotIn('Read the permitted materials before answering.', json.dumps(requests[-1]))
        self.assertEqual(len(result['read_trace']), 3)

    def test_discovery_has_only_metadata_and_prompt_and_scores_constraints(self):
        case = example_case(mode='discovery_positive')
        requests = []
        with patch('urllib.request.urlopen', side_effect=fake_http(
                [response(json.dumps({'selected_skills': ['sample'], 'reason': 'Matches the description.'}))], requests)):
            result = evaluator.evaluate_sample(self.client(), case,
                {'skills/sample/SKILL.md': b'SECRET SKILL BODY'},
                [{'name': 'sample', 'description': 'Use for sample.'}], 'metadata-sha')
        self.assertEqual(result['scores'], [True])
        self.assertEqual(len(requests), 1)
        self.assertNotIn('SECRET SKILL BODY', json.dumps(requests))
        self.assertNotIn('Preserves the scope.', json.dumps(requests))
        self.assertNotIn('tools', requests[0])
        self.assertEqual(requests[0]['response_format'], {'type': 'json_object'})
        self.assertIn('"selected_skills"', requests[0]['messages'][0]['content'])
        self.assertEqual(result['judgement'], 'programmatic_set_constraints')

    def test_refusal_incomplete_response_timeout_and_invalid_grade_are_insufficient(self):
        refused = response()
        refused['choices'][0]['message']['refusal'] = 'Cannot answer.'
        scenarios = [[refused], [response('partial', finish_reason='length')],
                     [response('blocked', finish_reason='content_filter')], [response('')], [TimeoutError()],
                     [response(calls=[tool_call('read_file', {'path': 'skills/sample/SKILL.md'})]),
                      response('answer'), response('{"criteria":[]}')]]
        for api in scenarios:
            with self.subTest(api=api), patch('urllib.request.urlopen', side_effect=fake_http(api, [])):
                result = evaluator.evaluate_sample(self.client(), example_case(),
                    {'skills/sample/SKILL.md': b'Instructions'}, [], 'sha')
            self.assertEqual(result['status'], 'error')
            self.assertTrue(result['error'])
            self.assertTrue(result['api_trace'])

    def test_malformed_or_unauthorized_tool_messages_are_insufficient(self):
        read = tool_call('read_file', {'path': 'skills/sample/SKILL.md'})
        missing_id = copy.deepcopy(read)
        del missing_id['id']
        invalid_arguments = copy.deepcopy(read)
        invalid_arguments['function']['arguments'] = {'path': 'skills/sample/SKILL.md'}
        wrong_role = response('answer')
        wrong_role['choices'][0]['message']['role'] = 'tool'
        scenarios = [response(calls=[read], finish_reason='stop'),
                     response(finish_reason='tool_calls'), response(calls=[missing_id]),
                     response(calls=[read, read]), response(calls=[invalid_arguments]), wrong_role,
                     response(reasoning_content='Only thinking, no final answer.')]
        for item in scenarios:
            with self.subTest(item=item), patch('urllib.request.urlopen', side_effect=fake_http([item], [])):
                sample = evaluator.evaluate_sample(self.client(), example_case(),
                    {'skills/sample/SKILL.md': b'instructions'}, [], 'sha')
                self.assertEqual(sample['status'], 'error')
                self.assertEqual(sample['read_trace'], [])
        with patch('urllib.request.urlopen', side_effect=fake_http([response(calls=[read])], [])):
            sample = evaluator.evaluate_sample(self.client(), example_case(mode='discovery_positive'), {},
                [{'name': 'sample', 'description': 'Use sample.'}], 'sha')
        self.assertEqual(sample['status'], 'error')
        self.assertEqual(sample['read_trace'], [])

    def test_budget_and_round_limits_prevent_unbounded_requests(self):
        requests = []
        api = [response(calls=[tool_call('read_file', {'path': 'skills/sample/SKILL.md'})]), response('answer')]
        with patch('urllib.request.urlopen', side_effect=fake_http(api, requests)):
            result = evaluator.evaluate_sample(self.client({'SKILL_EVAL_MAX_REQUESTS': '2'}), example_case(),
                {'skills/sample/SKILL.md': b'Instructions'}, [], 'sha')
        self.assertEqual(result['status'], 'error')
        self.assertTrue(result['skill_loaded'])
        self.assertIn('预算', result['error'])
        self.assertEqual(len(requests), 2)
        requests = []
        api = [response(calls=[tool_call('list_files', {'path': ''})])] * 2
        with patch('urllib.request.urlopen', side_effect=fake_http(api, requests)):
            result = evaluator.evaluate_sample(self.client({'SKILL_EVAL_MAX_TURNS': '2'}), example_case(),
                {'skills/sample/SKILL.md': b'Instructions'}, [], 'sha')
        self.assertEqual(result['status'], 'error')
        self.assertEqual(len(requests), 2)

    def test_configuration_never_infers_api_model_key_or_unbounded_budget(self):
        for changes in ({'SKILL_EVAL_ENABLED': 'false'}, {'SKILL_EVAL_MODEL': ''},
                        {'UNIF_MODEL_API_KEY': ''}, {'UNIF_MODEL_BASE_URL': ''}, {'SKILL_EVAL_MAX_REQUESTS': '0'},
                        {'SKILL_EVAL_MAX_REQUESTS': 'unlimited'}, {'SKILL_EVAL_MAX_TURNS': '999'},
                        {'SKILL_EVAL_MAX_WORKERS': '4'}):
            with self.subTest(changes=changes), self.assertRaises(evaluator.EvalError):
                evaluator.configuration(dict(ENV, **changes))

    def test_concurrent_requests_share_one_atomic_budget(self):
        client = self.client({'SKILL_EVAL_MAX_REQUESTS': '2'})
        requests, lock = [], threading.Lock()

        def http(request, timeout):
            with lock:
                requests.append(request)
            return io.BytesIO(json.dumps(response('answer')).encode())

        def request_once(_):
            try:
                client.request([{'role': 'user', 'content': 'task'}], [])
                return True
            except evaluator.EvalError:
                return False

        with patch('urllib.request.urlopen', side_effect=http), ThreadPoolExecutor(max_workers=8) as pool:
            outcomes = list(pool.map(request_once, range(20)))
        self.assertEqual(sum(outcomes), 2)
        self.assertEqual(len(requests), 2)
        self.assertEqual(client.requests_used, 2)

    def test_malformed_usage_or_content_retains_error_trace_without_crashing(self):
        bad_usage = response('answer')
        bad_usage['usage']['total_tokens'] = 'invalid'
        bad_content = response('answer')
        bad_content['choices'][0]['message']['content'] = ['invalid']
        for bad in (bad_usage, bad_content, [], {'choices': None}, {'choices': []}):
            with self.subTest(bad=bad), patch('urllib.request.urlopen', side_effect=fake_http([bad], [])):
                result = evaluator.evaluate_sample(self.client(), example_case(),
                    {'skills/sample/SKILL.md': b'instructions'}, [], 'sha')
                self.assertEqual(result['status'], 'error')
                self.assertTrue(result['api_trace'])

    def test_http_failure_stops_later_requests_and_marks_usage_unknown(self):
        for status in (401, 429, 500):
            with self.subTest(status=status):
                client, requests = self.client(), []
                failure = urllib.error.HTTPError(ENV['UNIF_MODEL_BASE_URL'] + '/chat/completions', status,
                                                'failed', {}, io.BytesIO(b'do not disclose this body'))
                with patch('urllib.request.urlopen', side_effect=fake_http([failure], requests)):
                    first = evaluator.evaluate_sample(client, example_case(), {'skills/sample/SKILL.md': b'body'}, [], 'sha')
                    second = evaluator.evaluate_sample(client, example_case(), {'skills/sample/SKILL.md': b'body'}, [], 'sha')
                self.assertEqual(len(requests), 1)
                self.assertEqual(first['status'], 'error')
                self.assertEqual(second['status'], 'error')
                self.assertFalse(first['usage_complete'])
                self.assertNotIn('do not disclose', json.dumps(first))

    def test_metadata_parser_never_returns_skill_body_or_other_frontmatter(self):
        text = '---\nname: sample\ndescription: >-\n  Use for first\n  and second.\nmetadata:\n  private: hidden\n---\nSECRET BODY'
        self.assertEqual(evaluator.skill_metadata(text, 'sample'),
                         {'name': 'sample', 'description': 'Use for first and second.'})


class ComparisonTests(unittest.TestCase):
    def samples(self, before, after, count):
        return [({'status': 'complete', 'scores': before}, {'status': 'complete', 'scores': after}) for _ in range(count)]

    def test_aggregation_keeps_incomplete_evidence_and_never_offsets_regression(self):
        for states, expected in ((['regressed', 'insufficient'], 'insufficient'),
                                 (['regressed', 'improved'], 'regressed'),
                                 (['improved', 'unchanged'], 'improved')):
            with self.subTest(states=states):
                self.assertEqual(evaluator.aggregate({'status': state} for state in states), expected)

    def test_smoke_and_five_discordant_pairs_are_insufficient_with_two_sided_rule(self):
        self.assertEqual(evaluator.compare_results(self.samples([True], [True], 1), 1)['status'], 'insufficient')
        outcome = evaluator.compare_results(self.samples([False], [True], 5), 5)
        self.assertEqual(outcome['status'], 'insufficient')
        self.assertEqual(outcome['criteria'][0]['p_two_sided'], 0.0625)

    def test_unchanged_and_significant_improvement_and_regression(self):
        cases = [([True], [True], 5, 'unchanged'), ([False], [True], 10, 'improved'),
                 ([True], [False], 10, 'regressed')]
        for before, after, repeats, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(evaluator.compare_results(self.samples(before, after, repeats), repeats)['status'], expected)

    def test_criterion_regression_cannot_be_canceled_by_other_improvements(self):
        outcome = evaluator.compare_results(self.samples([True, False, False], [False, True, True], 6), 6)
        self.assertEqual(outcome['status'], 'regressed')
        self.assertEqual(outcome['observed_losses'], 6)

    def test_missing_or_error_pair_is_insufficient(self):
        pairs = self.samples([True], [True], 5)
        self.assertEqual(evaluator.compare_results(pairs[:-1], 5)['status'], 'insufficient')
        pairs[0][0]['status'] = 'error'
        self.assertEqual(evaluator.compare_results(pairs, 5)['status'], 'insufficient')

    def test_incomplete_run_retains_observed_changes_from_completed_pairs(self):
        pairs = self.samples([True], [False], 1)
        pairs.append(({'status': 'error'}, {'status': 'error'}))
        result = evaluator.compare_results(pairs, 10)
        self.assertEqual(result['status'], 'insufficient')
        self.assertEqual(result['completed_pairs'], 1)
        self.assertEqual(result['observed_losses'], 1)

    def test_mixed_actual_models_cannot_be_compared(self):
        pairs = self.samples([True], [True], 5)
        pairs[0][0]['actual_models'] = {'answer': ['snapshot-a']}
        pairs[0][1]['actual_models'] = {'answer': ['snapshot-b']}
        self.assertEqual(evaluator.compare_results(pairs, 5)['status'], 'insufficient')
        for before, after in pairs:
            before['actual_models'] = after['actual_models'] = {'answer': ['snapshot-a', 'snapshot-b']}
        self.assertEqual(evaluator.compare_results(pairs, 5)['status'], 'insufficient')


if __name__ == '__main__':
    unittest.main()
