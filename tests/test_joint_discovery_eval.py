"""联合目录使用真实 Git 快照；模型网络边界由受控响应替代。"""

from pathlib import Path
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import urllib.request
from unittest.mock import patch
from typing import override

from scripts import behavior_eval as evaluator
from scripts import joint_discovery_eval as joint
from scripts import sync_evaluation_tools as sync


ROOT = Path(__file__).resolve().parents[1]


class JointDiscoveryTests(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base: Path = Path(self.temp.name)
        self.repositories: dict[str, Path] = {}
        self.revisions: dict[str, str] = {}
        self.catalog: Path = self.base / 'catalog.json'

    @override
    def setUp(self) -> None:
        for package, skill in [('uni-skills', 'uni-example'), ('unif-portal-dev-skills', 'unif-example')]:
            repo = self.base / package
            repo.mkdir()
            _ = (repo / 'plugin.json').write_text(json.dumps({'name': package}), encoding='utf-8')
            directory = repo / 'skills' / skill
            directory.mkdir(parents=True)
            _ = (directory / 'SKILL.md').write_text(
                f'---\nname: {skill}\ndescription: Apply {skill} when its task is requested.\n---\n', encoding='utf-8')
            if package == 'uni-skills':
                optional = repo / 'skills/uni-optional'
                optional.mkdir()
                _ = (optional / 'SKILL.md').write_text('---\nname: uni-optional\ndescription: Optional method.\n---\n', encoding='utf-8')
            for args in [('init', '-q'), ('config', 'user.email', 'test@example.invalid'),
                         ('config', 'user.name', 'Test'), ('add', '.'), ('commit', '-qm', 'fixture')]:
                _ = subprocess.run(['git', *args], cwd=repo, check=True, capture_output=True)
            self.repositories[package] = repo
            self.revisions[package] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()

    def command(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = dict(os.environ)
        environment['PYTHONDONTWRITEBYTECODE'] = '1'
        _ = environment.pop('SKILL_EVAL_ENABLED', None)
        return subprocess.run([sys.executable, '-m', 'scripts.joint_discovery_eval', *arguments],
                              cwd=ROOT, env=environment, text=True, capture_output=True, check=False)

    def test_freeze_combines_two_fixed_repositories_without_local_paths(self) -> None:
        result = self.command('freeze', '--uni-repo', str(self.repositories['uni-skills']),
                              '--uni-ref', self.revisions['uni-skills'], '--unif-repo',
                              str(self.repositories['unif-portal-dev-skills']), '--unif-ref',
                              self.revisions['unif-portal-dev-skills'], '--catalog', str(self.catalog))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(str(self.base), self.catalog.read_text(encoding='utf-8'))
        self.assertIn('uni-example', self.catalog.read_text(encoding='utf-8'))
        self.assertIn('unif-example', self.catalog.read_text(encoding='utf-8'))


    def frozen(self) -> joint.Catalog:
        catalog = joint.freeze(self.repositories['uni-skills'], self.revisions['uni-skills'],
                               self.repositories['unif-portal-dev-skills'], self.revisions['unif-portal-dev-skills'])
        evaluator.write_json(self.catalog, catalog)
        return catalog

    def suite(self) -> Path:
        case: evaluator.Case = {'id': 'combined', 'skill': 'uni-example', 'mode': 'discovery_positive',
            'prompt': 'Implement the project feature.', 'source': 'synthetic joint case',
            'rubric': ['DO_NOT_SEND_RUBRIC'], 'fixtures': {},
            'required_skills': ['uni-example', 'unif-example'], 'forbidden_skills': []}
        path = self.base / 'cases.json'
        evaluator.write_json(path, {'formatVersion': 1, 'cases': [case]})
        return path

    def configuration(self, budget: int = 2) -> dict[str, str]:
        return {'SKILL_EVAL_ENABLED': 'true', 'SKILL_EVAL_MODEL': 'synthetic-model',
                'SKILL_EVAL_MAX_REQUESTS': str(budget), 'UNIF_MODEL_BASE_URL': 'https://example.invalid/v1',
                'UNIF_MODEL_API_KEY': 'synthetic-secret'}

    def test_cross_package_constraints_and_unlisted_choices_are_supported(self) -> None:
        catalog = self.frozen()
        cases = joint.read_cases(self.suite(), catalog)
        self.assertEqual(cases[0]['required_skills'], ['uni-example', 'unif-example'])
        self.assertEqual(len(catalog['skills']), 3)
        cases[0]['forbidden_skills'] = ['not-in-catalog']
        evaluator.write_json(self.suite_path(), {'formatVersion': 1, 'cases': cases})
        with self.assertRaisesRegex(ValueError, '集合'):
            _ = joint.read_cases(self.suite_path(), catalog)

    def suite_path(self) -> Path:
        return self.base / 'cases.json'

    def test_catalog_tampering_and_application_mode_are_rejected(self) -> None:
        catalog = self.frozen()
        catalog['skills'][0]['description'] = 'Changed without re-freezing.'
        with self.assertRaisesRegex(ValueError, '摘要'):
            _ = joint.parse_catalog(catalog)
        catalog = self.frozen()
        cases = joint.read_cases(self.suite(), catalog)
        cases[0]['mode'] = 'application'
        evaluator.write_json(self.suite_path(), {'formatVersion': 1, 'cases': cases})
        with self.assertRaisesRegex(ValueError, '只支持目录发现'):
            _ = joint.read_cases(self.suite_path(), catalog)

    def test_sources_are_fixed_commits_and_metadata_must_match_them(self) -> None:
        catalog = self.frozen()
        path = self.repositories['uni-skills'] / 'skills/uni-example/SKILL.md'
        _ = path.write_text('dirty working tree', encoding='utf-8')
        joint.verify_sources(catalog, self.repositories['uni-skills'], self.repositories['unif-portal-dev-skills'])
        catalog['skills'][0]['description'] = 'Forged but internally consistent.'
        catalog['sha256'] = joint.catalog_digest(catalog['sources'], catalog['skills'])
        with self.assertRaisesRegex(ValueError, '固定来源'):
            joint.verify_sources(catalog, self.repositories['uni-skills'], self.repositories['unif-portal-dev-skills'])

    def test_package_comparison_only_uses_the_selected_committed_discovery_inputs(self) -> None:
        _ = self.frozen()
        repo = self.repositories['unif-portal-dev-skills']
        _ = self.repositories['uni-skills'].rename(self.base / 'offline')
        manifest = repo / 'plugin.json'
        original = manifest.read_bytes()
        _ = manifest.write_text('{"name":"unif-portal-dev-skills","version":"1.1.1"}', encoding='utf-8')
        _ = subprocess.run(['git', 'commit', '-qam', 'change only version'], cwd=repo, check=True)
        version_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()

        _ = manifest.write_bytes(original)
        path = repo / 'skills/unif-example/SKILL.md'
        _ = path.write_text(path.read_text(encoding='utf-8') + '\nRevised body.\n', encoding='utf-8')
        _ = subprocess.run(['git', 'commit', '-qam', 'restore version and update body'], cwd=repo, check=True)
        body_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
        _ = path.write_text('uncommitted edit', encoding='utf-8')
        args = ('compare-package', '--repo', str(repo), '--catalog', str(self.catalog))
        for revision, flags in ((version_commit, ('--ref', version_commit)), (body_commit, ())):
            with self.subTest(revision=revision):
                result = self.command(*args, *flags)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('名称和描述一致', result.stdout)
                self.assertIn(revision, result.stdout)

    def test_package_comparison_reports_changes_while_the_historical_baseline_remains_valid(self) -> None:
        catalog = self.frozen()
        repo = self.repositories['uni-skills']
        path = repo / 'skills/uni-example/SKILL.md'
        _ = path.write_text(path.read_text(encoding='utf-8').replace('is requested', 'is reviewed'), encoding='utf-8')
        old = repo / 'skills/uni-optional/SKILL.md'
        new = repo / 'skills/uni-added/SKILL.md'
        new.parent.mkdir()
        _ = new.write_text(old.read_text(encoding='utf-8').replace('uni-optional', 'uni-added'), encoding='utf-8')
        old.unlink()
        _ = subprocess.run(['git', 'add', '-A'], cwd=repo, check=True)
        _ = subprocess.run(['git', 'commit', '-qm', 'change discovery inputs'], cwd=repo, check=True)

        _ = joint.validate(self.catalog, self.suite())
        joint.verify_sources(catalog, repo, self.repositories['unif-portal-dev-skills'])
        args = ('compare-package', '--repo', str(repo), '--catalog', str(self.catalog))
        for ci in (False, True):
            with self.subTest(ci=ci):
                summary = self.base / 'summary.md'
                with patch.dict(os.environ, {'GITHUB_STEP_SUMMARY': str(summary)}):
                    result = self.command(*args, *(['--ci'] if ci else []))
                self.assertEqual(result.returncode, 0 if ci else 1, result.stderr)
                for change in ('新增：uni-added', '删除：uni-optional', '描述变化：uni-example'):
                    self.assertIn(change, result.stdout)
                    if ci:
                        self.assertIn(change, summary.read_text(encoding='utf-8'))
                self.assertEqual('::warning::' in result.stdout, ci)
        previous = self.command(*args, '--ref', self.revisions['uni-skills'])
        self.assertEqual(previous.returncode, 0, previous.stderr)
        self.assertIn('名称和描述一致', previous.stdout)

    def test_ci_keeps_unreadable_sources_and_invalid_catalogs_as_errors(self) -> None:
        _ = self.frozen()
        args = ('compare-package', '--ci', '--repo', str(self.repositories['uni-skills']), '--catalog', str(self.catalog))
        missing = self.command(*args, '--ref', 'missing-ref')
        self.assertEqual(missing.returncode, 2)
        self.assertIn('Git 对象不可读取', missing.stderr)
        _ = self.catalog.write_text('{}', encoding='utf-8')
        invalid = self.command(*args)
        self.assertEqual(invalid.returncode, 2)
        self.assertIn('formatVersion', invalid.stderr)

    def test_run_without_explicit_configuration_is_insufficient_and_offline(self) -> None:
        _ = self.frozen()
        output = self.base / 'disabled-run'
        with patch('urllib.request.urlopen', side_effect=AssertionError('unexpected network')):
            code = joint.run(self.catalog, self.suite(), output, repeats=1, env={})
        report = joint.read_json(output / 'report.json')
        assert evaluator.is_object(report)
        self.assertEqual(code, 2)
        self.assertEqual(report['status'], 'insufficient')
        self.assertEqual(report['requests_used'], 0)

    def test_combined_selection_uses_real_set_scoring_and_records_evidence(self) -> None:
        _ = self.frozen()
        output = self.base / 'passed-run'
        requests: list[bytes] = []

        def send(request: urllib.request.Request, *, timeout: int) -> io.BytesIO:
            self.assertGreater(timeout, 0)
            assert isinstance(request.data, bytes)
            requests.append(request.data)
            payload: evaluator.Response = {'model': 'synthetic-model-v1', 'usage': {
                'prompt_tokens': 20, 'completion_tokens': 5, 'total_tokens': 25}, 'choices': [{
                'finish_reason': 'stop', 'message': {'role': 'assistant', 'content': json.dumps({
                    'selected_skills': ['uni-example', 'unif-example', 'uni-optional'], 'reason': 'Both layers apply.'})}}]}
            return io.BytesIO(json.dumps(payload).encode())

        with patch('urllib.request.urlopen', side_effect=send):
            code = joint.run(self.catalog, self.suite(), output, repeats=1, env=self.configuration())
        self.assertEqual(code, 0)
        self.assertIn(b'uni-example', requests[0])
        self.assertIn(b'unif-example', requests[0])
        for hidden in (b'required_skills', b'forbidden_skills', b'DO_NOT_SEND_RUBRIC', b'synthetic-secret'):
            self.assertNotIn(hidden, requests[0])
        sample = joint.read_json(output / 'samples/combined/1.json')
        report = joint.read_json(output / 'report.json')
        assert evaluator.is_object(sample) and evaluator.is_object(report)
        self.assertEqual(sample['scores'], [True, True])
        self.assertEqual(report['status'], 'passed')
        self.assertEqual(report['requests_used'], 1)
        self.assertNotIn('synthetic-secret', json.dumps(report))
        self.assertEqual((output / 'catalog.json').read_bytes(), self.catalog.read_bytes())

    def test_missing_project_layer_fails_and_budget_limit_is_not_a_pass(self) -> None:
        _ = self.frozen()
        suite = self.suite()
        payload: evaluator.Response = {'model': 'synthetic-model-v1', 'usage': {
            'prompt_tokens': 20, 'completion_tokens': 5, 'total_tokens': 25}, 'choices': [{
            'finish_reason': 'stop', 'message': {'role': 'assistant', 'content': json.dumps({
                'selected_skills': ['uni-example'], 'reason': 'Only platform selected.'})}}]}
        with patch('urllib.request.urlopen', return_value=io.BytesIO(json.dumps(payload).encode())):
            code = joint.run(self.catalog, suite, self.base / 'failed-run', repeats=1, env=self.configuration())
        self.assertEqual(code, 1)
        with patch('urllib.request.urlopen', return_value=io.BytesIO(json.dumps(payload).encode())):
            code = joint.run(self.catalog, suite, self.base / 'budget-run', repeats=2, env=self.configuration(1))
        report = joint.read_json(self.base / 'budget-run/report.json')
        assert evaluator.is_object(report)
        self.assertEqual(code, 2)
        self.assertEqual(report['requests_used'], 1)
        self.assertEqual(report['completed_samples'], 1)

    def test_checked_in_catalog_and_cases_validate_without_other_repositories(self) -> None:
        catalog, cases = joint.validate(ROOT / joint.CATALOG, ROOT / joint.SUITE)
        self.assertEqual(set(catalog['sources']), set(joint.PACKAGES))
        self.assertGreaterEqual(len(cases), 4)
        self.assertTrue(any(any(name.startswith('uni-') for name in case['required_skills']) and
                            any(name.startswith('unif-') for name in case['required_skills']) for case in cases))


    def test_sync_adopts_joint_tool_and_frozen_inputs_without_external_runtime_dependency(self) -> None:
        source, target = self.repositories['uni-skills'], self.repositories['unif-portal-dev-skills']
        joint_files = ('scripts/joint_discovery_eval.py', 'tests/test_joint_discovery_eval.py',
                       joint.CATALOG, joint.SUITE)
        for relative in set(sync.FILES) | set(joint_files):
            path = source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            _ = path.write_text('frozen: ' + relative, encoding='utf-8')
        sync.sync_evaluation_tools(source, target)
        for relative in joint_files:
            self.assertTrue((target / relative).is_file(), relative)
            self.assertEqual((target / relative).read_bytes(), (source / relative).read_bytes())
        _ = (target / joint.CATALOG).write_text('changed local snapshot', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, '摘要'):
            _ = sync.check_evaluation_tools(target)


if __name__ == '__main__':
    _ = unittest.main()
