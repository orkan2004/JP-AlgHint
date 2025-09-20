import json, random, time
from pathlib import Path

TODAY = time.strftime("%Y%m%d")
def new_id(i): return f"RSQ_{TODAY}_{i:05d}"

def build_case(a, queries):
    n = len(a); q = len(queries)
    lines = [f"{n} {q}", " ".join(map(str, a))]
    for l, r in queries: lines.append(f"{l} {r}")
    # 答え生成
    pref = [0]*(n+1)
    for i in range(n): pref[i+1] = pref[i] + a[i]
    ans = [str(pref[r] - pref[l-1]) for l, r in queries]
    return {"in": "\n".join(lines) + "\n", "out": "\n".join(ans) + "\n"}

def gen_one(r, i):
    n = r.randint(12, 60)
    a = [r.randint(-100, 100) for _ in range(n)]
    # テスト1: ランダム
    q1 = r.randint(12, 60)
    queries1 = []
    for _ in range(q1):
        x, y = sorted(r.sample(range(1, n+1), 2))
        queries1.append((x, y))
    t1 = build_case(a, queries1)
    # テスト2: 端寄せ（境界・単一点・全区間）
    pts = [(1, 1), (n, n), (1, n)]
    for _ in range(max(9, n//4)):
        x, y = sorted(r.sample(range(1, n+1), 2))
        pts.append((x, y))
    t2 = build_case(a, pts)

    return {
        "id": new_id(i),
        "version": "1.0",
        "lang": "ja",
        "task_family": "range_sum_query",
        "answer_type": "lines",
        "task": "rsq_prefix",
        "statement_ja": "配列 a と Q 個の区間 [l,r] (1-indexed, 閉区間) が与えられる。各区間の和を求めよ。",
        "io_spec": {"input": "n Q\\na_1 .. a_n\\n(l r)×Q", "output": "各クエリの区間和（改行区切り）"},
        "instance": {"seed": i, "template_id": "RSQ_T1", "params": {"n": n}},
        "tests": [t1, t2],
        "reference": {"py": "ref/py/rsq_prefix.py"},
        "hints": [
            {"level": 1, "text": "累積和を作ると O(1) で区間和が出せる。"},
            {"level": 2, "text": "pref[i] = a_1+…+a_i、答えは pref[r]-pref[l-1]。"},
            {"level": 3, "text": "1-indexed の境界 (l-1) を忘れないこと。"}
        ],
        "distractors": [
            {"code": "OFF_BY_ONE_L", "desc": "pref[r]-pref[l] としてしまう"},
            {"code": "ZERO_INDEX_INPUT", "desc": "入力1-indexedを0-index前提で処理"},
            {"code": "REBUILD_EACH_QUERY", "desc": "毎回部分和をループで足す O(nQ)"}
        ],
        "witness": {"array_len": n, "sample_queries": pts[:3]},
        "difficulty": {"score": 0.25, "basis": "prefix sum basics"},
        "tags": ["array", "prefix_sum", "beginner"],
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
    print(f"generated {n} RSQ items for {TODAY}")

if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv)>1 else 30
    main(n)
