#!/bin/sh
# 从本地仓库接入市场，或沿用已经配置的 Unif 市场。
set -eu

market=unif-portal-dev-skills
for plugin in "$@"; do
    case "$plugin" in
        unif-engineering-skills|unif-react-native-skills|unif-harmony-skills|unif-python-skills|unif-library-skills) ;;
        *)
            echo "未知业务插件：$plugin" >&2
            exit 2
            ;;
    esac
done

root=$(CDPATH= cd -P "$(dirname "$0")/.." && pwd)
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
