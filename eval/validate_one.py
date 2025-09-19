import json, sys
from jsonschema import validate, ValidationError

def load_json_bom_safe(path: str):
    # UTF-8 BOM があってもなくてもOKで読める
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

schema = load_json_bom_safe("docs/schema.json")
j = load_json_bom_safe(sys.argv[1])

try:
    validate(j, schema)
    print("Schema: OK")
except ValidationError as e:
    print("Schema: NG")
    print(e)
