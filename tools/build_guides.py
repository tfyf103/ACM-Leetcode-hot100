"""Combine authored teaching notes; no network, generated prose, or execution."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('guide_schema', ROOT / 'catalog/guide_schema.py')
schema = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schema)


def build():
    guides = {}
    for path in sorted((ROOT / 'tools/guide_notes').glob('*.json')):
        entries = json.loads(path.read_text(encoding='utf-8'))
        if set(guides) & set(entries):
            raise ValueError('Duplicate guide in ' + path.name)
        guides.update(entries)
    expected = json.loads((ROOT / 'catalog/tutorials.json').read_text(encoding='utf-8'))
    schema.validate_guides(guides, expected)
    destination = ROOT / 'catalog/guides.json'
    destination.write_text(json.dumps(guides, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Wrote %d complete guided tutorials.' % len(guides))


if __name__ == '__main__':
    build()
