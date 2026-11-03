#!/usr/bin/env python3
"""从根 skills 生成五个独立插件；--check 只核对完整内容，不写文件。"""

import argparse
import json
from pathlib import Path

GROUPS = {
    'unif-engineering-skills': ('企业工程共用规范', ('unif-architecture-design', 'unif-code-delivery')),
    'unif-rn-skills': ('React Native 企业开发、测试与审查', ('unif-rn-dev', 'unif-rn-test', 'unif-rn-review')),
    'unif-harmony-skills': ('原生鸿蒙企业开发、测试与审查', ('unif-harmony-dev', 'unif-harmony-test', 'unif-harmony-review')),
    'unif-python-skills': ('Python 企业开发、测试与审查', ('unif-python-dev', 'unif-python-test', 'unif-python-review')),
    'unif-library-skills': ('Unif 十一个库能力，双平台契约保留在同一技能', tuple('unif-' + name for name in
        ('amap', 'camera', 'chat', 'design', 'files', 'hms-scan', 'icons', 'logger', 'oss', 'speech', 'umeng'))),
}


def json_bytes(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def ordinary_tree(path):
    if path.is_symlink() or any(p.is_symlink() for p in path.rglob('*')):
        raise ValueError(f'分发来源及目标不得含符号链接：{path}')


def expected_files(root):
    root = Path(root).resolve()
    for name, required in (('plugin.json', True), ('LICENSE', False)):
        path = root / name
        if path.is_symlink():
            raise ValueError(f'分发来源不得含符号链接：{path}')
        if not path.is_file() and (required or path.exists()):
            raise ValueError(f'分发来源必须是普通文件：{path}')
    ordinary_tree(root / 'skills')
    ordinary_tree(root / 'assets')
    manifest = json.loads((root / 'plugin.json').read_text(encoding='utf-8'))
    skill_names = [skill for _, skills in GROUPS.values() for skill in skills]
    if len(set(skill_names)) != len(skill_names) or set(skill_names) != {p.name for p in (root / 'skills').iterdir() if p.is_dir()}:
        raise ValueError('五插件分组必须恰好覆盖全部技能源且不得重复')
    expected = {}
    for name, (description, skills) in GROUPS.items():
        base = f'plugins/{name}'
        expected[f'{base}/plugin.json'] = json_bytes({**manifest, 'name': name, 'description': description})
        for directory in [root / 'assets', *(root / 'skills' / skill for skill in skills)]:
            for path in sorted(directory.rglob('*')):
                if path.is_file():
                    expected[f'{base}/{path.relative_to(root)}'] = path.read_bytes()
        if (root / 'LICENSE').is_file():
            expected[f'{base}/LICENSE'] = (root / 'LICENSE').read_bytes()
    return expected


def sync_plugins(root, *, check=False):
    root = Path(root).resolve()
    ordinary_tree(root / 'plugins')
    expected = expected_files(root)
    existing = {str(p.relative_to(root)) for p in (root / 'plugins').rglob('*') if p.is_file()}
    extra = existing - expected.keys()
    if extra:
        raise ValueError(f'插件目录存在非生成文件，请先核对归属：{sorted(extra)}')
    different = [name for name, data in expected.items()
                 if not (root / name).is_file() or (root / name).read_bytes() != data]
    if check and different:
        raise ValueError(f'插件分发副本与根技能源不一致：{different[:5]}（共 {len(different)} 项）')
    if not check:
        for name in different:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(expected[name])
    return len(GROUPS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        count = sync_plugins(args.root, check=args.check)
    except (OSError, ValueError) as error:
        parser.exit(1, f'五插件同步失败：{error}\n')
    print(f'五插件{"校验" if args.check else "同步"}通过：{count} 个插件。')


if __name__ == '__main__':
    main()
