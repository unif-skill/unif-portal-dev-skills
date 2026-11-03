#!/usr/bin/env python3
"""显式同步 Uni 维护的行为评测工具；--verify 仅核对本仓采用摘要。"""

import argparse
import hashlib
import json
from pathlib import Path
import re


FILES = ('scripts/behavior_eval.py', 'scripts/sync_evaluation_tools.py',
         'tests/test_behavior_eval.py', 'tests/test_sync_evaluation_tools.py',
         '.github/workflows/behavior-eval.yml')
RECORD = 'scripts/evaluation-tools.json'
SOURCE = 'unif-skill/uni-skills'


def managed_path(root, name):
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


def package_name(root):
    return json.loads(managed_path(root, 'plugin.json').read_text(encoding='utf-8'))['name']


def check_evaluation_tools(root):
    root = Path(root)
    name = package_name(root)
    if name == 'uni-skills':
        return None
    if name != 'unif-portal-dev-skills':
        raise ValueError('不支持的行为评测采用仓')
    record = json.loads(managed_path(root, RECORD).read_text(encoding='utf-8'))
    if (not isinstance(record, dict) or record.get('formatVersion') != 1
            or record.get('source') != SOURCE or not isinstance(record.get('files'), dict)
            or set(record['files']) != set(FILES)):
        raise ValueError('行为评测工具来源或文件集合无效')
    for file in FILES:
        digest = record['files'][file]
        path = managed_path(root, file)
        if (not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest)
                or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest):
            raise ValueError(f'行为评测工具与采用摘要不一致：{file}')
    return record


def sync_evaluation_tools(source, target, *, check=False):
    source, target = Path(source), Path(target)
    if package_name(source) != 'uni-skills' or package_name(target) != 'unif-portal-dev-skills':
        raise ValueError('来源必须是 Uni 技能仓，采用方必须是 Unif 技能仓')
    contents = {name: managed_path(source, name).read_bytes() for name in FILES}
    paths = {name: managed_path(target, name) for name in FILES}
    record_path = managed_path(target, RECORD)
    expected = {'formatVersion': 1, 'source': SOURCE,
                'files': {name: hashlib.sha256(data).hexdigest() for name, data in contents.items()}}
    if record_path.exists():
        adopted = check_evaluation_tools(target)
        if check:
            if adopted != expected:
                raise ValueError('行为评测工具与指定来源不同，请审查后同步')
            return
    elif check:
        raise ValueError('尚无行为评测工具采用记录')
    else:
        for name, path in paths.items():
            if path.exists() and path.read_bytes() != contents[name]:
                raise ValueError(f'拒绝覆盖未纳管文件：{name}')
    for name, path in paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents[name])
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    check_evaluation_tools(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--target', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.verify and (args.source or args.check):
        parser.error('--verify 只核对当前采用，不同时指定来源或 --check')
    if not args.verify and not args.source:
        parser.error('同步或比较需 --source；仅核对采用记录用 --verify')
    try:
        if args.verify:
            check_evaluation_tools(args.target)
        else:
            sync_evaluation_tools(args.source, args.target, check=args.check)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'行为评测工具检查失败：{error}\n')
    print('行为评测工具检查通过。' if args.verify or args.check else '已同步行为评测工具与来源摘要。')


if __name__ == '__main__':
    main()
