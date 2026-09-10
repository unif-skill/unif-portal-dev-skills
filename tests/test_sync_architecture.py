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
    'PORTAL_DEVELOPMENT.md': [
        '1. 文件变更入口', '2. 各类代码的开发规则', '3. 常量、类型、变量与文件拆分',
        '4. 命名与公开出口', '5. 规则执行与定向验证',
    ],
    'PORTAL_STRUCTURE.md': [
        '1. 目标目录', '2. 基础组件与 UI 复用', '3. 工具、常量、类型及其他文件的归属',
        '4. 公共入口与依赖方向', '5. 基础能力与资源归属', '6. 基础代码迁移与定向验证',
    ],
}


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
            (self.sources / name).write_text(text, encoding='utf-8')
        self.source = self.sources / 'ARCHITECTURE.md'
        self.script = self.root / 'package/scripts/sync_architecture.py'
        self.script.parent.mkdir(parents=True)
        shutil.copy2(SCRIPT, self.script)
        self.reference = self.root / 'package/skills/architecture-design/references'

    def run_sync(self, *args, portal=False):
        arguments = ['--source', str(self.sources if portal else self.source)]
        if portal:
            arguments += ['--skill', 'portal-development']
        return subprocess.run([sys.executable, str(self.script), *arguments, *args],
                              capture_output=True, text=True)

    def files(self):
        return {p.name: p.read_bytes() for p in self.reference.iterdir()}

    def test_partitions_every_source_line_once_with_verifiable_provenance(self):
        for portal in (False, True):
            with self.subTest(portal=portal):
                result = self.run_sync(portal=portal)
                self.assertEqual(result.returncode, 0, result.stderr)
                skill = 'portal-development' if portal else 'architecture-design'
                reference = self.root / 'package/skills' / skill / 'references'
                record = json.loads((reference / 'source.json').read_text())
                expected_sources = set(HEADINGS) - {'ARCHITECTURE.md'} if portal else {'ARCHITECTURE.md'}
                self.assertEqual(set(record['sources']), expected_sources)
                self.assertEqual({p.name for p in reference.iterdir()}, set(record['files']) | {'source.json'})
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
                    self.assertEqual(content.decode().split('-->\n\n', 1)[1], '\n'.join(parts))
                for name in expected_sources:
                    source = (self.sources / name).read_bytes()
                    self.assertEqual(sorted(covered[name]), list(range(1, len(source.splitlines()) + 1)))
                    self.assertEqual(record['sources'][name]['sha256'], hashlib.sha256(source).hexdigest())
                self.assertEqual(self.run_sync('--check', portal=portal).returncode, 0)

    def test_preserves_code_and_external_links_but_removes_relative_document_links(self):
        self.source.write_text(self.source.read_text() +
                               '[领域](domains/example.md) [外部](https://example.com) [锚点](#a)\n'
                               '```md\n## 10. 代码里的标题\n[示例](relative.md)\n```\n')
        result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.reference / 'documentation.md').read_text()
        self.assertIn('领域 [外部](https://example.com) [锚点](#a)', text)
        self.assertIn('```md\n## 10. 代码里的标题\n[示例](relative.md)\n```', text)

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
        self.assertEqual(self.run_sync(portal=True).returncode, 2)
        self.assertFalse((self.root / 'package/skills/portal-development').exists())

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


if __name__ == '__main__':
    unittest.main()
