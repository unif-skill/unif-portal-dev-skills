#!/usr/bin/env python3
"""显式采用 Uni 的通用技能校验；--verify 仅核对本仓副本与摘要。"""

import argparse
from collections.abc import Callable
import hashlib
import json
from pathlib import Path
import re
from typing import TypeGuard, TypedDict


FILES = (
    'scripts/skill_validation.py', 'scripts/sync_validation_tools.py',
    'scripts/requirements-skill-validation.txt', 'typings/skills_ref/__init__.pyi',
    'tests/test_skill_validation.py', 'tests/test_sync_validation_tools.py',
)
RECORD = 'scripts/validation-tools.json'
SOURCE = 'unif-skill/uni-skills'
load_json: Callable[[str], object] = json.loads


class AdoptionRecord(TypedDict):
    formatVersion: int
    source: str
    files: dict[str, str]


def is_mapping(value: object) -> TypeGuard[dict[object, object]]:
    return isinstance(value, dict)


def is_record(value: object) -> TypeGuard[AdoptionRecord]:
    if (not is_mapping(value) or type(value.get('formatVersion')) is not int
            or value.get('formatVersion') != 1 or value.get('source') != SOURCE):
        return False
    files = value.get('files')
    return (is_mapping(files) and set(files) == set(FILES)
            and all(isinstance(name, str) and isinstance(digest, str) for name, digest in files.items()))


def managed_path(root: Path, relative: str) -> Path:
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f'仓库必须是普通目录：{root}')
    path = root
    for part in Path(relative).parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f'受管路径不能是符号链接：{path}')
        if path.exists() and not (path.is_file() if path == root / relative else path.is_dir()):
            raise ValueError(f'受管路径类型无效：{path}')
    return path


def package_name(root: Path) -> str:
    value = load_json(managed_path(root, 'plugin.json').read_text(encoding='utf-8'))
    name = value.get('name') if is_mapping(value) else None
    if not isinstance(name, str):
        raise ValueError('插件清单缺少有效 name')
    return name


def check_validation_tools(root: str | Path) -> AdoptionRecord | None:
    root = Path(root)
    name = package_name(root)
    if name == 'uni-skills':
        return None
    if name != 'unif-portal-dev-skills':
        raise ValueError('不支持的通用校验采用仓')
    record = load_json(managed_path(root, RECORD).read_text(encoding='utf-8'))
    if not is_record(record):
        raise ValueError('通用校验工具来源或受管文件集合无效')
    for relative, digest in record['files'].items():
        path = managed_path(root, relative)
        if (not re.fullmatch(r'[0-9a-f]{64}', digest) or not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != digest):
            raise ValueError(f'通用校验工具与采用摘要不一致：{relative}')
    return record


def sync_validation_tools(source: str | Path, target: str | Path, *, check: bool = False) -> None:
    source, target = Path(source), Path(target)
    if package_name(source) != 'uni-skills' or package_name(target) != 'unif-portal-dev-skills':
        raise ValueError('来源必须是 Uni 技能仓，采用方必须是 Unif 技能仓')
    contents = {name: managed_path(source, name).read_bytes() for name in FILES}
    targets = {name: managed_path(target, name) for name in FILES}
    record_path = managed_path(target, RECORD)
    expected: AdoptionRecord = {
        'formatVersion': 1, 'source': SOURCE,
        'files': {name: hashlib.sha256(data).hexdigest() for name, data in contents.items()},
    }
    if record_path.exists():
        adopted = check_validation_tools(target)
        if check:
            if adopted != expected:
                raise ValueError('通用校验工具与指定来源不同，请审查后同步')
            return
    elif check:
        raise ValueError('尚无通用校验工具采用记录')
    else:
        for name, path in targets.items():
            if path.exists() and path.read_bytes() != contents[name]:
                raise ValueError(f'拒绝覆盖未纳管文件：{name}')
    for name, path in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_bytes(contents[name])
    record_path.parent.mkdir(parents=True, exist_ok=True)
    _ = record_path.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    _ = check_validation_tools(target)


class Arguments(argparse.Namespace):
    source: Path | None = None
    target: Path = Path(__file__).resolve().parents[1]
    check: bool = False
    verify: bool = False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument('--source', type=Path)
    _ = parser.add_argument('--target', type=Path, default=Path(__file__).resolve().parents[1])
    _ = parser.add_argument('--check', action='store_true')
    _ = parser.add_argument('--verify', action='store_true')
    args = parser.parse_args(namespace=Arguments())
    if args.verify and (args.source or args.check):
        parser.error('--verify 只核对本仓采用，不同时指定来源或 --check')
    if not args.verify and args.source is None:
        parser.error('同步或比较需 --source；仅核对采用记录用 --verify')
    try:
        if args.verify:
            _ = check_validation_tools(args.target)
        elif args.source is not None:
            sync_validation_tools(args.source, args.target, check=args.check)
    except (OSError, ValueError) as error:
        parser.exit(1, f'通用校验工具检查失败：{error}\n')
    print('通用校验工具检查通过。' if args.verify or args.check else '已同步通用校验工具与来源摘要。')


if __name__ == '__main__':
    main()
