#!/usr/bin/env python3
"""在 main 推送通过校验后发布尚未发布的 0.x.x；不修改版本或重试写请求。"""

import json
import os
import re
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class GitHub:
    def __init__(self, repository, token):
        self.repository = repository
        self.token = token

    def request(self, method, path, payload=None, *, missing_ok=False):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', self.repository) or not self.token:
            raise ValueError('发布需要合法 GITHUB_REPOSITORY 和 GH_TOKEN')
        request = Request(
            f'https://api.github.com/repos/{self.repository}/{path}',
            data=None if payload is None else json.dumps(payload).encode('utf-8'),
            method=method,
            headers={
                'Accept': 'application/vnd.github+json',
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json',
                'X-GitHub-Api-Version': '2026-03-10',
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            error.close()
            if method == 'GET' and missing_ok and error.code == 404:
                return None
            raise

    def get(self, path, *, missing_ok=False):
        return self.request('GET', path, missing_ok=missing_ok)

    def post(self, path, payload):
        return self.request('POST', path, payload)


def publish(root, context, api):
    if (context.get('GITHUB_ACTIONS') != 'true' or context.get('GITHUB_EVENT_NAME') != 'push'
            or context.get('GITHUB_REF') != 'refs/heads/main'):
        return {'status': 'not-main-push'}
    manifest = json.loads((Path(root) / 'plugin.json').read_text(encoding='utf-8'))
    version = manifest.get('version')
    if not isinstance(version, str) or not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', version):
        raise ValueError('version 必须是无前缀、无前导零的 X.Y.Z')
    if not version.startswith('0.'):
        return {'status': 'manual-review-required', 'version': version}
    commit = context.get('GITHUB_SHA', '')
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('GITHUB_SHA 必须是本次已验证提交的完整 SHA')
    if api.get('git/ref/heads/main')['object']['sha'] != commit:
        return {'status': 'superseded', 'commit': commit}

    tag = f'v{version}'
    # 按 tag 查询只返回已发布版本；列表还包含有写权限时可见的草稿。
    page = 1
    while True:
        releases = api.get(f'releases?per_page=100&page={page}')
        existing = next((item for item in releases if item.get('tag_name') == tag), None)
        if existing is not None or len(releases) < 100:
            break
        page += 1
    if existing is not None:
        if existing.get('draft') is not False or existing.get('tag_name') != tag:
            raise ValueError(f'{tag} 存在 draft 或不匹配的 Release，需要人工核对')
        return {'status': 'already-published', 'tag': tag, 'url': existing['html_url']}
    tag_ref = f'commits/refs%2Ftags%2F{tag}'
    # 不存在的 commit 查询返回 422；只有 refs 接口以 404 表达标签缺失。
    existing_tag = api.get(f'git/ref/tags/{tag}', missing_ok=True)
    tagged_commit = api.get(tag_ref) if existing_tag is not None else None
    if tagged_commit is not None and tagged_commit['sha'] != commit:
        raise ValueError(f'{tag} tag 已指向其他提交，不覆盖或发布该标签')

    # target_commitish 固定到通过上游校验的 SHA；GitHub 为不存在的 tag 创建引用。
    release = api.post('releases', {
        'tag_name': tag, 'target_commitish': commit, 'name': tag,
        'draft': False, 'prerelease': False, 'generate_release_notes': True,
    })
    if release.get('draft') is not False or release.get('tag_name') != tag:
        raise ValueError(f'{tag} 未返回已发布的 Release')
    if api.get(tag_ref)['sha'] != commit:
        raise ValueError(f'{tag} tag 与本次已验证提交不一致，需要人工核对')
    return {'status': 'published', 'tag': tag, 'url': release['html_url']}


def main():
    try:
        result = publish(
            Path(__file__).resolve().parents[1], os.environ,
            GitHub(os.environ.get('GITHUB_REPOSITORY', ''), os.environ.get('GH_TOKEN', '')),
        )
    except (OSError, ValueError, KeyError) as error:
        raise SystemExit(f'发布失败：{error}') from error
    print(json.dumps(result, ensure_ascii=False))
    if result['status'] == 'manual-review-required':
        print('::notice::1.0.0 及以上版本须经用户审核后人工发布，自动发布已跳过。')


if __name__ == '__main__':
    main()
