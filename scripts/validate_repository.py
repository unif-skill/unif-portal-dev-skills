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


def validate_repository(root):
    root = Path(root).resolve()
    schema = read_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    check_plugin(root, validator)
    check_marketplace(root, validator)
    skill_count = check_skills(root)
    run_count, file_count = check_evaluations(root)
    return skill_count, run_count, file_count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        skills, runs, files = validate_repository(args.root)
    except (ValueError, OSError) as error:
        parser.exit(1, f'校验失败：{error}\n')
    print(f'校验通过：{skills} 个技能、{runs} 份评测清单、{files} 个冻结文件。')


if __name__ == '__main__':
    main()
