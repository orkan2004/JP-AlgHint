import json, glob

def load(p):  # BOM許容
    import io
    with io.open(p, "r", encoding="utf-8-sig") as f: return json.load(f)
def save(p,j):
    with open(p,"w",encoding="utf-8") as f: json.dump(j,f,ensure_ascii=False,indent=2)

seen=set(); updated=[]
for p in sorted(glob.glob("data/json/*.json")):
    j=load(p); task=j.get("task","")
    if task in seen: continue
    w=j.setdefault("witness",{})

    if task=="gcd" and "counterexample_mod_negative" not in w:
        w["counterexample_mod_negative"]={"in":"-6 9\n","expected_out":"3\n","desc":"負数の剰余/符号処理を誤る実装への反例"}
        updated.append(p); seen.add(task)

    elif task.startswith("binary_search") and "counterexample_off_by_one" not in w:
        w["counterexample_off_by_one"]={"in":"5\n1 3 5 7 9\n9\n","expected_out":"1\n","desc":"末尾一致で取り逃す境界バグの典型"}
        updated.append(p); seen.add(task)

    elif task.startswith("interval_scheduling") and "counterexample_end_exclusive" not in w:
        w["counterexample_end_exclusive"]={"in":"2\n0 10\n10 20\n","expected_out":"2\n","desc":">= を > にすると2本選べない半開/閉区間ミス"}
        updated.append(p); seen.add(task)

    elif task.startswith("bfs_") and "counterexample_index_base_mismatch" not in w:
        w["counterexample_index_base_mismatch"]={"in":"2 1 1 2\n1 2\n","expected_out":"1\n","desc":"1-indexed入力を0-index扱いするミスの最小例"}
        updated.append(p); seen.add(task)

    if p in updated: save(p,j)

print("updated:",len(updated))
for q in updated: print("  -",q)
