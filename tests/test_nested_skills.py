import re
import unittest
from pathlib import Path
from typing import cast

import yaml


PLUGINS = Path(__file__).resolve().parents[1] / 'plugins'


def has_skill_frontmatter(markdown: str) -> bool:
    """只识别文件开头的技能元数据，正文里的文档和代码示例可以照常引用。"""
    header = re.match(r'\A---[ \t]*\n(.*?)^---[ \t]*(?:\n|\Z)', markdown, re.MULTILINE | re.DOTALL)
    if header is None:
        return False
    try:
        metadata = cast(object, yaml.safe_load(header[1]))
    except yaml.YAMLError:
        return False
    if not isinstance(metadata, dict):
        return False
    fields = cast(dict[object, object], metadata)
    # 同名字段也可出现在平台资料里，只匹配 Agent Skills 入口允许的顶层字段。
    return (
        fields.keys() <= {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}
        and isinstance(fields.get('name'), str)
        and isinstance(fields.get('description'), str)
    )


class NestedSkillTests(unittest.TestCase):
    def test_only_the_skill_root_contains_an_entry_point(self) -> None:
        for skill in sorted(PLUGINS.glob('*/skills/*')):
            for path in sorted(skill.rglob('*.md')):
                if path == skill / 'SKILL.md':
                    continue
                with self.subTest(path=path.relative_to(PLUGINS)):
                    self.assertNotEqual(path.name.lower(), 'skill.md', '技能目录内嵌了另一份技能入口')
                    self.assertFalse(has_skill_frontmatter(path.read_text(encoding='utf-8')),
                                     '配套资料含另一份技能入口元数据')
