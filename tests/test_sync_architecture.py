import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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


def snapshot(reference):
    return {str(p.relative_to(reference)): p.read_bytes() for p in reference.rglob('*') if p.is_file()}


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sources = self.root / 'rules'
        self.sources.mkdir()
        for name, headings in HEADINGS.items():
            text = f'# {name}\n\n引言。\n\n' + ''.join(
                f'## {heading}\n\n保留 {name}/{heading}。\n\n' for heading in headings)
            (self.sources / name).parent.mkdir(parents=True, exist_ok=True)
            (self.sources / name).write_text(text, encoding='utf-8')
        self.source = self.sources / 'ARCHITECTURE.md'
        self.script = self.root / 'package/scripts/sync_architecture.py'
        self.script.parent.mkdir(parents=True)
        shutil.copy2(SCRIPT, self.script)
        self.reference = self.root / 'package/skills/unif-architecture-design/references'

    def test_backend_topics_have_independent_provenance_and_detect_drift(self):
        headings = ["1. 适用范围与实施", "2. 目录与文件归属", "3. 公共入口与依赖", "4. 运行与资源生命周期", "5. 契约与任务指令", "6. 验证与交付"]
        source = self.sources / "PYTHON_DEVELOPMENT.md"
        source.write_text("# 后端工程规范\n\n引言。\n\n" + "".join(f"## {heading}\n\n内容。\n\n" for heading in headings))
        args = [sys.executable, str(self.script), "--source", str(self.sources), "--skill", "unif-python-dev"]
        generated = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(generated.returncode, 0, generated.stderr)
        reference = self.root / "package/skills/unif-python-dev/references"
        record = json.loads((reference / "source.json").read_text())
        self.assertEqual(set(record["sources"]), {"PYTHON_DEVELOPMENT.md", "ARCHITECTURE.md"})
        self.assertEqual(set(record["files"]), {"scope.md", "structure.md", "lifecycle.md", "validation.md", "common/state.md", "common/contracts.md", "common/verification.md"})
        checked = subprocess.run([*args, "--check"], capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        source.write_text(source.read_text() + "新增约束。\n")
        drift = subprocess.run([*args, "--check"], capture_output=True, text=True)
        self.assertEqual(drift.returncode, 1, drift.stderr)

    def run_sync(self, *args, skill='unif-architecture-design'):
        arguments = ['--source', str(self.source if skill == 'unif-architecture-design' else self.sources), '--skill', skill]
        return subprocess.run([sys.executable, str(self.script), *arguments, *args],
                              capture_output=True, text=True)

    def files(self):
        return {p.name: p.read_bytes() for p in self.reference.iterdir()}

    def test_partitions_every_source_line_once_with_verifiable_provenance(self):
        for skill, expected_sources in {
            'unif-architecture-design': {'ARCHITECTURE.md'},
            'unif-rn-dev': {'ARCHITECTURE.md', 'PORTAL_DEVELOPMENT.md', 'PORTAL_STRUCTURE.md'},
            'unif-harmony-dev': {'ARCHITECTURE.md', 'HARMONY_DEVELOPMENT.md', 'HARMONY_STRUCTURE.md',
                                    *(f'libraries/harmony-{name}.md' for name in HARMONY_LIBRARIES)},
            'unif-python-dev': {'ARCHITECTURE.md', 'PYTHON_DEVELOPMENT.md'},
        }.items():
            with self.subTest(skill=skill):
                result = self.run_sync(skill=skill)
                self.assertEqual(result.returncode, 0, result.stderr)
                reference = self.root / 'package/skills' / skill / 'references'
                record = json.loads((reference / 'source.json').read_text())
                self.assertEqual(set(record['sources']), expected_sources)
                self.assertEqual(set(snapshot(reference)), set(record['files']) | {'source.json'})
                covered = {name: [] for name in expected_sources}
                for filename, topic in record['files'].items():
                    content = (reference / filename).read_bytes()
                    self.assertEqual(hashlib.sha256(content).hexdigest(), topic['sha256'])
                    parts = []
                    for selection in topic['sections']:
                        source = selection['source']
                        start, end = selection['lines']
                        lines = (self.sources / source).read_text().splitlines(keepends=True)
                        covered[source].extend(range(start, end + 1))
                        parts.append(''.join(lines[start - 1:end]))
                    self.assertEqual(content.decode().split('-->\n\n', 1)[1], '\n'.join(parts).rstrip('\n') + '\n')
                for name in expected_sources:
                    source = (self.sources / name).read_bytes()
                    expected = record['sources'][name].get('selectedSections')
                    lines = ([line for section in expected for line in range(section['lines'][0], section['lines'][1] + 1)]
                             if expected else list(range(1, len(source.splitlines()) + 1)))
                    self.assertEqual(sorted(covered[name]), lines)
                    self.assertEqual(record['sources'][name]['sha256'], hashlib.sha256(source).hexdigest())
                self.assertEqual(self.run_sync('--check', skill=skill).returncode, 0)

    def test_harmony_topics_have_independent_provenance(self):
        source = self.sources / 'HARMONY_STRUCTURE.md'
        source.write_text(source.read_text() +
                          '[状态](HARMONY_DEVELOPMENT.md#3-arkui-状态与生命周期)\n')
        result = self.run_sync(skill='unif-harmony-dev')
        self.assertEqual(result.returncode, 0, result.stderr)
        reference = self.root / 'package/skills/unif-harmony-dev/references'
        record = json.loads((reference / 'source.json').read_text())
        expected = {
            'harmony/scope.md': {'HARMONY_DEVELOPMENT.md'},
            'harmony/files.md': {'HARMONY_DEVELOPMENT.md'},
            'harmony/state.md': {'HARMONY_DEVELOPMENT.md'},
            'harmony/integration.md': {'HARMONY_DEVELOPMENT.md', 'HARMONY_STRUCTURE.md'},
            'harmony/testing.md': {'HARMONY_DEVELOPMENT.md'},
            'harmony/directory.md': {'HARMONY_STRUCTURE.md'},
            'harmony/ui.md': {'HARMONY_STRUCTURE.md'},
        }
        expected.update({f'harmony/{name}.md': {f'libraries/harmony-{name}.md'}
                         for name in HARMONY_LIBRARIES})
        self.assertEqual({name for name in record['files'] if name.startswith('harmony/')}, set(expected))
        for name, sources in expected.items():
            self.assertEqual({part['source'] for part in record['files'][name]['sections']}, sources)
        self.assertFalse(any(name.startswith('rn/') for name in record['files']))
        self.assertIn('[状态](state.md#3-arkui-状态与生命周期)',
                      (reference / 'harmony/integration.md').read_text())

    def test_harmony_missing_source_does_not_partially_generate(self):
        self.assertEqual(self.run_sync(skill='unif-harmony-dev').returncode, 0)
        reference = self.root / 'package/skills/unif-harmony-dev/references'
        before = snapshot(reference)
        for name in ('HARMONY_DEVELOPMENT.md', 'HARMONY_STRUCTURE.md',
                     *(f'libraries/harmony-{name}.md' for name in HARMONY_LIBRARIES)):
            with self.subTest(source=name):
                source = self.sources / name
                content = source.read_bytes()
                source.unlink()
                result = self.run_sync(skill='unif-harmony-dev')
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn(name, result.stderr)
                self.assertEqual(snapshot(reference), before)
                source.write_bytes(content)

    def test_harmony_source_drift_is_detected_without_writes(self):
        self.assertEqual(self.run_sync(skill='unif-harmony-dev').returncode, 0)
        reference = self.root / 'package/skills/unif-harmony-dev/references'
        for target in (self.sources / 'HARMONY_DEVELOPMENT.md',
                       self.sources / 'HARMONY_STRUCTURE.md',
                       reference / 'harmony/state.md', reference / 'source.json',
                       *(self.sources / f'libraries/harmony-{name}.md' for name in HARMONY_LIBRARIES),
                       *(reference / f'harmony/{name}.md' for name in HARMONY_LIBRARIES)):
            with self.subTest(target=target.name):
                self.assertTrue(target.is_file(), str(target))
                original = target.read_bytes()
                target.write_bytes(original + b'\n')
                before = snapshot(reference)
                result = self.run_sync('--check', skill='unif-harmony-dev')
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(snapshot(reference), before)
                self.assertEqual(target.read_bytes(), original + b'\n')
                target.write_bytes(original)

    def test_harmony_library_nested_links_stay_portable(self):
        source = self.sources / 'libraries/harmony-icons.md'
        source.write_text(source.read_text() +
                          '[Design](harmony-design.md#1-职责与依赖) '
                          '[字体](../HARMONY_STRUCTURE.md#2-组件主题与玻璃材质) '
                          '[RN](react-native-icons.md#公开输入) '
                          '[架构](../ARCHITECTURE.md#4-状态归属)\n')
        result = self.run_sync(skill='unif-harmony-dev')
        self.assertEqual(result.returncode, 0, result.stderr)
        reference = self.root / 'package/skills/unif-harmony-dev/references'
        topic = reference / 'harmony/icons.md'
        self.assertTrue(topic.is_file(), '六库专题应随 unif-harmony-dev 分发')
        text = topic.read_text()
        self.assertIn('[Design](design.md#1-职责与依赖)', text)
        self.assertIn('[字体](ui.md#2-组件主题与玻璃材质)', text)
        self.assertIn('RN（规范源相对路径：`libraries/react-native-icons.md#公开输入`）', text)
        self.assertIn('[架构](../common/state.md#4-状态归属)', text)
        self.assertEqual(self.run_sync('--check', skill='unif-harmony-dev').returncode, 0)

    def test_generated_topics_end_with_one_newline(self):
        self.assertEqual(self.run_sync(skill='unif-rn-dev').returncode, 0)
        reference = self.root / 'package/skills/unif-rn-dev/references'
        for topic in reference.rglob('*.md'):
            with self.subTest(topic=topic.name):
                self.assertTrue(topic.read_bytes().endswith(b'\n'))
                self.assertFalse(topic.read_bytes().endswith(b'\n\n'))

    def test_preserves_code_and_external_links_with_source_relative_hints(self):
        self.source.write_text(self.source.read_text() +
                               '[领域](domains/example.md#entity) [外部](https://example.com) '
                               '[站外](//example.com/docs)\n'
                               '`[内联示例](relative.md)`\n'
                               '```md\n## 10. 代码里的标题\n[示例](relative.md)\n```\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.reference / 'documentation.md').read_text()
        self.assertIn('领域（规范源相对路径：`domains/example.md#entity`）', text)
        self.assertIn('[外部](https://example.com) [站外](//example.com/docs)', text)
        self.assertIn('`[内联示例](relative.md)`', text)
        self.assertIn('```md\n## 10. 代码里的标题\n[示例](relative.md)\n```', text)

    def test_rewrites_source_anchors_to_their_generated_topics(self):
        source = self.source.read_text().replace(
            '## 3. 功能、场景与入口\n', '## 3. 功能、场景与入口\n\n### 公共输入\n')
        self.source.write_text(source +
                               '[状态](./ARCHITECTURE.md#4-状态归属) '
                               '[输入](#公共输入)\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.reference / 'documentation.md').read_text()
        self.assertIn('[状态](state.md#4-状态归属)', text)
        self.assertIn('[输入](composition.md#公共输入)', text)
        self.assertIn('### 公共输入', (self.reference / 'composition.md').read_text())

    def test_code_styled_link_labels_are_resolved_and_validated(self):
        original = self.source.read_text()
        self.source.write_text(original + '[`状态`](#4-状态归属)\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('[`状态`](state.md#4-状态归属)', (self.reference / 'documentation.md').read_text())
        before = self.files()
        self.source.write_text(original + '[`缺失`](#missing)\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('锚点', result.stderr)
        self.assertEqual(self.files(), before)

    def test_multiline_code_spans_remain_literal(self):
        example = '`代码示例\n[状态](#4-状态归属)\n[缺失](#missing)\n`\n'
        self.source.write_text(self.source.read_text() + example)
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(example, (self.reference / 'documentation.md').read_text())

    def test_code_spans_do_not_cross_markdown_block_boundaries(self):
        original = self.source.read_text()
        examples = (
            '第一段 `\n\n[缺失](#missing)\n\n第三段 `\n',
            '第一段 `\n### 标题\n[缺失](#missing)\n结束 `\n',
            '第一段 `\n- [缺失](#missing)\n结束 `\n',
        )
        for example in examples:
            with self.subTest(example=example):
                self.source.write_text(original + example)
                result = self.run_sync()
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn('锚点', result.stderr)

    def test_routes_bundled_documents_and_preserves_unbundled_source_paths(self):
        source = self.sources / 'PORTAL_STRUCTURE.md'
        source.write_text(source.read_text() +
                          '[文件角色](PORTAL_DEVELOPMENT.md#3-常量类型变量与文件拆分) '
                          '[完整规则](PORTAL_DEVELOPMENT.md) '
                          '[状态](ARCHITECTURE.md#4-状态归属)\n')
        result = self.run_sync(skill='unif-rn-dev')
        self.assertEqual(result.returncode, 0, result.stderr)
        reference = self.root / 'package/skills/unif-rn-dev/references'
        text = (reference / 'rn/testing.md').read_text()
        self.assertIn('[文件角色](file-rules.md#3-常量类型变量与文件拆分)', text)
        self.assertIn('[完整规则](../../SKILL.md)', text)
        self.assertIn('[状态](../common/state.md#4-状态归属)', text)
        self.assertEqual(self.run_sync('--check', skill='unif-rn-dev').returncode, 0)

    def test_missing_bundled_anchor_fails_before_writing(self):
        self.assertEqual(self.run_sync().returncode, 0)
        before = self.files()
        self.source.write_text(self.source.read_text() + '[缺失章节](#missing)\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('锚点', result.stderr)
        self.assertEqual(self.files(), before)

    def test_reconciles_duplicate_anchors_after_splitting_and_combining_sources(self):
        source = self.source.read_text()
        for heading in ('3. 功能、场景与入口', '4. 状态归属'):
            source = source.replace(f'## {heading}\n', f'## {heading}\n\n### 输入\n')
        self.source.write_text(source + '[后者](#输入-1)\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('[后者](state.md#输入)', (self.reference / 'documentation.md').read_text())

        for name, heading in (('PORTAL_DEVELOPMENT.md', '5. 规则执行与定向验证'),
                              ('PORTAL_STRUCTURE.md', '6. 开发维护与定向验证')):
            path = self.sources / name
            source = path.read_text().replace(f'## {heading}\n', f'## {heading}\n\n### 验证对象\n')
            path.write_text(source + '[本规范的验证对象](#验证对象)\n')
        result = self.run_sync(skill='unif-rn-dev')
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.root / 'package/skills/unif-rn-dev/references/rn/testing.md').read_text()
        self.assertIn('[本规范的验证对象](testing.md#验证对象)', text)
        self.assertIn('[本规范的验证对象](testing.md#验证对象-1)', text)

    def test_reconciles_source_and_output_heading_order(self):
        path = self.sources / 'PORTAL_DEVELOPMENT.md'
        source = path.read_text()
        third = source.index('## 3. 常量、类型、变量与文件拆分')
        fourth = source.index('## 4. 命名与公开出口')
        fifth = source.index('## 5. 规则执行与定向验证')
        names = source[fourth:fifth] + '### 输入\n\n[名称部分输入](#输入)\n\n'
        types = source[third:fourth] + '### 输入\n\n[类型部分输入](#输入-1)\n\n'
        path.write_text(source[:third] + names + types + source[fifth:])
        result = self.run_sync(skill='unif-rn-dev')
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.root / 'package/skills/unif-rn-dev/references/rn/file-rules.md').read_text()
        self.assertIn('[类型部分输入](file-rules.md#输入)', text)
        self.assertIn('[名称部分输入](file-rules.md#输入-1)', text)

    def test_unknown_missing_and_duplicate_sections_fail_without_writes(self):
        self.assertEqual(self.run_sync().returncode, 0)
        before = self.files()
        source = self.source.read_text()
        for changed in (source + '\n## 10. 新规则\n不能静默丢弃\n',
                        source.replace('## 4. 状态归属', '### 4. 状态归属'),
                        source + '\n## 4. 状态归属\n重复\n'):
            with self.subTest(changed=changed[-40:]):
                self.source.write_text(changed)
                result = self.run_sync()
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(self.files(), before)

    def test_check_detects_content_and_provenance_changes_without_writing(self):
        self.assertEqual(self.run_sync().returncode, 0)
        for filename in ('contracts.md', 'source.json'):
            with self.subTest(filename=filename):
                path = self.reference / filename
                original = path.read_bytes()
                path.write_text('改动')
                before = self.files()
                result = self.run_sync('--check')
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(filename, result.stderr)
                self.assertEqual(self.files(), before)
                path.write_bytes(original)

    def test_check_detects_changed_canonical_source(self):
        self.assertEqual(self.run_sync().returncode, 0)
        before = self.files()
        self.source.write_text(self.source.read_text() + '\n新增规则。\n')
        self.assertEqual(self.run_sync('--check').returncode, 1)
        self.assertEqual(self.files(), before)

    def test_missing_second_source_does_not_partially_generate(self):
        (self.sources / 'PORTAL_STRUCTURE.md').unlink()
        self.assertEqual(self.run_sync(skill='unif-rn-dev').returncode, 2)
        self.assertFalse((self.root / 'package/skills/unif-rn-dev').exists())

    def test_removes_only_obsolete_generated_files_and_check_is_read_only(self):
        self.reference.mkdir(parents=True)
        old = self.reference / 'platform-architecture.md'
        old.write_text('<!-- 此文件由 scripts/sync_architecture.py 生成，请修改规范源后重新同步。\n-->\n旧正文\n')
        (self.reference / 'source.json').write_text(json.dumps({'source': 'unif-platform-architecture/ARCHITECTURE.md'}))
        (self.reference / 'manual.md').write_text('手工资料')
        before = self.files()
        result = self.run_sync('--check')
        self.assertEqual(result.returncode, 1)
        self.assertIn('platform-architecture.md', result.stderr)
        self.assertEqual(self.files(), before)
        self.assertEqual(self.run_sync().returncode, 0)
        self.assertFalse(old.exists())
        self.assertEqual((self.reference / 'manual.md').read_text(), '手工资料')

    def test_will_not_delete_unmanaged_legacy_or_overwrite_symlinked_outputs(self):
        self.reference.mkdir(parents=True)
        target = self.reference / 'platform-architecture.md'
        target.write_text('未确认的手工文档')
        before = self.files()
        self.assertEqual(self.run_sync().returncode, 2)
        self.assertEqual(self.files(), before)
        target.unlink()
        target = self.reference / 'contracts.md'
        target.symlink_to(self.source)
        original = self.source.read_bytes()
        self.assertEqual(self.run_sync().returncode, 2)
        self.assertEqual(self.source.read_bytes(), original)

    def test_invalid_previous_manifest_does_not_partially_write(self):
        self.assertEqual(self.run_sync().returncode, 0)
        (self.reference / 'source.json').write_text(json.dumps({'formatVersion': 2, 'files': None}))
        self.source.write_text(self.source.read_text() + '\n更新正文。\n')
        before = self.files()
        self.assertEqual(self.run_sync().returncode, 2)
        self.assertEqual(self.files(), before)

    def test_directory_collision_does_not_partially_write(self):
        (self.reference / 'contracts.md').mkdir(parents=True)
        self.assertEqual(self.run_sync().returncode, 2)
        self.assertEqual([p.name for p in self.reference.iterdir()], ['contracts.md'])


    def test_stage_selection_bundles_rules_and_rejects_new_source_chapters(self):
        for platform in ('rn', 'harmony', 'python'):
            for stage in ('test', 'review'):
                skill = f'unif-{platform}-{stage}'
                with self.subTest(skill=skill):
                    original = self.source.read_text()
                    result = self.run_sync(skill=skill)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    reference = self.root / 'package/skills' / skill / 'references'
                    record = json.loads((reference / 'source.json').read_text())
                    selected = record['sources']['ARCHITECTURE.md']['selectedSections']
                    expected = ['3. 功能、场景与入口', '4. 状态归属', '6. 跨边界交接与业务结果', '7. 独立开发与验证']
                    if stage == 'review':
                        expected = ['1. 架构目标', '2. 系统边界与职责', *expected]
                        expected.insert(0, '')
                    self.assertEqual([section['heading'] for section in selected], expected)
                    self.assertTrue((reference / 'common/verification.md').is_file())
                    self.assertFalse((reference / 'common/cost.md').exists())
                    self.assertEqual(self.run_sync('--check', skill=skill).returncode, 0)
                    before = snapshot(reference)
                    self.source.write_text(original + '\n## 10. 新规则\n不能静默忽略。\n')
                    result = self.run_sync(skill=skill)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertEqual(snapshot(reference), before)
                    self.source.write_text(original)

    def test_platform_generation_does_not_read_other_platform_sources(self):
        for platform, prefixes in {
            'rn': ('PORTAL_',),
            'harmony': ('HARMONY_', 'libraries/harmony-'),
            'python': ('PYTHON_',),
        }.items():
            removed = {}
            for path in self.sources.rglob('*.md'):
                name = str(path.relative_to(self.sources))
                if name != 'ARCHITECTURE.md' and not name.startswith(prefixes):
                    removed[path] = path.read_bytes()
                    path.unlink()
            for stage in ('dev', 'test', 'review'):
                with self.subTest(platform=platform, stage=stage):
                    result = self.run_sync(skill=f'unif-{platform}-{stage}')
                    self.assertEqual(result.returncode, 0, result.stderr)
            for path, content in removed.items():
                path.write_bytes(content)

    def test_unselected_known_anchor_keeps_source_location(self):
        self.source.write_text(self.source.read_text().replace('## 4. 状态归属\n',
            '## 4. 状态归属\n\n[成本](#8-成本与效果验证)\n'))
        result = self.run_sync(skill='unif-rn-dev')
        self.assertEqual(result.returncode, 0, result.stderr)
        topic = self.root / 'package/skills/unif-rn-dev/references/common/state.md'
        self.assertIn('成本（规范源相对路径：`ARCHITECTURE.md#8-成本与效果验证`）', topic.read_text())

    def test_nested_output_directory_cannot_be_a_symlink(self):
        reference = self.root / 'package/skills/unif-rn-dev/references'
        reference.mkdir(parents=True)
        outside = self.root / 'outside'
        outside.mkdir()
        (outside / 'preserve.md').write_text('preserve')
        (reference / 'rn').symlink_to(outside, target_is_directory=True)
        result = self.run_sync(skill='unif-rn-dev')
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(snapshot(outside), {'preserve.md': b'preserve'})
        self.assertFalse((reference / 'source.json').exists())

    def test_layout_migration_removes_only_registered_old_files(self):
        self.assertEqual(self.run_sync(skill='unif-rn-dev').returncode, 0)
        reference = self.root / 'package/skills/unif-rn-dev/references'
        (reference / 'rn/scope.md').rename(reference / 'scope.md')
        record = json.loads((reference / 'source.json').read_text())
        record['files']['scope.md'] = record['files'].pop('rn/scope.md')
        (reference / 'source.json').write_text(json.dumps(record))
        (reference / 'manual.md').write_text('manual')
        before = snapshot(reference)
        self.assertEqual(self.run_sync('--check', skill='unif-rn-dev').returncode, 1)
        self.assertEqual(snapshot(reference), before)
        self.assertEqual(self.run_sync(skill='unif-rn-dev').returncode, 0)
        self.assertFalse((reference / 'scope.md').exists())
        self.assertTrue((reference / 'rn/scope.md').is_file())
        self.assertEqual((reference / 'manual.md').read_text(), 'manual')


if __name__ == '__main__':
    unittest.main()
