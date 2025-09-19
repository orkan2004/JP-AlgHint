import json, subprocess, sys

def load_json_bom_safe(path: str):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

jpath = sys.argv[1]
item = load_json_bom_safe(jpath)

py = item["reference"]["py"]
t = item["tests"][0]

p = subprocess.run([sys.executable, py], input=t["in"].encode(), stdout=subprocess.PIPE)
out = p.stdout.decode()

if out.strip() == t["out"].strip():
    print("PASS")
else:
    print(f"FAIL\nexpected: {t['out']}\ngot     : {out}")
