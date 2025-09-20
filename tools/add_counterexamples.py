import json, glob, os

# 既存データから各タスクの最初の1件だけに反例 witness を付与する
# 追加だけで tests は変更しません（スキーマは witness 任意フィールドOK）

def load(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save(p, j):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(j, f, ensure_ascii=False, indent=2)

seen = set()
updated = []

for p in sorted(glob.glob("data/json/*.json")):
    j = load(p)
    task = j.get("task", "")
    if task in seen:
        continue

    w = j.setdefault("witness", {})

    if task == "gcd":
        # MOD_NEGATIVE の反例：負数を含んでも gcd は正の 3
        if "counterexample_mod_negative" not in w:
            w["counterexample_mod_negative"] = {
                "in": "-6 9\n",
                "expected_out": "3\n",
                "desc": "負数の剰余や符号処理を誤る実装への反例。"
            }
            updated.append(p); seen.add(task)

    elif task.startswith("binary_search"):
        # OFF_BY_ONE：末尾一致。右端の更新バグで見落としがち
        if "counterexample_off_by_one" not in w:
            w["counterexample_off_by_one"] = {
                "in": "5\n1 3 5 7 9\n9\n",
                "expected_out": "1\n",
                "desc": "上端の更新(r=mid)などの境界バグで、末尾一致を取り逃す典型。"
            }
            updated.append(p); seen.add(task)

    elif task.startswith("interval_scheduling"):
        # END_EXCLUSIVE_CONFUSION：隣接(0,10)と(10,20)は両方選べる（>= が正）
        if "counterexample_end_exclusive" not in w:
            w["counterexample_end_exclusive"] = {
                "in": "2\n0 10\n10 20\n",
                "expected_out": "2\n",
                "desc": ">= を > と誤ると 2 本選べなくなる。半開/閉区間の取り違え。"
            }
            updated.append(p); seen.add(task)

    elif task.startswith("bfs_"):
        # INDEX_BASE_MISMATCH：入力は 1-indexed。0-index 前提の実装は壊れる
        if "counterexample_index_base_mismatch" not in w:
            w["counterexample_index_base_mismatch"] = {
                "in": "2 1 1 2\n1 2\n",
                "expected_out": "1\n",
                "desc": "1-indexed を 0-indexed と誤解すると到達不能扱いになりやすい最小例。"
            }
            updated.append(p); seen.add(task)

    # 変更あれば保存
    if p in updated:
        save(p, j)

print("updated:", len(updated))
for q in updated:
    print("  -", q)
