#!/usr/bin/env python3
"""只读校验技能分发包；--include-evals 另校验本地评测记录。"""

import argparse
import hashlib
import json
import re
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple, Protocol, TypeGuard, cast
from urllib.parse import unquote, urlsplit

import yaml
from jsonschema import Draft202012Validator, ValidationError
from markdown_it import MarkdownIt
from skills_ref import validate as validate_skill

SCHEMA = Path(__file__).resolve().parent / 'schemas/plugin.schema.json'
DEFAULT_PLUGIN = 'unif-platform-rules'
BUSINESS_PLUGINS = {
    'unif-engineering-skills', 'unif-react-native-skills', 'unif-harmony-skills',
    'unif-python-skills', 'unif-library-skills',
}


def is_object(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict) and all(isinstance(key, str) for key in cast(dict[object, object], value))


def is_list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def read_json(path: Path) -> dict[str, object]:
    try:
        value: object = cast(object, json.loads(path.read_text(encoding='utf-8')))
        if not is_object(value):
            raise ValueError('必须是 JSON 对象')
        return value
    except (OSError, ValueError) as error:
        raise ValueError(f'{path}: {error}') from error


def contained_path(root: Path, base: Path, target: object, *, directory: bool = False) -> Path:
    if not isinstance(target, str) or not target or Path(target).is_absolute():
        raise ValueError(f'{base}: 非法相对路径 {target!r}')
    path = (base / target).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'{base}: 引用越出分发目录 {target}')
    if not (path.is_dir() if directory else path.is_file()):
        raise ValueError(f'{base}: 引用不存在 {target}')
    return path


def check_package_files(directory: Path) -> None:
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError(f'{directory}: 插件目录须为普通目录')
    for path in directory.rglob('*'):
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise ValueError(f'{path}: 插件只可包含普通文件和目录')


def check_assets(root: Path, interface: object, fields: Sequence[str]) -> None:
    if not is_object(interface):
        raise ValueError(f'{root}: interface 必须是对象')
    for field in fields:
        if field in interface:
            _ = contained_path(root, root, interface[field])


class PluginValidator(Protocol):
    def validate(self, instance: object, /) -> None: ...


def check_plugin(root: Path, validator: PluginValidator) -> dict[str, object]:
    path = root / 'plugin.json'
    manifest = read_json(path)
    try:
        validator.validate(manifest)
    except ValidationError as error:
        raise ValueError(f'{path}: {error.message}') from error
    version = manifest.get('version')
    if not isinstance(version, str) or not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', version):
        raise ValueError(f'{path}: version 必须是无前缀、无前导零的 X.Y.Z 版本号')
    if int(version.split('.')[0]) not in (0, 1):
        raise ValueError(f'{path}: 当前校验支持 0.x／1.x；主版本变化须单独明确授权')
    extensions = manifest.get('extensions', {})
    openai = extensions.get('com.openai', {}) if is_object(extensions) else None
    interface = openai.get('interface', {}) if is_object(openai) else None
    check_assets(root, interface, ('composerIcon', 'logo', 'logoDark'))
    screenshots = interface.get('screenshots', list[object]()) if is_object(interface) else list[object]()
    if not is_list(screenshots):
        raise ValueError(f'{path}: screenshots 必须是数组')
    for screenshot in screenshots:
        _ = contained_path(root, root, screenshot)
    return manifest


def check_marketplace(root: Path, validator: PluginValidator, *, release_version: object = None) -> dict[str, tuple[str, str]]:
    path = root / '.agents/plugins/marketplace.json'
    data = read_json(path)
    if not re.fullmatch(r'[A-Za-z0-9_-]+', str(data.get('name', ''))):
        raise ValueError(f'{path}: 缺少合法市场名称')
    entries = data.get('plugins')
    if not is_list(entries) or not entries:
        raise ValueError(f'{path}: plugins 必须是非空数组')
    packages: dict[str, tuple[str, str]] = {}
    for entry in entries:
        if not is_object(entry):
            raise ValueError(f'{path}: 插件条目必须是对象')
        source = entry.get('source', {})
        if not is_object(source) or source.get('source') != 'local':
            raise ValueError(f'{path}: 本仓市场条目须引用仓内标准插件')
        location = source.get('path')
        if not isinstance(location, str):
            raise ValueError(f'{path}: 插件路径必须是字符串')
        plugin_root = contained_path(root, root, location, directory=True)
        if release_version is not None:
            if location != './plugins/' + plugin_root.name:
                raise ValueError(f'{path}: 插件路径须指向 plugins/ 的直属目录')
            check_package_files(root / location)
        plugin = check_plugin(plugin_root, validator)
        if release_version is not None and plugin['version'] != release_version:
            raise ValueError(f'{plugin_root}/plugin.json: 插件版本须与本仓版本一致')
        name = entry.get('name')
        if not isinstance(name, str) or name != plugin['name'] or name in packages:
            raise ValueError(f'{path}: 插件名称不匹配或重复 {entry.get("name")}')
        policy = entry.get('policy', {})
        install = policy.get('installation') if is_object(policy) else None
        if (not is_object(policy) or not isinstance(install, str)
                or install not in ('AVAILABLE', 'NOT_AVAILABLE', 'INSTALLED_BY_DEFAULT')
                or policy.get('authentication') not in ('ON_INSTALL', 'ON_USE')):
            raise ValueError(f'{path}: 非法安装或认证策略')
        category = entry.get('category')
        if not isinstance(category, str) or not category.strip():
            raise ValueError(f'{path}: 缺少 category')
        packages[name] = location, install
    return packages


def check_markdown(root: Path, path: Path) -> None:
    pending = list(MarkdownIt('commonmark').parse(path.read_text(encoding='utf-8')))
    while pending:
        token = pending.pop()
        pending.extend(token.children or [])
        target = token.attrGet('href') if token.type == 'link_open' else token.attrGet('src')
        if not isinstance(target, str) or not target:
            continue
        url = urlsplit(target)
        if url.scheme and url.scheme != 'file':
            continue
        if url.path:
            _ = contained_path(root, path.parent, unquote(url.path))


def source_section(value: object, size: int, where: str) -> tuple[str, int, int]:
    heading = value.get('heading') if is_object(value) else None
    lines = value.get('lines') if is_object(value) else None
    if isinstance(heading, str) and is_list(lines) and len(lines) == 2:
        start, end = lines
        if type(start) is int and type(end) is int and 1 <= start <= end <= size:
            return heading, start, end
    raise ValueError(f'{where}：{lines!r}')


class SourceCoverage(NamedTuple):
    digest: str
    lines: int
    spans: list[tuple[int, int]]


def check_complete_coverage(spans: list[tuple[int, int]], size: int, label: str) -> None:
    next_line = 1
    for start, end in sorted(spans):
        if start != next_line:
            raise ValueError(f'{label} 源章节重复或缺失')
        next_line = end + 1
    if next_line != size + 1:
        raise ValueError(f'{label} 源章节缺失')


def check_generated_references(skill: Path, coverage: dict[str, SourceCoverage] | None = None) -> None:
    directory = skill / 'references'
    generated = {str(p.relative_to(directory)) for p in directory.rglob('*.md')
                 if p.read_text(encoding='utf-8').startswith('<!-- 此文件由 scripts/sync_architecture.py 生成')}
    manifest = directory / 'source.json'
    if not generated and not manifest.exists():
        return
    _ = contained_path(skill, directory, 'source.json')
    data = read_json(manifest)
    if data.get('formatVersion') != 2:
        raise ValueError(f'{manifest}: 不支持的来源记录格式')
    sources, files = data.get('sources'), data.get('files')
    if not is_object(sources) or not sources or not is_object(files) or not files:
        raise ValueError(f'{manifest}: sources 和 files 必须是非空对象')
    if generated - files.keys():
        raise ValueError(f'{manifest}: 未登记的生成资料 {sorted(generated - files.keys())}')
    counts: dict[str, int] = {}
    expected: dict[str, list[tuple[str, int, int]]] = {}
    selected: dict[str, list[tuple[str, int, int]]] = {name: [] for name in sources}
    for name, info in sources.items():
        size = info.get('lines') if is_object(info) else None
        if (not is_object(info) or not isinstance(info.get('source'), str)
                or not re.fullmatch(r'[0-9a-f]{64}', str(info.get('sha256', '')))
                or type(size) is not int or size < 1):
            raise ValueError(f'{manifest}: {name} 来源或摘要无效')
        counts[name] = size
        if coverage is not None:
            digest = str(info['sha256'])
            if name not in coverage:
                coverage[name] = SourceCoverage(digest, size, [])
            elif (coverage[name].digest, coverage[name].lines) != (digest, size):
                raise ValueError(f'{manifest}: {name} 与其他插件的规范源版本不一致')
        if 'selectedSections' in info:
            declarations = info['selectedSections']
            if not is_list(declarations) or not declarations:
                raise ValueError(f'{manifest}: {name} 选取范围无效')
            expected[name] = [source_section(item, size, f'{manifest}: {name} 选取章节无效')
                              for item in declarations]
    for name, record in files.items():
        path = contained_path(directory, directory, name)
        if not is_object(record) or hashlib.sha256(path.read_bytes()).hexdigest() != record.get('sha256'):
            raise ValueError(f'{manifest}: {name} SHA-256 不匹配')
        sections = record.get('sections')
        if not is_list(sections) or not sections:
            raise ValueError(f'{manifest}: {name} 缺少源章节')
        for section in sections:
            if not is_object(section):
                raise ValueError(f'{manifest}: {name} 非法源章节')
            source = section.get('source')
            if not isinstance(source, str) or source not in counts:
                raise ValueError(f'{manifest}: {name} 未知来源 {source!r}')
            selected[source].append(source_section(section, counts[source], f'{manifest}: {name} 非法源行段'))
    for source, actual in selected.items():
        ordered = sorted((start, end) for _, start, end in actual)
        if coverage is not None:
            coverage[source].spans.extend(ordered)
        if source in expected:
            claimed = expected[source]
            if (sorted(actual) != sorted(claimed) or len({title for title, _, _ in claimed}) != len(claimed)
                    or any(start <= previous[1] for previous, (start, _) in zip(ordered, ordered[1:]))):
                raise ValueError(f'{manifest}: {source} 选取章节重复或缺失')
            continue
        check_complete_coverage(ordered, counts[source], f'{manifest}: {source}')


def check_organization_profile(skill: Path) -> None:
    path = skill / 'assets/organization.json'
    if not path.exists():
        return
    _ = contained_path(skill, skill, 'assets/organization.json')
    data = read_json(path)
    required = {'schemaVersion', 'owner', 'namePattern', 'pagesURL', 'releaseAppId',
                'repositorySettings', 'security', 'obsoleteFiles'}
    if set(data) != required or type(data['schemaVersion']) is not int or data['schemaVersion'] != 1:
        raise ValueError(f'{path}: organization 字段或版本无效')
    app_id = data['releaseAppId']
    if (data['owner'] != 'unif-design'
            or data['namePattern'] != r'^@unif/react-native-[a-z0-9]+(?:-[a-z0-9]+)*$'
            or data['pagesURL'] != 'https://unif-design.github.io/{repo}/'
            or type(app_id) is not int or app_id <= 0):
        raise ValueError(f'{path}: organization 身份、命名或 Pages 配置无效')
    settings = data['repositorySettings']
    flags = {'allow_merge_commit', 'allow_squash_merge', 'allow_rebase_merge',
             'allow_auto_merge', 'delete_branch_on_merge', 'has_issues'}
    if (not is_object(settings) or set(settings) != flags | {'security_and_analysis'}
            or any(type(settings[key]) is not bool for key in flags)):
        raise ValueError(f'{path}: organization 仓库设置字段无效')
    analysis = settings['security_and_analysis']
    if (not is_object(analysis) or set(analysis) != {'secret_scanning', 'secret_scanning_push_protection'}
            or any(value != {'status': 'enabled'} for value in analysis.values())):
        raise ValueError(f'{path}: organization 安全扫描配置无效')
    security = data['security']
    if (not is_object(security) or security != {'codeqlDefaultSetup': 'not-configured', 'dependabotSecurityUpdates': 'disabled',
                            'privateVulnerabilityReporting': True}
            or type(security['privateVulnerabilityReporting']) is not bool):
        raise ValueError(f'{path}: organization 安全策略无效')
    obsolete = data['obsoleteFiles']
    expected = {'.github/dependabot.yaml', '.github/workflows/dependabot-auto-merge.yml',
                '.github/workflows/dependabot-automerge.yml'}
    if (not is_list(obsolete) or any(not isinstance(name, str) for name in obsolete)
            or len(obsolete) != len(expected) or set(obsolete) != expected):
        raise ValueError(f'{path}: organization 停用文件清单无效')


def check_skills(root: Path, *, standalone: bool = True, seen: set[str] | None = None,
                 coverage: dict[str, SourceCoverage] | None = None) -> int:
    directory = contained_path(root, root, 'skills', directory=True)
    skills = sorted(p for p in directory.iterdir() if p.is_dir())
    if not skills:
        raise ValueError(f'{directory}: 没有可分发技能')
    for skill in skills:
        _ = contained_path(root, directory, skill.name, directory=True)
        if seen is not None:
            if skill.name in seen:
                raise ValueError(f'{skill}: 技能名称已由其他插件提供')
            seen.add(skill.name)
        errors = validate_skill(skill)
        if errors:
            raise ValueError(f'{skill}: {"; ".join(errors)}')
        for path in skill.rglob('*.md'):
            _ = contained_path(skill, skill, str(path.relative_to(skill)))
            check_markdown(skill if standalone else root, path)
        check_generated_references(skill, coverage)
        check_organization_profile(skill)
        metadata = skill / 'agents/openai.yaml'
        if metadata.exists():
            _ = contained_path(skill, skill, 'agents/openai.yaml')
            try:
                data = cast(object, yaml.safe_load(metadata.read_text(encoding='utf-8')))
            except yaml.YAMLError as error:
                raise ValueError(f'{metadata}: {error}') from error
            if not is_object(data):
                raise ValueError(f'{metadata}: 必须是对象')
            check_assets(skill, data.get('interface', {}), ('icon_small', 'icon_large'))
    return len(skills)


def check_evaluations(root: Path) -> tuple[int, int]:
    runs = sorted(p for p in (root / 'evals').glob('*/runs/*') if p.is_dir())
    count = 0
    for run in runs:
        manifest = run / 'manifest.json'
        data = read_json(manifest)
        files = data.get('files')
        if not is_object(files) or not files:
            raise ValueError(f'{manifest}: files 必须包含冻结文件及其摘要')
        for name, record in files.items():
            path = contained_path(run, run, name)
            if not is_object(record) or not re.fullmatch(r'[0-9a-f]{64}', str(record.get('sha256', ''))):
                raise ValueError(f'{manifest}: {name} 缺少合法 SHA-256')
            content = path.read_bytes()
            if hashlib.sha256(content).hexdigest() != record['sha256']:
                raise ValueError(f'{manifest}: {name} SHA-256 不匹配')
            for size in ('bytes', 'utf8Bytes'):
                if size in record and len(content) != record[size]:
                    raise ValueError(f'{manifest}: {name} {size} 不匹配')
            count += 1
    return len(runs), count


def validate_repository(root: Path | str, release_tag: str | None = None, include_evals: bool = False) -> tuple[int, int, int]:
    root = Path(root).resolve()
    schema = read_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    for filename in ('plugin.json', 'LICENSE'):
        path = root / filename
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise ValueError(f'{path}: 须为普通文件')
    plugin = check_plugin(root, validator)
    if release_tag is not None and release_tag != f'v{plugin["version"]}':
        raise ValueError(f'发布 tag {release_tag!r} 与 plugin.json version {plugin["version"]!r} 不一致')
    if (root / 'plugins').exists() or plugin['name'] == 'unif-portal-dev-skills':
        if (root / 'skills').exists() or (root / 'skills').is_symlink():
            raise ValueError('请直接维护各插件内的技能；根 skills/ 会产生重复入口')
        packages_dir = root / 'plugins'
        if packages_dir.is_symlink() or not packages_dir.is_dir():
            raise ValueError(f'{packages_dir}: 缺少插件目录或使用了符号链接')
        distributed = {p.name for p in packages_dir.iterdir() if p.is_dir() or p.is_symlink()}
        if distributed != BUSINESS_PLUGINS | {DEFAULT_PLUGIN}:
            raise ValueError('插件目录与六个市场入口不一致')
        entries = check_marketplace(root, validator, release_version=plugin['version'])
        expected = {name: ('./plugins/' + name, 'AVAILABLE') for name in BUSINESS_PLUGINS}
        expected[DEFAULT_PLUGIN] = './plugins/' + DEFAULT_PLUGIN, 'INSTALLED_BY_DEFAULT'
        if entries != expected:
            raise ValueError('市场必须默认安装公共规范，五个业务插件按需安装，并分别指向对应目录')
        seen: set[str] = set()
        coverage: dict[str, SourceCoverage] = {}
        for name in entries:
            _ = check_skills(packages_dir / name, standalone=False, seen=seen, coverage=coverage)
        for name, record in coverage.items():
            check_complete_coverage(record.spans, record.lines, name)
        skill_count = len(seen)
    else:
        _ = check_marketplace(root, validator)
        skill_count = check_skills(root, standalone=True)
    run_count, file_count = check_evaluations(root) if include_evals else (0, 0)
    return skill_count, run_count, file_count


class Arguments(argparse.Namespace):
    root: Path = Path(__file__).resolve().parents[1]
    release_tag: str | None = None
    include_evals: bool = False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    _ = parser.add_argument('--release-tag', help='发布时核对 vX.Y.Z tag 与插件版本一致')
    _ = parser.add_argument('--include-evals', action='store_true', help='同时校验本地 runs 中的评测清单和文件摘要')
    args = parser.parse_args(namespace=Arguments())
    try:
        skills, runs, files = validate_repository(
            args.root, release_tag=args.release_tag, include_evals=args.include_evals,
        )
    except (ValueError, OSError) as error:
        parser.exit(1, f'校验失败：{error}\n')
    detail = f'、{runs} 份评测清单、{files} 个冻结文件' if args.include_evals else ''
    print(f'校验通过：{skills} 个技能{detail}。')


if __name__ == '__main__':
    main()
