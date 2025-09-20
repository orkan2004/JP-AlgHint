import json, random, time
from pathlib import Path

TODAY = time.strftime("%Y%m%d")
def new_id(i): return f"KNAP_{TODAY}_{i:05d}"

def knap_solve(w, v, W):
    n = len(w)
    dp = [[0]*(W+1) for _ in range(n+1)]
    for i in range(n):
        wi, vi = w[i], v[i]
        for cap in range(W+1):
            dp[i+1][cap] = dp[i][cap]
            if wi <= cap:
                cand = dp[i][cap-wi] + vi
                if cand > dp[i+1][cap]:
                    dp[i+1][cap] = cand
    # 復元（0-based indices）
    cap = W
    chosen = []
    for i in range(n, 0, -1):
        if dp[i][cap] != dp[i-1][cap]:
            chosen.append(i-1); cap -= w[i-1]
    chosen.reverse()
    return dp[n][W], chosen

def build_input(w, v, W):
    lines = [f"{len(w)} {W}"] + [f"{w[i]} {v[i]}" for i in range(len(w))]
    return "\n".join(lines) + "\n"

def gen_one(r, i):
    n = r.randint(8, 25)
    w = [r.randint(1, 30) for _ in range(n)]
    v = [r.randint(1, 100) for _ in range(n)]
    W = int(sum(w) * r.uniform(0.4, 0.6))

    # test1: 通常ケース
    opt1, ch1 = knap_solve(w, v, W)
    t1 = {"in": build_input(w, v, W), "out": f"{opt1}\n"}

    # test2: 境界寄せ（重い高価品 vs 軽い複数）
    # 1つ重い/高価なアイテムを注入して選択の分岐を作る
    w2 = list(w); v2 = list(v)
    heavy_w = max(5, int(W*0.6))
    heavy_v = max(120, int(sum(v)//n)) + r.randint(20, 80)
    w2.append(heavy_w); v2.append(heavy_v)
    opt2, ch2 = knap_solve(w2, v2, W)
    t2 = {"in": build_input(w2, v2, W), "out": f"{opt2}\n"}

    return {
        "id": new_id(i),
        "version": "1.0",
        "lang": "ja",
        "task_family": "knapsack_01",
        "answer_type": "int",
        "task": "knapsack_01",
        "statement_ja": "重さ w_i と価値 v_i の品物から、容量 W を超えないように選んで価値合計を最大化せよ（各品物は高々1個）。",
        "io_spec": {"input": "n W\\n(w v)×n", "output": "最大価値（整数）"},
        "instance": {"seed": i, "template_id": "KNAP_T1", "params": {"n": n, "W": W}},
        "tests": [t1, t2],
        "reference": {"py": "ref/py/knap01.py"},
        "hints": [
            {"level": 1, "text": "0/1ナップサックは DP（容量方向）で解く。"},
            {"level": 2, "text": "dp[cap] を容量 cap の最大価値として、各品物を後ろ向きに更新。"},
            {"level": 3, "text": "復元は dp の差分から選択アイテムを逆順に辿る。"}
        ],
        "distractors": [
            {"code": "TAKE_MAX_VALUE_ONLY", "desc": "価値の大きい順に貪欲に取ってしまう誤り"},
            {"code": "WRONG_GREEDY_ORDER", "desc": "価値/重さ比のみで貪欲に決める誤り（0/1では最適保証がない）"},
            {"code": "OVERFLOW_EDGE_IGNORED", "desc": "容量境界での等号扱いを誤る"}
        ],
        "witness": {"opt_value_t1": opt1, "chosen_items_t1": ch1,
                    "opt_value_t2": opt2, "chosen_items_t2": ch2},
        "difficulty": {"score": 0.45, "basis": "O(nW) DP with reconstruction"},
        "tags": ["dp", "simulation", "intermediate"],
        "license": "CC BY-SA 4.0 (texts) / MIT (code)"
    }

def main(n=30):
    r = random.Random(20240920)
    Path("data/json").mkdir(parents=True, exist_ok=True)
    for i in range(1, n+1):
        item = gen_one(r, i)
        path = Path("data/json") / f"{item['id']}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(item, f, ensure_ascii=False, indent=2)
    print(f"generated {n} KNAP items for {TODAY}")

if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv)>1 else 30
    main(n)
