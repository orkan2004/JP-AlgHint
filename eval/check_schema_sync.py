import json, sys, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
a = json.loads((root/'docs/schema.json').read_text(encoding='utf-8'))
b = json.loads((root/'eval/schema.json').read_text(encoding='utf-8'))
if a != b:
    print('docs/schema.json と eval/schema.json が一致しません', file=sys.stderr)
    sys.exit(1)
print('schemas are in sync')


