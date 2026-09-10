#!/usr/bin/env python3
"""只读校验技能分发包及评测记录；不调用模型或修改生成文件。"""

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from jsonschema import Draft202012Validator
from markdown_it import MarkdownIt
from skills_ref import validate as validate_skill

SCHEMA = Path(__file__).resolve().parent / 'schemas/plugin.schema.json'


def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise ValueError(f'{path}: {error}') from error


def contained_path(root, base, target, *, directory=False):
    if not isinstance(target, str) or not target or Path(target).is_absolute():
        raise ValueError(f'{base}: 非法相对路径 {target!r}')
    path = (base / target).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'{base}: 引用越出分发目录 {target}')
    if not (path.is_dir() if directory else path.is_file()):
        raise ValueError(f'{base}: 引用不存在 {target}')
    return path


def check_assets(root, interface, fields):
    if not isinstance(interface, dict):
        raise ValueError(f'{root}: interface 必须是对象')
    for field in fields:
        if field in interface:
            contained_path(root, root, interface[field])


def check_plugin(root, validator):
    path = root / 'plugin.json'
    manifest = read_json(path)
    errors = list(validator.iter_errors(manifest))
    if errors:
        raise ValueError(f'{path}: {errors[0].message}')
    if not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', manifest.get('version', '')):
        raise ValueError(f'{path}: version 必须是无前缀、无前导零的 X.Y.Z 版本号')
    interface = manifest.get('extensions', {}).get('com.openai', {}).get('interface', {})
    check_assets(root, interface, ('composerIcon', 'logo', 'logoDark'))
    for screenshot in interface.get('screenshots', []):
        contained_path(root, root, screenshot)
    return manifest


def check_marketplace(root, validator):
    path = root / '.agents/plugins/marketplace.json'
    data = read_json(path)
    if not isinstance(data, dict) or not re.fullmatch(r'[A-Za-z0-9_-]+', str(data.get('name', ''))):
        raise ValueError(f'{path}: 缺少合法市场名称')
    entries = data.get('plugins')
    if not isinstance(entries, list) or not entries:
        raise ValueError(f'{path}: plugins 必须是非空数组')
    names = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError(f'{path}: 插件条目必须是对象')
        source = entry.get('source', {})
        if not isinstance(source, dict) or source.get('source') != 'local':
            raise ValueError(f'{path}: 本仓市场条目须引用仓内标准插件')
        plugin_root = contained_path(root, root, source.get('path'), directory=True)
        plugin = check_plugin(plugin_root, validator)
        if entry.get('name') != plugin['name'] or plugin['name'] in names:
            raise ValueError(f'{path}: 插件名称不匹配或重复 {entry.get("name")}')
        names.add(plugin['name'])
        policy = entry.get('policy', {})
        if (not isinstance(policy, dict)
                or policy.get('installation') not in ('AVAILABLE', 'NOT_AVAILABLE', 'INSTALLED_BY_DEFAULT')
                or policy.get('authentication') not in ('ON_INSTALL', 'ON_USE')):
            raise ValueError(f'{path}: 非法安装或认证策略')
        if not isinstance(entry.get('category'), str) or not entry['category'].strip():
            raise ValueError(f'{path}: 缺少 category')


def check_markdown(root, path):
    pending = list(MarkdownIt('commonmark').parse(path.read_text(encoding='utf-8')))
    while pending:
        token = pending.pop()
        pending.extend(token.children or [])
        target = token.attrGet('href') if token.type == 'link_open' else token.attrGet('src')
        if not target:
            continue
        url = urlsplit(target)
        if url.scheme and url.scheme != 'file':
            continue
        if url.path:
            contained_path(root, path.parent, unquote(url.path))


def check_generated_references(skill):
    directory = skill / 'references'
    generated = {p.name for p in directory.glob('*.md')
                 if p.read_text(encoding='utf-8').startswith('<!-- 此文件由 scripts/sync_architecture.py 生成')}
    manifest = directory / 'source.json'
    if not generated and not manifest.exists():
        return
    contained_path(skill, directory, 'source.json')
    data = read_json(manifest)
    if not isinstance(data, dict) or data.get('formatVersion') != 2:
        raise ValueError(f'{manifest}: 不支持的来源记录格式')
    sources, files = data.get('sources'), data.get('files')
    if not isinstance(sources, dict) or not sources or not isinstance(files, dict) or not files:
        raise ValueError(f'{manifest}: sources 和 files 必须是非空对象')
    if generated - files.keys():
        raise ValueError(f'{manifest}: 未登记的生成资料 {sorted(generated - files.keys())}')
    covered = {name: [] for name in sources}
    for name, source in sources.items():
        if (not isinstance(source, dict) or not isinstance(source.get('source'), str)
                or not re.fullmatch(r'[0-9a-f]{64}', str(source.get('sha256', '')))
                or type(source.get('lines')) is not int or source['lines'] < 1):
            raise ValueError(f'{manifest}: {name} 来源或摘要无效')
    for name, record in files.items():
        path = contained_path(skill, directory, name)
        if (not isinstance(record, dict)
                or hashlib.sha256(path.read_bytes()).hexdigest() != record.get('sha256')):
            raise ValueError(f'{manifest}: {name} SHA-256 不匹配')
        sections = record.get('sections')
        if not isinstance(sections, list) or not sections:
            raise ValueError(f'{manifest}: {name} 缺少源章节')
        for section in sections:
            if not isinstance(section, dict):
                raise ValueError(f'{manifest}: {name} 非法源章节')
            source, lines = section.get('source'), section.get('lines')
            if not isinstance(source, str) or source not in sources:
                raise ValueError(f'{manifest}: {name} 未知来源 {source!r}')
            if (not isinstance(section.get('heading'), str) or not isinstance(lines, list)
                    or len(lines) != 2 or any(type(n) is not int for n in lines)
                    or not 1 <= lines[0] <= lines[1] <= sources[source]['lines']):
                raise ValueError(f'{manifest}: {name} 非法源行段 {lines!r}')
            covered[source].append(lines)
    for source, spans in covered.items():
        next_line = 1
        for start, end in sorted(spans):
            if start != next_line:
                raise ValueError(f'{manifest}: {source} 源章节重复或缺失')
            next_line = end + 1
        if next_line != sources[source]['lines'] + 1:
            raise ValueError(f'{manifest}: {source} 源章节缺失')


def check_skills(root):
    directory = contained_path(root, root, 'skills', directory=True)
    skills = sorted(p for p in directory.iterdir() if p.is_dir())
    if not skills:
        raise ValueError(f'{directory}: 没有可分发技能')
    for skill in skills:
        contained_path(root, directory, skill.name, directory=True)
        errors = validate_skill(skill)
        if errors:
            raise ValueError(f'{skill}: {"; ".join(errors)}')
        for path in skill.rglob('*.md'):
            contained_path(skill, skill, str(path.relative_to(skill)))
            check_markdown(skill, path)
        check_generated_references(skill)
        metadata = skill / 'agents/openai.yaml'
        if metadata.exists():
            contained_path(skill, skill, 'agents/openai.yaml')
            try:
                data = yaml.safe_load(metadata.read_text(encoding='utf-8'))
            except yaml.YAMLError as error:
                raise ValueError(f'{metadata}: {error}') from error
            if not isinstance(data, dict):
                raise ValueError(f'{metadata}: 必须是对象')
            check_assets(skill, data.get('interface', {}), ('icon_small', 'icon_large'))
    return len(skills)


def check_evaluations(root):
    runs = sorted(p for p in (root / 'evals').glob('*/runs/*') if p.is_dir())
    count = 0
    for run in runs:
        manifest = run / 'manifest.json'
        data = read_json(manifest)
        files = data.get('files') if isinstance(data, dict) else None
        if not isinstance(files, dict) or not files:
            raise ValueError(f'{manifest}: files 必须包含冻结文件及其摘要')
        for name, record in files.items():
            path = contained_path(run, run, name)
            if not isinstance(record, dict) or not re.fullmatch(r'[0-9a-f]{64}', str(record.get('sha256', ''))):
                raise ValueError(f'{manifest}: {name} 缺少合法 SHA-256')
            content = path.read_bytes()
            if hashlib.sha256(content).hexdigest() != record['sha256']:
                raise ValueError(f'{manifest}: {name} SHA-256 不匹配')
            for size in ('bytes', 'utf8Bytes'):
                if size in record and len(content) != record[size]:
                    raise ValueError(f'{manifest}: {name} {size} 不匹配')
            count += 1
    return len(runs), count


def validate_repository(root, release_tag=None):
    root = Path(root).resolve()
    schema = read_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    plugin = check_plugin(root, validator)
    if release_tag is not None and release_tag != f'v{plugin["version"]}':
        raise ValueError(f'发布 tag {release_tag!r} 与 plugin.json version {plugin["version"]!r} 不一致')
    check_marketplace(root, validator)
    skill_count = check_skills(root)
    run_count, file_count = check_evaluations(root)
    return skill_count, run_count, file_count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--release-tag', help='发布时核对 vX.Y.Z tag 与插件版本一致')
    args = parser.parse_args()
    try:
        skills, runs, files = validate_repository(args.root, release_tag=args.release_tag)
    except (ValueError, OSError) as error:
        parser.exit(1, f'校验失败：{error}\n')
    print(f'校验通过：{skills} 个技能、{runs} 份评测清单、{files} 个冻结文件。')


if __name__ == '__main__':
    main()
