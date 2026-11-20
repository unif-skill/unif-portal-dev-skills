#!/usr/bin/env python3
"""冻结两仓目录，离线校验联合题库，并显式运行跨包发现集合评测。"""

import argparse
from collections.abc import Mapping, Sequence
import os
from pathlib import Path
import re
import sys
from typing import TypedDict

from scripts import behavior_eval as evaluator


ROOT = Path(__file__).resolve().parents[1]
CATALOG = 'evals/joint-discovery/catalog.json'
SUITE = 'evals/joint-discovery/cases.json'
PACKAGES = ('uni-skills', 'unif-portal-dev-skills')


class Entry(TypedDict):
    name: str
    description: str
    package: str
    path: str
    source_sha256: str


class Catalog(TypedDict):
    formatVersion: int
    sources: dict[str, str]
    skills: list[Entry]
    sha256: str


def catalog_digest(sources: Mapping[str, str], skills: Sequence[Entry]) -> str:
    return evaluator.digest(evaluator.encode({'sources': sources, 'skills': skills}).encode())


def parse_catalog(value: object) -> Catalog:
    """验证冻结目录结构与内容摘要；来源 Git 字节另由 verify_sources 核实。"""
    if not evaluator.is_object(value) or type(value.get('formatVersion')) is not int or value['formatVersion'] != 1:
        raise evaluator.EvalError('联合目录 formatVersion 必须为 1')
    raw_sources, raw_skills = value.get('sources'), value.get('skills')
    if not evaluator.is_object(raw_sources) or set(raw_sources) != set(PACKAGES):
        raise evaluator.EvalError('联合目录必须包含 Uni 与 Unif 两个来源')
    sources: dict[str, str] = {}
    for package, revision in raw_sources.items():
        if not isinstance(revision, str) or not re.fullmatch(r'[0-9a-f]{40}', revision):
            raise evaluator.EvalError('目录来源必须为固定 Git 提交')
        sources[package] = revision
    if not evaluator.is_array(raw_skills) or not raw_skills:
        raise evaluator.EvalError('联合目录 skills 必须非空')
    entries: list[Entry] = []
    names: set[str] = set()
    for item in raw_skills:
        if not evaluator.is_object(item):
            raise evaluator.EvalError('目录条目必须为对象')
        name, description, package = item.get('name'), item.get('description'), item.get('package')
        path, digest = item.get('path'), item.get('source_sha256')
        if (not isinstance(name, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name)
                or name in names or not isinstance(description, str) or not description.strip()
                or not isinstance(package, str) or package not in sources
                or not isinstance(path, str) or not path.endswith('/SKILL.md')
                or not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest)):
            raise evaluator.EvalError('目录名称重复或来源字段无效')
        _ = evaluator.safe_path(path)
        names.add(name)
        entries.append({'name': name, 'description': description, 'package': package,
                        'path': path, 'source_sha256': digest})
    if {entry['package'] for entry in entries} != set(PACKAGES):
        raise evaluator.EvalError('两包均须提供技能条目')
    expected = catalog_digest(sources, entries)
    if value.get('sha256') != expected:
        raise evaluator.EvalError('联合目录内容与摘要不一致，请从指定来源重新冻结')
    return {'formatVersion': 1, 'sources': sources, 'skills': entries, 'sha256': expected}


def read_json(path: Path) -> object:
    raw = path.read_bytes()
    if len(raw) > evaluator.MAX_SUITE_BYTES:
        raise evaluator.EvalError('联合评测输入超过大小上限')
    return evaluator.load_json(raw)


def freeze(uni_repo: Path, uni_ref: str, unif_repo: Path, unif_ref: str) -> Catalog:
    """仅从显式指定提交读取技能 metadata，不读取工作区或本机安装。"""
    sources: dict[str, str] = {}
    entries: list[Entry] = []
    for package, repo, revision in zip(PACKAGES, (uni_repo, unif_repo), (uni_ref, unif_ref), strict=True):
        snapshot = evaluator.Snapshot(repo, revision)
        manifest = evaluator.load_json(snapshot.read('plugin.json'))
        if not evaluator.is_object(manifest) or manifest.get('name') != package:
            raise evaluator.EvalError('来源仓库身份不符：' + package)
        sources[package] = snapshot.commit
        for name in snapshot.skill_names():
            path = snapshot.skill_dir(name) + '/SKILL.md'
            raw = snapshot.read(path)
            metadata = evaluator.skill_metadata(raw.decode('utf-8'), name)
            entries.append({'name': name, 'description': metadata['description'], 'package': package,
                            'path': path, 'source_sha256': evaluator.digest(raw)})
    return parse_catalog({'formatVersion': 1, 'sources': sources, 'skills': entries,
                          'sha256': catalog_digest(sources, entries)})


def verify_sources(catalog: Catalog, uni_repo: Path, unif_repo: Path) -> None:
    current = freeze(uni_repo, catalog['sources']['uni-skills'],
                     unif_repo, catalog['sources']['unif-portal-dev-skills'])
    if current != catalog:
        raise evaluator.EvalError('冻结目录与固定来源提交不一致')


def read_cases(path: Path, catalog: Catalog) -> list[evaluator.Case]:
    """联合目录是专项发现集，不要求每个技能包含单包的三种评测模式。"""
    suite = read_json(path)
    if not evaluator.is_object(suite) or type(suite.get('formatVersion')) is not int or suite['formatVersion'] != 1:
        raise evaluator.EvalError('联合题库 formatVersion 必须为 1')
    cases = suite.get('cases')
    if not evaluator.is_array(cases) or not cases:
        raise evaluator.EvalError('联合题库 cases 必须非空')
    names = [entry['name'] for entry in catalog['skills']]
    identifiers: set[str] = set()
    validated: list[evaluator.Case] = []
    for case in cases:
        if not evaluator.validate_case(case, names, identifiers):
            raise evaluator.EvalError('联合题目格式无效')
        if case['mode'] not in ('discovery_positive', 'discovery_negative'):
            raise evaluator.EvalError('联合入口只支持目录发现，不执行技能应用')
        validated.append(case)
    return validated


def validate(catalog_path: Path, suite_path: Path) -> tuple[Catalog, list[evaluator.Case]]:
    catalog = parse_catalog(read_json(catalog_path))
    return catalog, read_cases(suite_path, catalog)


def run(catalog_path: Path, suite_path: Path, output: Path, *, repeats: int = 5,
        case_ids: Sequence[str] = (), env: Mapping[str, str] | None = None) -> int:
    """每题独立上下文；仅保存集合判定证据，不推断实际宿主加载或效果改善。"""
    if output.resolve().is_relative_to(ROOT.resolve()):
        raise evaluator.EvalError('联合评测运行记录必须放在仓库外')
    output.mkdir(parents=True, exist_ok=False)
    report: dict[str, object] = {'formatVersion': 1, 'status': 'insufficient', 'requests_used': 0,
        'scope': '联合目录发现集合判定；不证明宿主加载、技能应用、业务验收或相对改善',
        'harness_sha256': {'joint': evaluator.digest(Path(__file__).read_bytes()),
                           'behavior': evaluator.digest(Path(evaluator.__file__).read_bytes())}}
    client: evaluator.ChatCompletionsClient | None = None
    samples: list[evaluator.Sample] = []
    try:
        catalog, cases = validate(catalog_path, suite_path)
        if not 1 <= repeats <= 100:
            raise evaluator.EvalError('repeats 必须在 1 到 100 之间')
        unknown = set(case_ids) - {case['id'] for case in cases}
        if unknown:
            raise evaluator.EvalError('未知题号：' + ', '.join(sorted(unknown)))
        selected = [case for case in cases if not case_ids or case['id'] in case_ids]
        report.update(catalog_sha256=catalog['sha256'], suite_sha256=evaluator.digest(suite_path.read_bytes()),
                      sources=catalog['sources'], case_ids=[case['id'] for case in selected], repeats=repeats)
        _ = (output / 'catalog.json').write_bytes(catalog_path.read_bytes())
        _ = (output / 'cases.json').write_bytes(suite_path.read_bytes())
        config = evaluator.configuration(os.environ if env is None else env)
        report['config'] = {key: value for key, value in config.items() if key != 'api_key'}
        client = evaluator.ChatCompletionsClient(config)
        metadata = [{'name': entry['name'], 'description': entry['description']} for entry in catalog['skills']]
        for case in selected:
            for repetition in range(1, repeats + 1):
                sample = evaluator.evaluate_sample(client, case, {}, metadata, catalog['sha256'])
                sample.update(repeat=repetition, catalog_sha256=catalog['sha256'])
                evaluator.write_json(output / 'samples' / case['id'] / f'{repetition}.json', sample)
                samples.append(sample)
        complete = all(sample['status'] == 'complete' for sample in samples)
        passed = sum(sample['status'] == 'complete' and all(sample['scores']) for sample in samples)
        models = sorted({model for sample in samples for model in sample['actual_models']['answer']})
        report.update(status=('passed' if passed == len(samples) else 'failed') if complete else 'insufficient',
                      expected_samples=len(selected) * repeats, completed_samples=sum(
                          sample['status'] == 'complete' for sample in samples), passed_samples=passed,
                      actual_models=models, usage={key: sum(sample['usage'][key] for sample in samples)
                                                  for key in evaluator.USAGE_FIELDS},
                      usage_complete=all(sample['usage_complete'] for sample in samples))
        if len(models) > 1:
            report.update(status='insufficient', reason='实际返回模型版本不一致，结果仅逐样本保留')
    except (ValueError, OSError, KeyError, TypeError) as error:
        report.update(status='insufficient', reason=str(error))
    if client is not None:
        report.update(requests_used=client.requests_used, request_errors=client.request_errors)
    evaluator.write_json(output / 'report.json', report)
    print('联合目录发现：' + str(report['status']) + '；报告：' + str(output / 'report.json'))
    return 0 if report['status'] == 'passed' else 1 if report['status'] == 'failed' else 2


class Arguments(argparse.Namespace):
    command: str = ''
    catalog: Path = ROOT / CATALOG
    suite: Path = ROOT / SUITE
    uni_repo: Path | None = None
    unif_repo: Path | None = None
    uni_ref: str = ''
    unif_ref: str = ''
    output: Path | None = None
    repeats: int = 5
    case: list[str] | None = None


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('freeze', 'validate', 'verify-sources', 'run'):
        item = commands.add_parser(command)
        _ = item.add_argument('--catalog', type=Path, default=ROOT / CATALOG)
        if command in ('freeze', 'verify-sources'):
            _ = item.add_argument('--uni-repo', type=Path, required=True)
            _ = item.add_argument('--unif-repo', type=Path, required=True)
        if command == 'freeze':
            _ = item.add_argument('--uni-ref', required=True)
            _ = item.add_argument('--unif-ref', required=True)
        if command in ('validate', 'run'):
            _ = item.add_argument('--suite', type=Path, default=ROOT / SUITE)
        if command == 'run':
            _ = item.add_argument('--output', type=Path, required=True)
            _ = item.add_argument('--repeats', type=int, default=5)
            _ = item.add_argument('--case', action='append')
    args = parser.parse_args(argv, namespace=Arguments())
    try:
        if args.command == 'freeze' and args.uni_repo is not None and args.unif_repo is not None:
            catalog = freeze(args.uni_repo, args.uni_ref, args.unif_repo, args.unif_ref)
            evaluator.write_json(args.catalog, catalog)
            print(f'已冻结 {len(catalog["skills"])} 个技能；摘要 {catalog["sha256"]}')
        elif args.command == 'verify-sources' and args.uni_repo is not None and args.unif_repo is not None:
            verify_sources(parse_catalog(read_json(args.catalog)), args.uni_repo, args.unif_repo)
            print('联合目录与两个固定来源提交一致')
        elif args.command == 'validate':
            catalog, cases = validate(args.catalog, args.suite)
            print(f'联合目录校验通过：{len(catalog["skills"])} 个技能、{len(cases)} 道专项发现题')
        elif args.command == 'run' and args.output is not None:
            return run(args.catalog, args.suite, args.output, repeats=args.repeats, case_ids=args.case or [])
        else:
            raise evaluator.EvalError('缺少命令参数')
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
