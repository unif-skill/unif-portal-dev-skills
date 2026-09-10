"""评测用只读资料输出器：记录实际返回文本，不估算模型 Token。"""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('root', type=Path)
p.add_argument('file')
p.add_argument('--log', required=True, type=Path)
g = p.add_mutually_exclusive_group()
g.add_argument('--lines', help='1-based inclusive START:END')
g.add_argument('--headings', action='store_true')
a = p.parse_args()
root = a.root.resolve()
path = (root / a.file).resolve()
if not path.is_relative_to(root) or not path.is_file():
    p.error('file must exist inside root')
source = path.read_text(encoding='utf-8')
lines = source.splitlines(keepends=True)
mode = 'full'
if a.lines:
    start, end = map(int, a.lines.split(':'))
    if not 1 <= start <= end <= len(lines):
        p.error('invalid line range')
    output = ''.join(lines[start - 1:end])
    mode = 'lines'
elif a.headings:
    output = ''.join(f'{i}: {line}' for i, line in enumerate(lines, 1) if line.startswith('#'))
    mode = 'headings'
else:
    output = source
record = {'root': str(root), 'file': str(path.relative_to(root)), 'mode': mode,
          'range': a.lines, 'characters': len(output), 'bytes': len(output.encode()),
          'sha256': hashlib.sha256(output.encode()).hexdigest()}
a.log.parent.mkdir(parents=True, exist_ok=True)
with a.log.open('a', encoding='utf-8') as f:
    f.write(json.dumps(record, ensure_ascii=False) + '\n')
print(output, end='')
