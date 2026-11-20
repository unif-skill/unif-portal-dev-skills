"""Shared regressions exercised through each repository's real validation entry."""

from collections.abc import Iterator
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.validate_repository import validate_repository


REPOSITORY = Path(__file__).resolve().parents[1]
RELEASE_FILES = (
    'scripts/prepare_release.py', 'scripts/publish_release.py',
    'tests/test_prepare_release.py', 'tests/test_publish_release.py',
    'scripts/release-tools.json',
)


class SkillFixture:
    def __init__(self, root: Path) -> None:
        self.root: Path = root
        self.skill: Path = self.root / 'skills/sample'
        self.is_uni: bool = (REPOSITORY / 'scripts/release-tools.json').exists()
        name = 'uni-skills' if self.is_uni else 'example'
        self.write('plugin.json', json.dumps({'$schema': 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json', 'name': name, 'version': '0.1.0'}))
        self.write('.agents/plugins/marketplace.json', json.dumps({
            'name': name,
            'plugins': [{
                'name': name, 'source': {'source': 'local', 'path': './'},
                'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'},
                'category': 'Productivity',
            }],
        }))
        if self.is_uni:
            for relative in RELEASE_FILES:
                target = self.root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                _ = shutil.copyfile(REPOSITORY / relative, target)
        self.write_skill('# Example\n')
        self.write('skills/sample/agents/openai.yaml', 'interface:\n  display_name: Example\n')

    def write(self, relative: str, content: str) -> None:
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        _ = target.write_text(content, encoding='utf-8')

    def write_skill(self, body: str) -> None:
        self.write('skills/sample/SKILL.md', '---\nname: sample\ndescription: Validate sample input.\n---\n' + body)

    def validate(self) -> None:
        _ = validate_repository(self.root)

@contextmanager
def fixture() -> Iterator[SkillFixture]:
    with tempfile.TemporaryDirectory() as temporary:
        yield SkillFixture(Path(temporary))


class SkillContentValidationTests(unittest.TestCase):
    def test_minimal_skill_needs_no_icon_or_references_directory(self) -> None:
        with fixture() as case:
            case.validate()
            self.assertFalse((case.skill / 'assets').exists())
            self.assertFalse((case.skill / 'references').exists())

    def test_frontmatter_constraints_are_enforced(self) -> None:
        with fixture() as case:
            invalid = (
                'No frontmatter\n',
                '---\nname: sample\n---\n',
                '---\nname: Bad_Name\ndescription: Example\n---\n',
                '---\nname: sample\ndescription: ' + 'x' * 1025 + '\n---\n',
            )
            for text in invalid:
                with self.subTest(text=text[:60]):
                    case.write('skills/sample/SKILL.md', text)
                    with self.assertRaises(ValueError):
                        case.validate()

    def test_optional_metadata_is_parsed_when_present(self) -> None:
        with fixture() as case:
            for text in ('interface: [broken\n', '[]\n', 'interface: []\n'):
                with self.subTest(text=text):
                    case.write('skills/sample/agents/openai.yaml', text)
                    with self.assertRaises(ValueError):
                        case.validate()

    def test_declared_missing_or_escaping_icon_is_rejected(self) -> None:
        with fixture() as case:
            for icon in ('./assets/missing.svg', '../../../outside.svg'):
                with self.subTest(icon=icon):
                    case.write('outside.svg', '<svg/>')
                    case.write('skills/sample/agents/openai.yaml', f'interface:\n  icon_small: {icon}\n')
                    with self.assertRaises(ValueError):
                        case.validate()

    def test_missing_markdown_target_is_rejected_in_entry_and_reference(self) -> None:
        with fixture() as case:
            case.write_skill('[Guide](references/guide.md)\n')
            with self.assertRaises(ValueError):
                case.validate()
            case.write('skills/sample/references/guide.md', '[Missing][target]\n\n[target]: absent.md\n')
            with self.assertRaises(ValueError):
                case.validate()

    def test_same_page_and_cross_document_missing_anchors_are_rejected(self) -> None:
        with fixture() as case:
            case.write('skills/sample/references/guide.md', '# Guide\n')
            for target in ('#absent', 'references/guide.md#absent'):
                with self.subTest(target=target):
                    case.write_skill(f'# Example\n[Missing]({target})\n')
                    with self.assertRaisesRegex(ValueError, 'anchor|锚点'):
                        case.validate()

    def test_chinese_duplicate_inline_and_encoded_headings_are_supported(self) -> None:
        with fixture() as case:
            case.write('skills/sample/assets/icon.svg', '<svg/>')
            case.write('skills/sample/references/指南.md', '# 中文 标题\n')
            case.write_skill(
                '# 组件与状态\n'
                + '[Self](#组件与状态)\n'
                + '## 重复\n## 重复\n## 重复-1\n'
                + '[Repeated](#重复-1) [Collision](#重复-1-1)\n'
                + '## **强调** 与 `code()` [链接](https://example.invalid) ![图标](assets/icon.svg)\n'
                + '[Inline](#强调-与-code-链接-图标)\n'
                + '[Encoded](references/%E6%8C%87%E5%8D%97.md#%E4%B8%AD%E6%96%87-%E6%A0%87%E9%A2%98)\n'
                + '\nSetext heading\n--------------\n[Setext](#setext-heading)\n'
            )
            case.validate()

    def test_fenced_code_does_not_create_anchors_or_links(self) -> None:
        with fixture() as case:
            case.write_skill('```md\n# Fake\n[Ignored](missing.md)\n```\n[Fake](#fake)\n')
            with self.assertRaisesRegex(ValueError, 'anchor|锚点'):
                case.validate()
            case.write_skill('```md\n# Fake\n[Ignored](missing.md)\n```\n# Real\n[Real](#real)\n')
            case.validate()

    def test_images_non_markdown_assets_and_external_urls_are_not_parsed_as_documents(self) -> None:
        with fixture() as case:
            case.write('skills/sample/assets/icon.svg', '<svg/>')
            case.write('skills/sample/assets/manual.pdf', 'not a Markdown document')
            case.write_skill(
                '![Icon](assets/icon.svg#symbol)\n'
                + '[PDF](assets/manual.pdf#page=3)\n'
                + '[Asset directory](assets/)\n'
                + '[External](https://invalid.example/missing.md#absent)\n'
                + '[Network URL](//invalid.example/missing.md#absent)\n'
                + '[Mail](mailto:example@example.invalid)\n'
            )
            case.validate()

    def test_local_targets_cannot_escape_the_skill(self) -> None:
        with fixture() as case:
            case.write('outside.md', '# Outside\n')
            for target in ('../../outside.md', '%2e%2e/%2e%2e/outside.md'):
                with self.subTest(target=target):
                    case.write_skill(f'[Outside]({target})\n')
                    with self.assertRaises(ValueError):
                        case.validate()

    def test_explicit_html_anchors_are_supported(self) -> None:
        with fixture() as case:
            case.write_skill('<a id="legacy-section"></a>\n\n[Legacy](#legacy-section)\n')
            case.validate()


if __name__ == '__main__':
    _ = unittest.main()
