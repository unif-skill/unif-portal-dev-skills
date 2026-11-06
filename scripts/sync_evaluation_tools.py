#!/usr/bin/env python3
"""显式同步 Uni 维护的行为评测工具；--verify 仅核对本仓采用摘要。"""

import argparse
from collections.abc import Callable
import hashlib
import json
from pathlib import Path
import re
from typing import TypeGuard, TypedDict


FILES = ('scripts/behavior_eval.py', 'scripts/sync_evaluation_tools.py',
         'tests/test_behavior_eval.py', 'tests/test_behavior_eval_runtime.py',
         'tests/test_sync_evaluation_tools.py', '.github/workflows/behavior-eval.yml')
# Published consumers before runtime retry tests have five managed files. They
# may be upgraded explicitly, but do not pass verification as the new version.
PREVIOUS_FILES = tuple(name for name in FILES if name != 'tests/test_behavior_eval_runtime.py')
RECORD = 'scripts/evaluation-tools.json'
SOURCE = 'unif-skill/uni-skills'
load_json: Callable[[str], object] = json.loads


class AdoptionRecord(TypedDict):
    formatVersion: int
    source: str
    files: dict[str, str]


def is_mapping(value: object) -> TypeGuard[dict[object, object]]:
    return isinstance(value, dict)


def is_record(value: object, allow_previous: bool) -> TypeGuard[AdoptionRecord]:
    if not is_mapping(value) or type(value.get('formatVersion')) is not int or value['formatVersion'] != 1:
        return False
    if value.get('source') != SOURCE:
        return False
    files = value.get('files')
    if not is_mapping(files):
        return False
    allowed = set(files) == set(FILES) or (allow_previous and set(files) == set(PREVIOUS_FILES))
    return allowed and all(isinstance(name, str) and isinstance(digest, str) for name, digest in files.items())


def managed_path(root: Path, name: str) -> Path:
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f'仓库必须是普通目录：{root}')
    path = root
    for part in Path(name).parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f'受管路径不能是符号链接：{path}')
        if path.exists() and not (path.is_file() if path == root / name else path.is_dir()):
            raise ValueError(f'受管路径类型无效：{path}')
    return path


def package_name(root: Path) -> str:
    manifest = load_json(managed_path(root, 'plugin.json').read_text(encoding='utf-8'))
    name = manifest.get('name') if is_mapping(manifest) else None
    if not isinstance(name, str):
        raise ValueError('插件清单缺少有效 name')
    return name


def check_evaluation_tools(root: str | Path, *, allow_previous: bool = False) -> AdoptionRecord | None:
    root = Path(root)
    name = package_name(root)
    if name == 'uni-skills':
        return None
    if name != 'unif-portal-dev-skills':
        raise ValueError('不支持的行为评测采用仓')
    record = load_json(managed_path(root, RECORD).read_text(encoding='utf-8'))
    if not is_record(record, allow_previous):
        raise ValueError('行为评测工具来源或文件集合无效')
    for file, digest in record['files'].items():
        path = managed_path(root, file)
        if (not re.fullmatch(r'[0-9a-f]{64}', digest)
                or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest):
            raise ValueError(f'行为评测工具与采用摘要不一致：{file}')
    return record


def sync_evaluation_tools(source: str | Path, target: str | Path, *, check: bool = False) -> None:
    source, target = Path(source), Path(target)
    if package_name(source) != 'uni-skills' or package_name(target) != 'unif-portal-dev-skills':
        raise ValueError('来源必须是 Uni 技能仓，采用方必须是 Unif 技能仓')
    contents = {name: managed_path(source, name).read_bytes() for name in FILES}
    paths = {name: managed_path(target, name) for name in FILES}
    record_path = managed_path(target, RECORD)
    expected: AdoptionRecord = {'formatVersion': 1, 'source': SOURCE,
                'files': {name: hashlib.sha256(data).hexdigest() for name, data in contents.items()}}
    adopted: AdoptionRecord | None = None
    if record_path.exists():
        adopted = check_evaluation_tools(target, allow_previous=not check)
        if check:
            if adopted != expected:
                raise ValueError('行为评测工具与指定来源不同，请审查后同步')
            return
    elif check:
        raise ValueError('尚无行为评测工具采用记录')
    for name, path in paths.items():
        if adopted is not None and name in adopted['files']:
            continue
        if path.exists() and path.read_bytes() != contents[name]:
            raise ValueError(f'拒绝覆盖未纳管文件：{name}')
    for name, path in paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_bytes(contents[name])
    record_path.parent.mkdir(parents=True, exist_ok=True)
    _ = record_path.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    _ = check_evaluation_tools(target)


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
        parser.error('--verify 只核对当前采用，不同时指定来源或 --check')
    if not args.verify and not args.source:
        parser.error('同步或比较需 --source；仅核对采用记录用 --verify')
    try:
        if args.verify:
            _ = check_evaluation_tools(args.target)
        elif args.source is not None:
            sync_evaluation_tools(args.source, args.target, check=args.check)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'行为评测工具检查失败：{error}\n')
    print('行为评测工具检查通过。' if args.verify or args.check else '已同步行为评测工具与来源摘要。')


if __name__ == '__main__':
    main()
