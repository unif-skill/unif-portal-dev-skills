"""从冻结材料重建读取输出，验证版本隔离和摘要；不计模型 Token。"""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
summary = {}
for trace in sorted((root / 'traces').glob('*.jsonl')):
    variant = trace.stem.split('-', 1)[0]
    files = []
    for line in trace.read_text(encoding='utf-8').splitlines():
        record = json.loads(line)
        group = Path(record['root']).name
        assert group in (variant, 'cases'), record
        base = (root / 'cases' if group == 'cases' else root / 'inputs' / group).resolve()
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
        if group != 'cases' and record['file'] not in files:
            files.append(record['file'])
    summary[trace.stem] = files
print(json.dumps(summary, ensure_ascii=False, indent=2))
