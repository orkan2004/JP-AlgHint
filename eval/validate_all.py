import json, glob
from jsonschema import validate, ValidationError

def load_bom(path): 
    import json
    with open(path,"r",encoding="utf-8-sig") as f: 
        return json.load(f)

schema = load_bom("docs/schema.json")
fails = 0
for p in glob.glob("data/json/*.json"):
    try:
        validate(load_bom(p), schema)
        print("OK  ", p)
    except ValidationError as e:
        print("FAIL", p); print(" ", e); fails += 1
print("----")
print("All good!" if fails==0 else f"{fails} file(s) failed.")
