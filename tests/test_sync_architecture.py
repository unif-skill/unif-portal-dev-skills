import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from functools import cached_property
from pathlib import Path
from typing import TypedDict, cast, override

from scripts.sync_architecture import COMMON, DESIGN, SOURCE_URL, TopicRecord

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/sync_architecture.py'
HEADINGS = {
    'ARCHITECTURE.md': [
        '1. 架构目标', '2. 系统边界与职责', '3. 功能、场景与入口', '4. 状态归属',
        '5. 自然语言任务与上下文', '6. 跨边界交接与业务结果', '7. 独立开发与验证',
        '8. 成本与效果验证', '9. 领域与模块文档',
    ],
    'HARMONY_DEVELOPMENT.md': [
        '1. 适用范围与实施', '2. ArkTS 文件与公共入口', '3. ArkUI 状态与生命周期',
        '4. 原生能力与协议接入', '5. 验证与交付',
    ],
    'HARMONY_STRUCTURE.md': [
        '1. 工程目录与依赖', '2. 组件、主题与玻璃材质', '3. 契约与资源归属',
    ],
    'PORTAL_DEVELOPMENT.md': [
        '1. 文件变更入口', '2. 各类代码的开发规则', '3. 常量、类型、变量与文件拆分',
        '4. 命名与公开出口', '5. 规则执行与定向验证',
    ],
    'PORTAL_STRUCTURE.md': [
        '1. 目标目录', '2. 基础组件与 UI 复用', '3. 工具、常量、类型及其他文件的归属',
        '4. 公共入口与依赖方向', '5. 基础能力与资源归属', '6. 开发维护与定向验证',
    ],
}
HEADINGS['PYTHON_DEVELOPMENT.md'] = ['1. 适用范围与实施', '2. 目录与文件归属', '3. 公共入口与依赖', '4. 运行与资源生命周期', '5. 契约与任务指令', '6. 验证与交付']
HARMONY_LIBRARIES = ('icons', 'design', 'chat', 'camera', 'hms-scan', 'umeng')
for library in HARMONY_LIBRARIES:
    HEADINGS[f'libraries/harmony-{library}.md'] = [
        '1. 职责与依赖', '2. 公开契约与对齐', '3. 状态、资源与结束', '4. 验证与采用',
    ]


class Source(TypedDict):
    sha256: str


class SourceMap(TypedDict):
    files: dict[str, TopicRecord]
    sources: dict[str, Source]


def read_manifest(reference: Path) -> SourceMap:
    return cast(SourceMap, json.loads((reference / 'source.json').read_text()))


def snapshot(reference: Path) -> dict[str, bytes]:
    return {str(p.relative_to(reference)): p.read_bytes() for p in reference.rglob('*') if p.is_file()}


class SnapshotTests(unittest.TestCase):
    @cached_property
    def root(self) -> Path:
        return Path(self.enterContext(tempfile.TemporaryDirectory()))

    @property
    def sources(self) -> Path:
        return self.root / 'rules'

    @property
    def source(self) -> Path:
        return self.sources / 'ARCHITECTURE.md'

    @property
    def script(self) -> Path:
        return self.root / 'package/scripts/sync_architecture.py'

    @property
    def reference(self) -> Path:
        return self.refs(COMMON)

    def refs(self, skill: str) -> Path:
        return self.root / 'package/plugins' / skill / 'references'

    def platform_refs(self, platform: str) -> Path:
        package = 'react-native' if platform == 'rn' else platform
        return self.refs(f'unif-{package}-skills/skills/unif-{platform}-dev')

    def library_refs(self, name: str) -> Path:
        return self.refs(f'unif-{name}/skills/unif-{name}')

    @override
    def setUp(self) -> None:
        self.sources.mkdir()
        for name, headings in HEADINGS.items():
            text = f'# {name}\n\n引言。\n\n' + ''.join(
                f'## {heading}\n\n保留 {name}/{heading}。\n\n' for heading in headings)
            (self.sources / name).parent.mkdir(parents=True, exist_ok=True)
            _ = (self.sources / name).write_text(text, encoding='utf-8')
        self.script.parent.mkdir(parents=True)
        _ = shutil.copy2(SCRIPT, self.script)

    def run_sync(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(self.script), '--source', str(self.sources), *args],
                              capture_output=True, text=True)

    def files(self) -> dict[str, bytes]:
        return snapshot(self.root / 'package/plugins')

    def test_partitions_every_source_line_once_with_verifiable_provenance(self) -> None:
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        covered: dict[str, list[int]] = {name: [] for name in HEADINGS}
        manifests = list((self.root / 'package/plugins').rglob('source.json'))
        self.assertEqual(len(manifests), 11)
        for manifest in manifests:
            root = manifest.parent
            record = read_manifest(root)
            self.assertEqual(set(snapshot(root)), set(record['files']) | {'source.json'})
            for source, metadata in record['sources'].items():
                source_bytes = (self.sources / source).read_bytes()
                self.assertEqual(metadata['sha256'], hashlib.sha256(source_bytes).hexdigest())
            for filename, topic in record['files'].items():
                content = (root / filename).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), topic['sha256'])
                parts: list[str] = []
                for selection in topic['sections']:
                    source = selection['source']
                    start, end = selection['lines']
                    lines = (self.sources / source).read_text().splitlines(keepends=True)
                    covered[source].extend(range(start, end + 1))
                    parts.append(''.join(lines[start - 1:end]))
                self.assertEqual(content.decode().split('-->\n\n', 1)[1], '\n'.join(parts).rstrip('\n') + '\n')
        for name, lines in covered.items():
            self.assertEqual(sorted(lines), list(range(1, len((self.sources / name).read_bytes().splitlines()) + 1)))
        self.assertEqual(self.run_sync('--check').returncode, 0)

    def test_harmony_topics_have_independent_provenance(self) -> None:
        source = self.sources / 'HARMONY_STRUCTURE.md'
        _ = source.write_text(source.read_text() +
                          '[状态](HARMONY_DEVELOPMENT.md#3-arkui-状态与生命周期)\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        reference = self.platform_refs('harmony')
        record = read_manifest(reference)
        expected = {
            'harmony/scope.md': {'HARMONY_DEVELOPMENT.md'},
            'harmony/files.md': {'HARMONY_DEVELOPMENT.md'},
            'harmony/state.md': {'HARMONY_DEVELOPMENT.md'},
            'harmony/integration.md': {'HARMONY_DEVELOPMENT.md', 'HARMONY_STRUCTURE.md'},
            'harmony/testing.md': {'HARMONY_DEVELOPMENT.md'},
            'harmony/directory.md': {'HARMONY_STRUCTURE.md'},
            'harmony/ui.md': {'HARMONY_STRUCTURE.md'},
        }
        for name in HARMONY_LIBRARIES:
            library = read_manifest(self.library_refs(name))
            self.assertEqual(set(library['sources']), {f'libraries/harmony-{name}.md'})
            self.assertEqual(set(library['files']), {f'harmony/{name}.md'})
        self.assertEqual({name for name in record['files'] if name.startswith('harmony/')}, set(expected))
        for name, sources in expected.items():
            self.assertEqual({part['source'] for part in record['files'][name]['sections']}, sources)
        self.assertIn('[状态](state.md#3-arkui-状态与生命周期)',
                      (reference / 'harmony/integration.md').read_text())

    def test_harmony_missing_source_does_not_partially_generate(self) -> None:
        self.assertEqual(self.run_sync().returncode, 0)
        reference = self.root / 'package/plugins'
        before = snapshot(reference)
        for name in ('HARMONY_DEVELOPMENT.md', 'HARMONY_STRUCTURE.md',
                     *(f'libraries/harmony-{name}.md' for name in HARMONY_LIBRARIES)):
            with self.subTest(source=name):
                source = self.sources / name
                content = source.read_bytes()
                source.unlink()
                result = self.run_sync()
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn(name, result.stderr)
                self.assertEqual(snapshot(reference), before)
                _ = source.write_bytes(content)

    def test_harmony_source_drift_is_detected_without_writes(self) -> None:
        self.assertEqual(self.run_sync().returncode, 0)
        reference = self.platform_refs('harmony')
        for target in (self.sources / 'HARMONY_DEVELOPMENT.md',
                       self.sources / 'HARMONY_STRUCTURE.md',
                       reference / 'harmony/state.md', reference / 'source.json',
                       *(self.sources / f'libraries/harmony-{name}.md' for name in HARMONY_LIBRARIES),
                       *(self.library_refs(name) / f'harmony/{name}.md' for name in HARMONY_LIBRARIES)):
            with self.subTest(target=target.name):
                self.assertTrue(target.is_file(), str(target))
                original = target.read_bytes()
                _ = target.write_bytes(original + b'\n')
                before = snapshot(reference)
                result = self.run_sync('--check')
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(snapshot(reference), before)
                self.assertEqual(target.read_bytes(), original + b'\n')
                _ = target.write_bytes(original)

    def test_harmony_library_nested_links_stay_portable(self) -> None:
        source = self.sources / 'libraries/harmony-icons.md'
        _ = source.write_text(source.read_text() +
                          '[Design](harmony-design.md#1-职责与依赖) '
                          + '[字体](../HARMONY_STRUCTURE.md#2-组件主题与玻璃材质) '
                          + '[RN](react-native-icons.md#公开输入) '
                          + '[架构](../ARCHITECTURE.md#4-状态归属)\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        topic = self.library_refs('icons') / 'harmony/icons.md'
        self.assertTrue(topic.is_file(), '六库专题应随各自库技能分发')
        text = topic.read_text()
        self.assertIn(f'[Design]({SOURCE_URL}libraries/harmony-design.md#1-职责与依赖)', text)
        self.assertIn(f'[字体]({SOURCE_URL}HARMONY_STRUCTURE.md#2-组件主题与玻璃材质)', text)
        self.assertIn('RN（规范源相对路径：`libraries/react-native-icons.md#公开输入`）', text)
        self.assertIn(f'[架构]({SOURCE_URL}ARCHITECTURE.md#4-状态归属)', text)
        self.assertEqual(self.run_sync('--check').returncode, 0)

    def test_generated_topics_end_with_one_newline(self) -> None:
        self.assertEqual(self.run_sync().returncode, 0)
        reference = self.root / 'package/plugins'
        for topic in reference.rglob('*.md'):
            with self.subTest(topic=topic.name):
                self.assertTrue(topic.read_bytes().endswith(b'\n'))
                self.assertFalse(topic.read_bytes().endswith(b'\n\n'))

    def test_preserves_code_and_external_links_with_source_relative_hints(self) -> None:
        _ = self.source.write_text(self.source.read_text() +
                               '[领域](domains/example.md#entity) [外部](https://example.com) '
                               + '[站外](//example.com/docs)\n'
                               + '`[内联示例](relative.md)`\n'
                               + '```md\n## 10. 代码里的标题\n[示例](relative.md)\n```\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.refs(DESIGN) / 'architecture/documentation.md').read_text()
        self.assertIn('领域（规范源相对路径：`domains/example.md#entity`）', text)
        self.assertIn('[外部](https://example.com) [站外](//example.com/docs)', text)
        self.assertIn('`[内联示例](relative.md)`', text)
        self.assertIn('```md\n## 10. 代码里的标题\n[示例](relative.md)\n```', text)

    def test_rewrites_source_anchors_to_their_generated_topics(self) -> None:
        source = self.source.read_text().replace(
            '## 3. 功能、场景与入口\n', '## 3. 功能、场景与入口\n\n### 公共输入\n')
        _ = self.source.write_text(source +
                               '[状态](./ARCHITECTURE.md#4-状态归属) '
                               + '[输入](#公共输入)\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.refs(DESIGN) / 'architecture/documentation.md').read_text()
        self.assertIn(f'[状态]({SOURCE_URL}ARCHITECTURE.md#4-状态归属)', text)
        self.assertIn(f'[输入]({SOURCE_URL}ARCHITECTURE.md#公共输入)', text)
        self.assertIn('### 公共输入', (self.reference / 'architecture/composition.md').read_text())

    def test_code_styled_link_labels_are_resolved_and_validated(self) -> None:
        original = self.source.read_text()
        _ = self.source.write_text(original + '[`状态`](#4-状态归属)\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'[`状态`]({SOURCE_URL}ARCHITECTURE.md#4-状态归属)', (self.refs(DESIGN) / 'architecture/documentation.md').read_text())
        before = self.files()
        _ = self.source.write_text(original + '[`缺失`](#missing)\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('锚点', result.stderr)
        self.assertEqual(self.files(), before)

    def test_multiline_code_spans_remain_literal(self) -> None:
        example = '`代码示例\n[状态](#4-状态归属)\n[缺失](#missing)\n`\n'
        _ = self.source.write_text(self.source.read_text() + example)
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(example, (self.refs(DESIGN) / 'architecture/documentation.md').read_text())

    def test_code_spans_do_not_cross_markdown_block_boundaries(self) -> None:
        original = self.source.read_text()
        examples = (
            '第一段 `\n\n[缺失](#missing)\n\n第三段 `\n',
            '第一段 `\n### 标题\n[缺失](#missing)\n结束 `\n',
            '第一段 `\n- [缺失](#missing)\n结束 `\n',
        )
        for example in examples:
            with self.subTest(example=example):
                _ = self.source.write_text(original + example)
                result = self.run_sync()
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn('锚点', result.stderr)

    def test_routes_bundled_documents_and_preserves_unbundled_source_paths(self) -> None:
        source = self.sources / 'PORTAL_STRUCTURE.md'
        _ = source.write_text(source.read_text() +
                          '[文件角色](PORTAL_DEVELOPMENT.md#3-常量类型变量与文件拆分) '
                          + '[完整规则](PORTAL_DEVELOPMENT.md) '
                          + '[状态](ARCHITECTURE.md#4-状态归属)\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        reference = self.platform_refs('rn')
        text = (reference / 'rn/testing.md').read_text()
        self.assertIn('[文件角色](file-rules.md#3-常量类型变量与文件拆分)', text)
        self.assertIn('[完整规则](../../SKILL.md)', text)
        self.assertIn(f'[状态]({SOURCE_URL}ARCHITECTURE.md#4-状态归属)', text)
        self.assertEqual(self.run_sync('--check').returncode, 0)

    def test_missing_bundled_anchor_fails_before_writing(self) -> None:
        self.assertEqual(self.run_sync().returncode, 0)
        before = self.files()
        _ = self.source.write_text(self.source.read_text() + '[缺失章节](#missing)\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('锚点', result.stderr)
        self.assertEqual(self.files(), before)

    def test_reconciles_duplicate_anchors_after_splitting_and_combining_sources(self) -> None:
        source = self.source.read_text()
        for heading in ('3. 功能、场景与入口', '4. 状态归属'):
            source = source.replace(f'## {heading}\n', f'## {heading}\n\n### 输入\n')
        _ = self.source.write_text(source + '[后者](#输入-1)\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'[后者]({SOURCE_URL}ARCHITECTURE.md#输入-1)', (self.refs(DESIGN) / 'architecture/documentation.md').read_text())

        for name, heading in (('PORTAL_DEVELOPMENT.md', '5. 规则执行与定向验证'),
                              ('PORTAL_STRUCTURE.md', '6. 开发维护与定向验证')):
            path = self.sources / name
            source = path.read_text().replace(f'## {heading}\n', f'## {heading}\n\n### 验证对象\n')
            _ = path.write_text(source + '[本规范的验证对象](#验证对象)\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.platform_refs('rn') / 'rn/testing.md').read_text()
        self.assertIn('[本规范的验证对象](testing.md#验证对象)', text)
        self.assertIn('[本规范的验证对象](testing.md#验证对象-1)', text)

    def test_reconciles_source_and_output_heading_order(self) -> None:
        path = self.sources / 'PORTAL_DEVELOPMENT.md'
        source = path.read_text()
        third = source.index('## 3. 常量、类型、变量与文件拆分')
        fourth = source.index('## 4. 命名与公开出口')
        fifth = source.index('## 5. 规则执行与定向验证')
        names = source[fourth:fifth] + '### 输入\n\n[名称部分输入](#输入)\n\n'
        types = source[third:fourth] + '### 输入\n\n[类型部分输入](#输入-1)\n\n'
        _ = path.write_text(source[:third] + names + types + source[fifth:])
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.platform_refs('rn') / 'rn/file-rules.md').read_text()
        self.assertIn('[类型部分输入](file-rules.md#输入)', text)
        self.assertIn('[名称部分输入](file-rules.md#输入-1)', text)

    def test_unknown_missing_and_duplicate_sections_fail_without_writes(self) -> None:
        self.assertEqual(self.run_sync().returncode, 0)
        before = self.files()
        source = self.source.read_text()
        for changed in (source + '\n## 10. 新规则\n不能静默丢弃\n',
                        source.replace('## 4. 状态归属', '### 4. 状态归属'),
                        source + '\n## 4. 状态归属\n重复\n'):
            with self.subTest(changed=changed[-40:]):
                _ = self.source.write_text(changed)
                result = self.run_sync()
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(self.files(), before)

    def test_check_detects_content_and_provenance_changes_without_writing(self) -> None:
        self.assertEqual(self.run_sync().returncode, 0)
        for filename in ('architecture/contracts.md', 'source.json'):
            with self.subTest(filename=filename):
                path = self.reference / filename
                original = path.read_bytes()
                _ = path.write_text('改动')
                before = self.files()
                result = self.run_sync('--check')
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(filename, result.stderr)
                self.assertEqual(self.files(), before)
                _ = path.write_bytes(original)

    def test_check_detects_changed_canonical_source(self) -> None:
        self.assertEqual(self.run_sync().returncode, 0)
        before = self.files()
        _ = self.source.write_text(self.source.read_text() + '\n新增规则。\n')
        self.assertEqual(self.run_sync('--check').returncode, 1)
        self.assertEqual(self.files(), before)

    def test_missing_second_source_does_not_partially_generate(self) -> None:
        (self.sources / 'PORTAL_STRUCTURE.md').unlink()
        self.assertEqual(self.run_sync().returncode, 2)
        self.assertFalse(self.reference.exists())

    def test_removes_only_obsolete_generated_files_and_check_is_read_only(self) -> None:
        self.reference.mkdir(parents=True)
        old = self.reference / 'platform-architecture.md'
        _ = old.write_text('<!-- 此文件由 scripts/sync_architecture.py 生成，请修改规范源后重新同步。\n-->\n旧正文\n')
        _ = (self.reference / 'source.json').write_text(json.dumps({'formatVersion': 2, 'files': {'platform-architecture.md': {}}}))
        _ = (self.reference / 'manual.md').write_text('手工资料')
        before = self.files()
        result = self.run_sync('--check')
        self.assertEqual(result.returncode, 1)
        self.assertIn('platform-architecture.md', result.stderr)
        self.assertEqual(self.files(), before)
        self.assertEqual(self.run_sync().returncode, 0)
        self.assertFalse(old.exists())
        self.assertEqual((self.reference / 'manual.md').read_text(), '手工资料')

    def test_will_not_delete_unmanaged_legacy_or_overwrite_symlinked_outputs(self) -> None:
        self.reference.mkdir(parents=True)
        target = self.reference / 'platform-architecture.md'
        _ = target.write_text('未确认的手工文档')
        _ = (self.reference / 'source.json').write_text(json.dumps({'formatVersion': 2, 'files': {'platform-architecture.md': {}}}))
        before = self.files()
        self.assertEqual(self.run_sync().returncode, 2)
        self.assertEqual(self.files(), before)
        target.unlink()
        target = self.reference / 'architecture/contracts.md'
        target.parent.mkdir()
        target.symlink_to(self.source)
        original = self.source.read_bytes()
        self.assertEqual(self.run_sync().returncode, 2)
        self.assertEqual(self.source.read_bytes(), original)

    def test_invalid_previous_manifest_does_not_partially_write(self) -> None:
        self.assertEqual(self.run_sync().returncode, 0)
        _ = (self.reference / 'source.json').write_text(json.dumps({'formatVersion': 2, 'files': None}))
        _ = self.source.write_text(self.source.read_text() + '\n更新正文。\n')
        before = self.files()
        self.assertEqual(self.run_sync().returncode, 2)
        self.assertEqual(self.files(), before)

    def test_directory_collision_does_not_partially_write(self) -> None:
        (self.reference / 'architecture/contracts.md').mkdir(parents=True)
        self.assertEqual(self.run_sync().returncode, 2)
        self.assertEqual(list((self.reference / 'architecture').iterdir()), [self.reference / 'architecture/contracts.md'])
        self.assertEqual(self.files(), {})


    def test_nested_output_directory_cannot_be_a_symlink(self) -> None:
        reference = self.platform_refs('rn')
        reference.mkdir(parents=True)
        outside = self.root / 'outside'
        outside.mkdir()
        _ = (outside / 'preserve.md').write_text('preserve')
        (reference / 'rn').symlink_to(outside, target_is_directory=True)
        result = self.run_sync()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(snapshot(outside), {'preserve.md': b'preserve'})
        self.assertFalse((reference / 'source.json').exists())
        self.assertFalse(self.reference.exists())

    def test_layout_migration_removes_only_registered_old_files(self) -> None:
        self.assertEqual(self.run_sync().returncode, 0)
        reference = self.platform_refs('rn')
        _ = (reference / 'rn/scope.md').rename(reference / 'scope.md')
        record = read_manifest(reference)
        record['files']['scope.md'] = record['files'].pop('rn/scope.md')
        _ = (reference / 'source.json').write_text(json.dumps(record))
        _ = (reference / 'manual.md').write_text('manual')
        before = snapshot(reference)
        self.assertEqual(self.run_sync('--check').returncode, 1)
        self.assertEqual(snapshot(reference), before)
        self.assertEqual(self.run_sync().returncode, 0)
        self.assertFalse((reference / 'scope.md').exists())
        self.assertTrue((reference / 'rn/scope.md').is_file())
        self.assertEqual((reference / 'manual.md').read_text(), 'manual')


if __name__ == '__main__':
    _ = unittest.main()
