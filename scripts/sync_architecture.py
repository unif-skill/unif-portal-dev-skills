#!/usr/bin/env python3
"""从规范源按主题生成技能资料；--check 只比较，不修改文件。"""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
from collections.abc import Iterator
from pathlib import Path
from typing import NotRequired, TypedDict, cast
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

INLINE_CONTENT = re.compile(
    r'(?P<code>(?<!`)(?P<ticks>`+)(?!`)(?s:.*?)(?<!`)(?P=ticks)(?!`))'
    + r'|(?<!!)\[(?P<label>[^\]\n]+)\]\((?P<target>[^)\s]+)\)'
)
MARKER = '<!-- 此文件由 scripts/sync_architecture.py 生成'
HEADER = MARKER + '，请修改规范源后重新同步。来源与章节见 source.json。 -->\n\n'
# 每个源章节仅分配一次；空标题表示首个二级标题之前的引言。
TOPICS: dict[str, dict[str, list[str]]] = {
    'ARCHITECTURE.md': {
        'architecture/scope.md': ['', '1. 架构目标'],
        'architecture/responsibilities.md': ['2. 系统边界与职责'],
        'architecture/composition.md': ['3. 功能、场景与入口'],
        'architecture/state.md': ['4. 状态归属'],
        'architecture/agent-context.md': ['5. 自然语言任务与上下文'],
        'architecture/contracts.md': ['6. 跨边界交接与业务结果'],
        'architecture/verification.md': ['7. 独立开发与验证'],
        'architecture/cost.md': ['8. 成本与效果验证'],
        'architecture/documentation.md': ['9. 领域与模块文档'],
    },
    'PORTAL_DEVELOPMENT.md': {
        'rn/scope.md': ['', '1. 文件变更入口', '2. 各类代码的开发规则'],
        'rn/file-rules.md': ['3. 常量、类型、变量与文件拆分', '4. 命名与公开出口'],
        'rn/testing.md': ['5. 规则执行与定向验证'],
    },
    'PORTAL_STRUCTURE.md': {
        'rn/directory.md': ['', '1. 目标目录'],
        'rn/ui.md': ['2. 基础组件与 UI 复用'],
        'rn/utilities-config.md': ['3. 工具、常量、类型及其他文件的归属'],
        'rn/dependencies.md': ['4. 公共入口与依赖方向', '5. 基础能力与资源归属'],
        'rn/testing.md': ['6. 开发维护与定向验证'],
    },
    'HARMONY_DEVELOPMENT.md': {
        'harmony/scope.md': ['', '1. 适用范围与实施'],
        'harmony/files.md': ['2. ArkTS 文件与公共入口'],
        'harmony/state.md': ['3. ArkUI 状态与生命周期'],
        'harmony/integration.md': ['4. 原生能力与协议接入'],
        'harmony/testing.md': ['5. 验证与交付'],
    },
    'HARMONY_STRUCTURE.md': {
        'harmony/directory.md': ['', '1. 工程目录与依赖'],
        'harmony/ui.md': ['2. 组件、主题与玻璃材质'],
        'harmony/integration.md': ['3. 契约与资源归属'],
    },
    **{
        f'libraries/harmony-{name}.md': {
            f'harmony/{name}.md': [
                '', '1. 职责与依赖', '2. 公开契约与对齐',
                '3. 状态、资源与结束', '4. 验证与采用',
            ],
        }
        for name in ('icons', 'design', 'chat', 'camera', 'hms-scan', 'umeng')
    },
    'PYTHON_DEVELOPMENT.md': {
        'python/scope.md': ['', '1. 适用范围与实施'],
        'python/structure.md': ['2. 目录与文件归属', '3. 公共入口与依赖'],
        'python/lifecycle.md': ['4. 运行与资源生命周期'],
        'python/validation.md': ['5. 契约与任务指令', '6. 验证与交付'],
    },
}


SOURCE_URL = 'https://github.com/unif-design/unif-platform-architecture/blob/main/'
COMMON = 'unif-platform-rules/skills/unif-platform-rules'
DESIGN = 'unif-engineering-skills/skills/unif-architecture-design'
LIBRARIES = {'icons', 'design', 'chat', 'camera', 'hms-scan', 'umeng'}


def owner(topic: str) -> str:
    """返回主题在 plugins/ 中的唯一维护位置。"""
    platform, name = topic.split('/')
    if platform == 'architecture':
        return DESIGN if name in ('agent-context.md', 'cost.md', 'documentation.md') else COMMON
    if platform == 'harmony' and name.removesuffix('.md') in LIBRARIES:
        return 'unif-library-skills/skills/unif-' + name.removesuffix('.md')
    package = 'react-native' if platform == 'rn' else platform
    return f'unif-{package}-skills/skills/unif-{platform}-dev'


class SourceSection(TypedDict):
    source: str
    heading: str
    lines: list[int]


class SourceRecord(TypedDict):
    source: str
    sha256: str
    lines: int
    selectedSections: NotRequired[list[SourceSection]]


class TopicRecord(TypedDict):
    sections: list[SourceSection]
    sha256: str


def markdown_lines(text: str) -> Iterator[tuple[int, str, bool]]:
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


def split_sections(text: str) -> list[tuple[str, int, int, str]]:
    """保留源文和行号；代码围栏内的标题不参与章节划分。"""
    sections: list[tuple[str, int, int, str]] = []
    heading, start = '', 1
    body: list[str] = []
    for number, line, code in markdown_lines(text):
        title = None if code else re.match(r'^## (.+?)\s*$', line)
        if title:
            sections.append((heading, start, number - 1, ''.join(body)))
            heading, start, body = title[1], number, []
        body.append(line)
    sections.append((heading, start, len(text.splitlines()), ''.join(body)))
    return sections


def add_anchor(heading: str, used: set[str]) -> str:
    base = re.sub(r'[^\w -]', '', heading.lower()).replace(' ', '-')
    anchor, suffix = base, 0
    while anchor in used:
        suffix += 1
        anchor = f'{base}-{suffix}'
    used.add(anchor)
    return anchor


def topic_anchors(sections: list[tuple[str, int, int, str]], topics: dict[str, list[str]],
                  output_anchors: dict[str, set[str]]) -> dict[str, str]:
    """将规范的 ATX 标题锚点定位到所属主题，包括三级及以下标题。"""
    anchors: dict[str, str] = {}
    source_anchors: set[str] = set()
    section_titles: dict[str, list[tuple[str, str]]] = {}
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


def portable_text(body: str, source_name: str, anchors: dict[str, dict[str, str]], filename: str) -> str:
    def link(match: re.Match[str]) -> str:
        if match['code'] is not None:
            return match[0]
        label, target = match['label'], match['target']
        url = urlsplit(target)
        if url.scheme or url.netloc:
            return match[0]
        source = (posixpath.normpath(posixpath.join(posixpath.dirname(source_name), unquote(url.path)))
                  if url.path else source_name)
        hint = f'{label}（规范源相对路径：`{url._replace(path=source).geturl()}`）'
        if source not in anchors or url.query:
            return hint
        base = posixpath.dirname(filename) or '.'
        here = owner(filename)
        if not url.fragment:
            owners = {owner(topic) for topic in TOPICS[source]}
            if len(owners) == 1:
                target_skill = owners.pop()
                if target_skill.split('/')[0] == here.split('/')[0]:
                    index = posixpath.relpath(f'{target_skill}/SKILL.md', f'{here}/references/{base}')
                    return f'[{label}]({index})'
            return f'[{label}]({SOURCE_URL}{source})'
        fragment = unquote(url.fragment)
        if fragment not in anchors[source]:
            raise ValueError(f'{source_name}: 引用的规范锚点不存在：{target}')
        topic, anchor = anchors[source][fragment].split('#', 1)
        there = owner(topic)
        if here.split('/')[0] != there.split('/')[0]:
            return f'[{label}]({SOURCE_URL}{source}#{url.fragment})'
        target_file = f'{there}/references/{topic}'
        local = posixpath.relpath(target_file, f'{here}/references/{base}')
        return f'[{label}]({local}#{anchor})'

    lines = body.splitlines(keepends=True)
    output: list[str] = []
    start = 0
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


def render(sources: dict[str, bytes]) -> dict[str, dict[str, str]]:
    outputs: dict[str, str] = {}
    records: dict[str, TopicRecord] = {}
    source_records: dict[str, SourceRecord] = {}
    parsed = {name: split_sections(content.decode('utf-8')) for name, content in sources.items()}
    anchors: dict[str, dict[str, str]] = {}
    output_anchors: dict[str, set[str]] = {}
    for source_name, topics in TOPICS.items():
        sections = parsed[source_name]
        headings = [section[0] for section in sections]
        expected = [heading for selection in topics.values() for heading in selection]
        if (len(set(headings)) != len(headings) or len(set(expected)) != len(expected)
                or set(headings) != set(expected)):
            raise ValueError(f'{source_name}: 二级章节缺失、重复或未分配；请核对主题映射。'
                             + f' 缺失={set(expected) - set(headings)}，新增={set(headings) - set(expected)}')
        anchors[source_name] = topic_anchors(sections, topics, output_anchors)
    for source_name, topics in TOPICS.items():
        content = sources[source_name]
        source_records[source_name] = {
            'source': 'unif-platform-architecture/' + source_name,
            'sha256': hashlib.sha256(content).hexdigest(),
            'lines': len(content.decode('utf-8').splitlines()),
        }
        by_heading = {section[0]: section for section in parsed[source_name]}
        for filename, selected in topics.items():
            for title in selected:
                heading, start, end, body = by_heading[title]
                body = portable_text(body, source_name, anchors, filename)
                header = HEADER.replace('source.json', posixpath.relpath('source.json', posixpath.dirname(filename) or '.'))
                outputs[filename] = outputs.get(filename, header) + ('' if filename not in outputs else '\n') + body
                records.setdefault(filename, {'sections': [], 'sha256': ''})['sections'].append({
                    'source': source_name, 'heading': heading, 'lines': [start, end],
                })
    for filename, content in outputs.items():
        outputs[filename] = content = content.rstrip('\n') + '\n'
        records[filename]['sha256'] = hashlib.sha256(content.encode('utf-8')).hexdigest()
    packages: dict[str, dict[str, str]] = {}
    for filename, content in outputs.items():
        packages.setdefault(owner(filename), {})[filename] = content
    for files in packages.values():
        topics = {filename: records[filename] for filename in files}
        used: dict[str, list[SourceSection]] = {}
        for topic in topics.values():
            for section in topic['sections']:
                used.setdefault(section['source'], []).append(section)
        sources_for_owner: dict[str, SourceRecord] = {}
        for source, selections in used.items():
            info = source_records[source].copy()
            if len(selections) < len(parsed[source]):
                info['selectedSections'] = selections
            sources_for_owner[source] = info
        provenance = {'formatVersion': 2, 'transformation': 'section-owner-relative-links-v8',
                      'sources': sources_for_owner, 'files': topics}
        files['source.json'] = json.dumps(provenance, ensure_ascii=False, indent=2) + '\n'
    return packages


def output_path(destination: Path, name: str) -> Path:
    if (not name or Path(name).is_absolute()
            or any(part in ('', '.', '..') for part in name.split('/'))
            or not name.endswith(('.md', '.json'))):
        raise ValueError(f'非法生成文件名：{name!r}')
    path = destination / name
    for parent in (destination.parent, destination, *path.relative_to(destination).parents):
        candidate = parent if parent.is_absolute() else destination / parent
        if candidate.is_symlink() or (candidate.exists() and not candidate.is_dir()):
            raise ValueError(f'生成目录必须是普通目录：{candidate}')
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError(f'生成路径必须是普通文件：{path}')
    return path


def obsolete_files(destination: Path, outputs: dict[str, str]) -> list[Path]:
    # 只清理明确属于本生成器的资料，不碰同目录的手工文件。
    candidates: set[str] = set()
    record = destination / 'source.json'
    if record.is_file():
        try:
            raw = cast(object, json.loads(record.read_text(encoding='utf-8')))
        except json.JSONDecodeError:
            return []
        if not isinstance(raw, dict):
            raise ValueError(f'{record}: 来源记录必须是对象')
        previous = cast(dict[str, object], raw)
        files = previous.get('files')
        if previous.get('formatVersion') != 2 or not isinstance(files, dict):
            raise ValueError(f'{record}: 无效的来源记录或文件清单')
        candidates.update(cast(dict[str, object], files))
    obsolete: list[Path] = []
    for name in sorted(candidates - outputs.keys()):
        if not name.endswith('.md'):
            raise ValueError(f'非法旧生成文件名：{name!r}')
        path = output_path(destination, name)
        if path.exists():
            if not path.read_text(encoding='utf-8').startswith(MARKER):
                raise ValueError(f'旧文件不是可清理的生成资料：{path}')
            obsolete.append(path)
    return obsolete


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument('--source', required=True, type=Path)
    _ = parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    plugins = Path(__file__).resolve().parents[1] / 'plugins'
    try:
        source = cast(Path, args.source)
        sources = {name: (source / name).read_bytes() for name in TOPICS}
        writes: dict[Path, str] = {}
        obsolete: list[Path] = []
        for skill, outputs in render(sources).items():
            destination = plugins / skill / 'references'
            for directory in (destination, *destination.parents):
                if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
                    raise ValueError(f'生成目录必须是普通目录：{directory}')
                if directory == plugins:
                    break
            for name, content in outputs.items():
                path = output_path(destination, name)
                if not path.is_file() or path.read_text(encoding='utf-8') != content:
                    writes[path] = content
            obsolete.extend(obsolete_files(destination, outputs))
        if cast(bool, args.check):
            differences = [str(path.relative_to(plugins)) for path in (*writes, *obsolete)]
            if differences:
                parser.exit(1, '规范资料或来源记录不一致：' + '、'.join(differences) + '\n')
            print('规范资料与来源记录一致。')
            return
        for path, content in writes.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            _ = path.write_text(content, encoding='utf-8')
        for path in obsolete:
            path.unlink()
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f'同步失败：{error}\n')
    print('已将规范主题和来源记录同步到所属插件。')


if __name__ == '__main__':
    main()
