#!/usr/bin/env python3
"""从单一规范源生成随技能分发的快照；--check 只比较，不修改文件。"""

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

RELATIVE_LINK = re.compile(r"(?<!!)\[([^\]\n]+)\]\(([^)\s]+)\)")
SOURCE_NAME = "unif-platform-architecture/ARCHITECTURE.md"


def render(source_bytes):
    text = source_bytes.decode("utf-8")

    def portable_link(match):
        target = match.group(2)
        if urlsplit(target).scheme or target.startswith("#"):
            return match.group(0)
        return match.group(1)

    body = RELATIVE_LINK.sub(portable_link, text)
    digest = hashlib.sha256(source_bytes).hexdigest()
    header = (
        "<!-- 此文件由 scripts/sync_architecture.py 生成，请修改规范源后重新同步。\n"
        f"来源：{SOURCE_NAME}\n源文件 SHA-256：{digest}\n"
        "相对文档链接已转为文字；领域材料由目标工程按需提供。 -->\n\n"
    )
    record = {
        "source": SOURCE_NAME,
        "sourceSha256": digest,
        "transformation": "preserve-text-strip-relative-markdown-links-v1",
    }
    return {
        "platform-architecture.md": header + body,
        "source.json": json.dumps(record, ensure_ascii=False, indent=2) + "\n",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        outputs = render(args.source.read_bytes())
    except (OSError, UnicodeError) as error:
        parser.exit(2, f"规范源无法读取：{error}\n")
    destination = Path(__file__).resolve().parents[1] / "skills/architecture-design/references"
    if args.check:
        different = []
        for name, expected in outputs.items():
            path = destination / name
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                different.append(name)
        if different:
            parser.exit(1, "规范快照或来源记录不一致：" + "、".join(different) + "\n")
        print("规范快照与来源记录一致。")
        return
    destination.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        (destination / name).write_text(content, encoding="utf-8")
    print("已生成平台规范快照及来源记录。")


if __name__ == "__main__":
    main()

