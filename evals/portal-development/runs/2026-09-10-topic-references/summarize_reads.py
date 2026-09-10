"""用冻结输入复核每次资料输出的摘要，并汇总累计字符与 UTF-8 字节；只读。"""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
summary = {}
for trace in sorted((root / 'traces').glob('*.jsonl')):
    total = {'characters': 0, 'bytes': 0, 'reads': 0}
    for line in trace.read_text(encoding='utf-8').splitlines():
        record = json.loads(line)
        variant = Path(record['root']).name
        assert variant in ('before', 'after', 'cases'), record
        base = (root / 'inputs' / variant).resolve()
        path = (base / record['file']).resolve()
        assert path.is_relative_to(base), record
        source = path.read_text(encoding='utf-8')
        lines = source.splitlines(keepends=True)
        if record['mode'] == 'full':
            output = source
        elif record['mode'] == 'headings':
            output = ''.join(f'{i}: {text}' for i, text in enumerate(lines, 1) if text.startswith('#'))
        else:
            assert record['mode'] == 'lines', record
            start, end = map(int, record['range'].split(':'))
            assert 1 <= start <= end <= len(lines), record
            output = ''.join(lines[start - 1:end])
        assert len(output) == record['characters'], record
        assert len(output.encode()) == record['bytes'], record
        assert hashlib.sha256(output.encode()).hexdigest() == record['sha256'], record
        if variant != 'cases':
            total['characters'] += record['characters']
            total['bytes'] += record['bytes']
            total['reads'] += 1
    summary[trace.stem] = total
print(json.dumps(summary, ensure_ascii=False, indent=2))
