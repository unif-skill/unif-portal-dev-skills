"""Shared, offline validation of skill documents and declared UI assets."""

from collections.abc import Callable, Sequence
from html.parser import HTMLParser
from pathlib import Path
import re
from typing import TypeGuard, cast, override
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt
from markdown_it.token import Token
from skills_ref import validate as validate_skill
import yaml


load_yaml: Callable[[str], object] = yaml.safe_load
MARKDOWN_SUFFIXES = {'.md', '.markdown'}


def is_object(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict) and all(isinstance(key, str) for key in cast(dict[object, object], value))


def contained_path(root: Path, base: Path, target: object, *, directory: bool = False) -> Path:
    """Resolve a declared local target without allowing package escape."""
    if not isinstance(target, str) or not target or Path(target).is_absolute():
        raise ValueError(f'{base}: 非法相对路径 {target!r}')
    path = (base / target).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'{base}: 引用越出分发目录 {target}')
    if not (path.is_dir() if directory else path.is_file()):
        raise ValueError(f'{base}: 引用不存在 {target}')
    return path


def check_assets(root: Path, interface: object, fields: Sequence[str]) -> None:
    """Optional assets are checked only when their fields are declared."""
    if not is_object(interface):
        raise ValueError(f'{root}: interface 必须是对象')
    for field in fields:
        if field in interface:
            _ = contained_path(root, root, interface[field])


def markdown_tokens(path: Path) -> list[Token]:
    text = path.read_text(encoding='utf-8')
    # YAML metadata is not a rendered heading, including SKILL.md frontmatter.
    text = re.sub(r'\A---\n.*?\n(?:---|\.\.\.)[ \t]*(?:\n|$)', '', text, count=1, flags=re.DOTALL)
    return MarkdownIt('commonmark').parse(text)


def inline_text(tokens: Sequence[Token]) -> str:
    parts: list[str] = []
    for token in tokens:
        if token.type in ('text', 'code_inline'):
            parts.append(token.content)
        elif token.type in ('softbreak', 'hardbreak'):
            parts.append(' ')
        elif token.children:
            parts.append(inline_text(token.children))
    return ''.join(parts)


class HTMLAnchors(HTMLParser):
    """Collect explicit HTML IDs and legacy named anchors without rendering HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: set[str] = set()

    @override
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if value and (name == 'id' or (tag == 'a' and name == 'name')):
                self.anchors.add(value)


def markdown_anchors(path: Path) -> set[str]:
    """Build heading IDs from rendered inline text, including duplicate suffixes."""
    tokens = markdown_tokens(path)
    headings: set[str] = set()
    explicit = HTMLAnchors()
    pending = list(tokens)
    while pending:
        token = pending.pop()
        pending.extend(token.children or [])
        if token.type in ('html_inline', 'html_block'):
            explicit.feed(token.content)
    explicit.close()
    for index, token in enumerate(tokens):
        if token.type != 'heading_open':
            continue
        title = inline_text(tokens[index + 1].children or [])
        base = re.sub(r'[^\w -]', '', title.lower()).replace(' ', '-')
        anchor, suffix = base, 0
        while anchor in headings:
            suffix += 1
            anchor = f'{base}-{suffix}'
        headings.add(anchor)
    return headings | explicit.anchors


def check_markdown(root: Path, path: Path, *,
                   anchor_cache: dict[Path, set[str]] | None = None) -> None:
    """Validate local files and Markdown fragments; external URLs remain offline."""
    cache = anchor_cache if anchor_cache is not None else {}
    pending = markdown_tokens(path)
    while pending:
        token = pending.pop()
        pending.extend(token.children or [])
        target = token.attrGet('href') if token.type == 'link_open' else token.attrGet('src')
        if not isinstance(target, str) or not target:
            continue
        url = urlsplit(target)
        if (url.scheme and url.scheme != 'file') or (url.netloc and url.scheme != 'file'):
            continue
        if url.path:
            relative = unquote(url.path)
            local = contained_path(root, path.parent, relative, directory=(path.parent / relative).is_dir())
        else:
            local = path.resolve()
        if (url.fragment and token.type == 'link_open' and local.is_file()
                and local.suffix.lower() in MARKDOWN_SUFFIXES):
            if local not in cache:
                cache[local] = markdown_anchors(local)
            if unquote(url.fragment) not in cache[local]:
                raise ValueError(f'{path}: 锚点不存在：{target}')


def check_skill(skill: Path, *, markdown_root: Path | None = None) -> None:
    """Check the Agent Skills entry plus optional product metadata and local docs."""
    errors = validate_skill(skill)
    if errors:
        raise ValueError(f'{skill}: {"; ".join(errors)}')
    root = markdown_root if markdown_root is not None else skill
    cache: dict[Path, set[str]] = {}
    for path in skill.rglob('*'):
        if path.is_file() and path.suffix.lower() in MARKDOWN_SUFFIXES:
            _ = contained_path(skill, skill, str(path.relative_to(skill)))
            check_markdown(root, path, anchor_cache=cache)
    metadata = skill / 'agents/openai.yaml'
    if metadata.exists():
        _ = contained_path(skill, skill, 'agents/openai.yaml')
        try:
            data = load_yaml(metadata.read_text(encoding='utf-8'))
        except yaml.YAMLError as error:
            raise ValueError(f'{metadata}: {error}') from error
        if not is_object(data):
            raise ValueError(f'{metadata}: 必须是对象')
        check_assets(skill, data.get('interface', {}), ('icon_small', 'icon_large'))
