#!/usr/bin/env python3
"""为已验证的 main 提交准备已授权主版本内的发布，只回写 plugin.json 的补丁版本。"""

import json
import os
import re
import subprocess
from pathlib import Path


class Git:
    def __init__(self, root):
        self.root = root

    def run(self, *args, missing_ok=False):
        result = subprocess.run(['git', *args], cwd=self.root, text=True, capture_output=True)
        if missing_ok and result.returncode == 1:
            return None
        if result.returncode:
            raise RuntimeError(f'git {args[0]} 失败：{result.stderr.strip()}')
        return result.stdout.strip()


def version_parts(value):
    if not isinstance(value, str) or not re.fullmatch(r'[01]\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', value):
        raise ValueError('主版本仅允许已授权的 0 或 1，版本不得有前导零')
    return tuple(map(int, value.split('.')))


def release_message(version, source):
    return f'chore: 发布技能版本 {version} [skip ci]\n\nRelease-Source: {source}'


def check_existing_versions(git, version):
    current = version_parts(version)
    for tag in git.run('tag', '--list', 'v*').splitlines():
        if (re.fullmatch(r'v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', tag)
                and tuple(map(int, tag[1:].split('.'))) > current):
            raise ValueError('清单版本落后于已存在的版本标签')


def is_release_commit(git, commit, source, original, next_version):
    if (git.run('show', '-s', '--format=%P', commit) != source
            or git.run('show', '-s', '--format=%B', commit) != release_message(next_version, source)):
        return False
    manifest = json.loads(git.run('show', f'{commit}:plugin.json'))
    if (git.run('diff', '--name-only', source, commit) != 'plugin.json'
            or manifest != {**original, 'version': next_version}):
        raise ValueError('发布提交包含未经验证的额外变化')
    return True


def prepare(root, context, validate):
    if (context.get('GITHUB_ACTIONS') != 'true' or context.get('GITHUB_EVENT_NAME') != 'push'
            or context.get('GITHUB_REF') != 'refs/heads/main'):
        return {'status': 'not-main-push'}
    source = context.get('GITHUB_SHA', '')
    if not re.fullmatch(r'[0-9a-f]{40}', source):
        raise ValueError('GITHUB_SHA 必须是已验证源提交的完整 SHA')
    root = Path(root)
    manifest_path = root / 'plugin.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    version = manifest.get('version')
    major, minor, patch = version_parts(version)
    next_version = f'{major}.{minor}.{patch + 1}'
    git = Git(root)
    if git.run('status', '--porcelain'):
        raise ValueError('发布工作区必须干净')
    if git.run('rev-parse', 'HEAD') != source:
        raise ValueError('工作区 HEAD 与已验证源提交不一致')
    remote = git.run('ls-remote', 'origin', 'refs/heads/main').split()
    if len(remote) != 2 or remote[1] != 'refs/heads/main':
        raise ValueError('无法确认远端 main')
    remote_head = remote[0]
    if remote_head != source:
        git.run('fetch', 'origin', 'main')
        if not is_release_commit(git, remote_head, source, manifest, next_version):
            return {'status': 'superseded', 'commit': source}
        check_existing_versions(git, next_version)
        # 原运行可能已完成写回，但尚未创建 Release；只恢复同一个已知发布提交。
        git.run('checkout', '--detach', remote_head)
        validate(root, release_tag=f'v{next_version}')
        return {'status': 'ready', 'version': next_version, 'commit': remote_head}

    check_existing_versions(git, version)
    previous = git.run('rev-parse', '--verify', '--quiet', f'refs/tags/v{version}^{{commit}}', missing_ok=True)
    if previous is None or previous == source:
        validate(root, release_tag=f'v{version}')
        return {'status': 'ready', 'version': version, 'commit': source}
    if git.run('merge-base', '--is-ancestor', previous, source, missing_ok=True) is None:
        raise ValueError('版本标签不属于当前 main 历史')

    manifest_path.write_text(json.dumps({**manifest, 'version': next_version}, ensure_ascii=False, indent=2) + '\n',
                             encoding='utf-8')
    validate(root, release_tag=f'v{next_version}')
    if git.run('diff', '--name-only') != 'plugin.json':
        raise ValueError('发布工作区包含非版本变化')
    git.run('add', '--', 'plugin.json')
    git.run('commit', '-m', release_message(next_version, source))
    commit = git.run('rev-parse', 'HEAD')
    if (not is_release_commit(git, commit, source, manifest, next_version)
            or git.run('status', '--porcelain')):
        raise ValueError('发布提交与已验证的版本变化不一致')
    # 不强推。验证期间 main 若前进，新提交与它分叉，Git 会拒绝覆盖。
    git.run('push', 'origin', 'HEAD:refs/heads/main')
    return {'status': 'ready', 'version': next_version, 'commit': commit}


def main():
    from scripts.validate_repository import validate_repository

    try:
        result = prepare(Path(__file__).resolve().parents[1], os.environ, validate_repository)
        print(json.dumps(result, ensure_ascii=False))
        if output := os.environ.get('GITHUB_OUTPUT'):
            with Path(output).open('a', encoding='utf-8') as stream:
                stream.write(f'ready={str(result["status"] == "ready").lower()}\n')
                if result['status'] == 'ready':
                    stream.write(f'commit={result["commit"]}\nversion={result["version"]}\n')
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        raise SystemExit(f'准备发布失败：{error}') from error


if __name__ == '__main__':
    main()
