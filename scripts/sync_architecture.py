#!/usr/bin/env python3
"""从规范源按主题生成技能资料；--check 只比较，不修改文件。"""

import argparse
import hashlib
import json
import posixpath
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

INLINE_CONTENT = re.compile(
    r'(?P<code>(?<!`)(?P<ticks>`+)(?!`)(?s:.*?)(?<!`)(?P=ticks)(?!`))'
    r'|(?<!!)\[(?P<label>[^\]\n]+)\]\((?P<target>[^)\s]+)\)'
)
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
            'testing.md': ['6. 分批重写与定向验证'],
        },
    },
}
LEGACY = {
    'architecture-design': {'platform-architecture.md'},
    'portal-development': {'portal-development.md', 'portal-structure.md'},
}


def markdown_lines(text):
    """标出代码围栏，供章节划分、锚点定位和链接转换共用。"""
    fence = None
    for number, line in enumerate(text.splitlines(keepends=True), 1):
        if fence:
            if re.fullmatch(r' {0,3}' + re.escape(fence[0]) + '{' + str(len(fence)) + r',}\s*', line):
                fence = None
            yield number, line, True
            continue
        opening = re.match(r' {0,3}(`{3,}|~{3,})', line)
        if opening:
            fence = opening[1]
        yield number, line, bool(opening)


def split_sections(text):
    """保留源文和行号；代码围栏内的标题不参与章节划分。"""
    sections = []
    heading, start, body = '', 1, []
    for number, line, code in markdown_lines(text):
        title = None if code else re.match(r'^## (.+?)\s*$', line)
        if title:
            sections.append((heading, start, number - 1, ''.join(body)))
            heading, start, body = title[1], number, []
        body.append(line)
    sections.append((heading, start, len(text.splitlines()), ''.join(body)))
    return sections


def add_anchor(heading, used):
    base = re.sub(r'[^\w -]', '', heading.lower()).replace(' ', '-')
    anchor, suffix = base, 0
    while anchor in used:
        suffix += 1
        anchor = f'{base}-{suffix}'
    used.add(anchor)
    return anchor


def topic_anchors(sections, topics, output_anchors):
    """将规范的 ATX 标题锚点定位到所属主题，包括三级及以下标题。"""
    anchors, source_anchors, section_titles = {}, set(), {}
    for section, _, _, body in sections:
        section_titles[section] = []
        for _, line, code in markdown_lines(body):
            title = None if code else re.match(r'^#{1,6} +(.+?)\s*$', line)
            if not title:
                continue
            heading = re.sub(r'\s+#+$', '', title[1])
            anchor = add_anchor(heading, source_anchors)
            section_titles[section].append((anchor, heading))
    # 源章节可以换序；目标锚点按 render 实际写出的顺序计数。
    for filename, selected in topics.items():
        for section in selected:
            for anchor, heading in section_titles[section]:
                output_anchor = add_anchor(heading, output_anchors.setdefault(filename, set()))
                anchors[anchor] = f'{filename}#{output_anchor}'
    return anchors


def portable_text(body, source_name, anchors):
    def link(match):
        if match['code'] is not None:
            return match[0]
        label, target = match['label'], match['target']
        url = urlsplit(target)
        if url.scheme or url.netloc:
            return match[0]
        source = (posixpath.normpath(posixpath.join(posixpath.dirname(source_name), unquote(url.path)))
                  if url.path else source_name)
        if source not in anchors or url.query:
            return f'{label}（规范源相对路径：`{target}`）'
        if not url.fragment:
            return f'[{label}](../SKILL.md)'
        fragment = unquote(url.fragment)
        if fragment not in anchors[source]:
            raise ValueError(f'{source_name}: 引用的规范锚点不存在：{target}')
        return f'[{label}]({anchors[source][fragment]})'

    lines, output, start = body.splitlines(keepends=True), [], 0
    # 只在同一个 Markdown 行内块内识别代码 span，保留围栏与块间原文。
    for token in MarkdownIt('commonmark').parse(body):
        if token.type != 'inline' or token.map is None:
            continue
        first, last = token.map
        output.extend(lines[start:first])
        output.append(INLINE_CONTENT.sub(link, ''.join(lines[first:last])))
        start = last
    output.extend(lines[start:])
    return ''.join(output)


def render(sources, skill):
    outputs, records = {}, {}
    provenance = {'formatVersion': 2, 'transformation': 'section-text-portable-links-v3',
                  'sources': {}, 'files': records}
    parsed = {name: split_sections(content.decode('utf-8')) for name, content in sources.items()}
    anchors, output_anchors = {}, {}
    for source_name, topics in TOPICS[skill].items():
        sections = parsed[source_name]
        headings = [section[0] for section in sections]
        expected = [heading for selection in topics.values() for heading in selection]
        if (len(set(headings)) != len(headings) or len(set(expected)) != len(expected)
                or set(headings) != set(expected)):
            raise ValueError(f'{source_name}: 二级章节缺失、重复或未分配；请核对主题映射。'
                             f' 缺失={set(expected) - set(headings)}，未分配={set(headings) - set(expected)}')
        anchors[source_name] = topic_anchors(sections, topics, output_anchors)
    for source_name, topics in TOPICS[skill].items():
        content = sources[source_name]
        provenance['sources'][source_name] = {
            'source': 'unif-platform-architecture/' + source_name,
            'sha256': hashlib.sha256(content).hexdigest(),
            'lines': len(content.decode('utf-8').splitlines()),
        }
        by_heading = {section[0]: section for section in parsed[source_name]}
        for filename, selected in topics.items():
            for title in selected:
                heading, start, end, body = by_heading[title]
                body = portable_text(body, source_name, anchors)
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
