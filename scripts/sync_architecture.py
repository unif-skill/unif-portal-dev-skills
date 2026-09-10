#!/usr/bin/env python3
"""从规范源按主题生成技能资料；--check 只比较，不修改文件。"""

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

RELATIVE_LINK = re.compile(r'(?<!!)\[([^\]\n]+)\]\(([^)\s]+)\)')
MARKER = '<!-- 此文件由 scripts/sync_architecture.py 生成'
HEADER = MARKER + '，请修改规范源后重新同步。来源与章节见 source.json。 -->\n\n'
# 每个源章节仅分配一次；空标题表示首个二级标题之前的引言。
TOPICS = {
    'architecture-design': {
        'ARCHITECTURE.md': {
            'scope.md': ['', '1. 架构目标'],
            'responsibilities.md': ['2. 系统边界与职责'],
            'composition.md': ['3. 功能、场景与入口'],
            'state.md': ['4. 状态归属'],
            'agent-context.md': ['5. 自然语言任务与上下文'],
            'contracts.md': ['6. 跨边界交接与业务结果'],
            'verification.md': ['7. 独立开发与验证'],
            'cost.md': ['8. 成本与效果验证'],
            'documentation.md': ['9. 领域与模块文档'],
        },
    },
    'portal-development': {
        'PORTAL_DEVELOPMENT.md': {
            'scope.md': ['', '1. 文件变更入口', '2. 各类代码的开发规则'],
            'file-rules.md': ['3. 常量、类型、变量与文件拆分', '4. 命名与公开出口'],
            'testing.md': ['5. 规则执行与定向验证'],
        },
        'PORTAL_STRUCTURE.md': {
            'directory.md': ['', '1. 目标目录'],
            'ui.md': ['2. 基础组件与 UI 复用'],
            'utilities-config.md': ['3. 工具、常量、类型及其他文件的归属'],
            'dependencies.md': ['4. 公共入口与依赖方向', '5. 基础能力与资源归属'],
            'testing.md': ['6. 基础代码迁移与定向验证'],
        },
    },
}
LEGACY = {
    'architecture-design': {'platform-architecture.md'},
    'portal-development': {'portal-development.md', 'portal-structure.md'},
}


def portable_link(match):
    target = match.group(2)
    return match.group(0) if urlsplit(target).scheme or target.startswith('#') else match.group(1)


def split_sections(text):
    """保留原文和行号；代码围栏内的标题和示例链接不参与转换。"""
    lines = text.splitlines(keepends=True)
    sections = []
    heading, start, body, fence = '', 1, [], None
    for number, line in enumerate(lines, 1):
        if fence:
            body.append(line)
            if re.fullmatch(r' {0,3}' + re.escape(fence[0]) + '{' + str(len(fence)) + r',}\s*', line):
                fence = None
            continue
        opening = re.match(r' {0,3}(`{3,}|~{3,})', line)
        if opening:
            fence = opening[1]
            body.append(line)
            continue
        title = re.match(r'^## (.+?)\s*$', line)
        if title:
            sections.append((heading, start, number - 1, ''.join(body)))
            heading, start, body = title[1], number, []
        body.append(RELATIVE_LINK.sub(portable_link, line))
    sections.append((heading, start, len(lines), ''.join(body)))
    return sections


def render(sources, skill):
    outputs, records = {}, {}
    provenance = {'formatVersion': 2, 'transformation': 'section-text-portable-links-v2',
                  'sources': {}, 'files': records}
    for source_name, topics in TOPICS[skill].items():
        content = sources[source_name]
        sections = split_sections(content.decode('utf-8'))
        headings = [section[0] for section in sections]
        expected = [heading for selection in topics.values() for heading in selection]
        if (len(set(headings)) != len(headings) or len(set(expected)) != len(expected)
                or set(headings) != set(expected)):
            raise ValueError(f'{source_name}: 二级章节缺失、重复或未分配；请核对主题映射。'
                             f' 缺失={set(expected) - set(headings)}，未分配={set(headings) - set(expected)}')
        provenance['sources'][source_name] = {
            'source': 'unif-platform-architecture/' + source_name,
            'sha256': hashlib.sha256(content).hexdigest(),
            'lines': len(content.decode('utf-8').splitlines()),
        }
        by_heading = {section[0]: section for section in sections}
        for filename, selected in topics.items():
            for title in selected:
                heading, start, end, body = by_heading[title]
                outputs[filename] = outputs.get(filename, HEADER) + ('' if filename not in outputs else '\n') + body
                records.setdefault(filename, {'sections': []})['sections'].append({
                    'source': source_name, 'heading': heading, 'lines': [start, end],
                })
    for filename, content in outputs.items():
        records[filename]['sha256'] = hashlib.sha256(content.encode('utf-8')).hexdigest()
    outputs['source.json'] = json.dumps(provenance, ensure_ascii=False, indent=2) + '\n'
    return outputs


def obsolete_files(destination, skill, outputs):
    # 只清理明确属于本生成器的资料，不碰同目录的手工文件。
    candidates = set(LEGACY[skill])
    record = destination / 'source.json'
    if record.is_file():
        try:
            old = json.loads(record.read_text(encoding='utf-8'))
        except ValueError:
            old = {}
        if isinstance(old, dict) and old.get('formatVersion') == 2:
            if not isinstance(old.get('files'), dict):
                raise ValueError(f'{record}: 旧来源记录的 files 必须是对象')
            candidates.update(old['files'])
    obsolete = []
    for name in sorted(candidates - outputs.keys()):
        if not isinstance(name, str) or Path(name).name != name or not name.endswith('.md'):
            raise ValueError(f'非法旧生成文件名：{name!r}')
        path = destination / name
        if path.is_symlink():
            raise ValueError(f'生成路径不能是符号链接：{path}')
        if path.exists():
            if not path.read_text(encoding='utf-8').startswith(MARKER):
                raise ValueError(f'旧文件不是可清理的生成资料：{path}')
            obsolete.append(path)
    return obsolete


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--skill', choices=tuple(TOPICS), default='architecture-design',
                        help='architecture-design 接受规范文件；portal-development 接受规范目录')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    destination = Path(__file__).resolve().parents[1] / 'skills' / args.skill / 'references'
    try:
        sources = {name: (args.source if args.skill == 'architecture-design' else args.source / name).read_bytes()
                   for name in TOPICS[args.skill]}
        outputs = render(sources, args.skill)
        if destination.is_symlink() or destination.parent.is_symlink():
            raise ValueError(f'生成目录不能是符号链接：{destination}')
        for name in outputs:
            path = destination / name
            if path.is_symlink() or (path.exists() and not path.is_file()):
                raise ValueError(f'生成路径必须是普通文件：{path}')
        obsolete = obsolete_files(destination, args.skill, outputs)
        different = [name for name, expected in outputs.items()
                     if not (destination / name).is_file()
                     or (destination / name).read_text(encoding='utf-8') != expected]
        if args.check:
            different += [path.name for path in obsolete]
            if different:
                parser.exit(1, '规范资料或来源记录不一致：' + '、'.join(different) + '\n')
            print('规范资料与来源记录一致。')
            return
        destination.mkdir(parents=True, exist_ok=True)
        for name in different:
            (destination / name).write_text(outputs[name], encoding='utf-8')
        for path in obsolete:
            path.unlink()
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f'同步失败：{error}\n')
    print(f'已生成 {args.skill} 主题资料及来源记录。')


if __name__ == '__main__':
    main()
