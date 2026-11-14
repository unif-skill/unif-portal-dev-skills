#!/bin/sh
# 从本地仓库接入市场，或沿用已经配置的 Unif 市场。
set -eu

market=unif-portal-dev-skills
root=$(CDPATH= cd -P "$(dirname "$0")/.." && pwd)
python3 - "$root/.agents/plugins/marketplace.json" "$@" <<'PY'
import json
import sys
from pathlib import Path

entries = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))['plugins']
available = {entry['name'] for entry in entries if entry['policy']['installation'] == 'AVAILABLE'}
for plugin in sys.argv[2:]:
    if plugin not in available:
        print(f'未知业务插件：{plugin}', file=sys.stderr)
        raise SystemExit(2)
PY

markets=$(codex plugin marketplace list --json)
registered=$(printf '%s' "$markets" | python3 -c '
import json, sys
print(any(entry["name"] == sys.argv[1] for entry in json.load(sys.stdin)["marketplaces"]))
' "$market")
if [ "$registered" = False ]; then
    codex plugin marketplace add "$root"
fi

for plugin in unif-platform-rules "$@"; do
    codex plugin add "$plugin@$market"
done
