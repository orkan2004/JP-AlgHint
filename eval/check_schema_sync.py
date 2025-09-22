# eval/check_schema_sync.py
from pathlib import Path
import json, sys, difflib

def load_json(path: str):
    # BOM あり/なし両対応
    text = Path(path).read_text(encoding="utf-8-sig")
    return json.loads(text)

docs = load_json("docs/schema.json")
eval_ = load_json("eval/schema.json")

if docs != eval_:
    print("ERROR: docs/schema.json と eval/schema.json が一致していません。差分を表示します。\n")
    sa = json.dumps(docs, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    sb = json.dumps(eval_, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    for line in difflib.unified_diff(
        sa.splitlines(), sb.splitlines(),
        fromfile="docs/schema.json", tofile="eval/schema.json", lineterm=""
    ):
        print(line)
    sys.exit(1)

print("OK: schema files are in sync.")
