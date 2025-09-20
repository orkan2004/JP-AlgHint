import json, random, time
from pathlib import Path

TODAY = time.strftime("%Y%m%d")
def new_id(i): return f"UF_{TODAY}_{i:05d}"

def build_case(n, comps, extra_edges_ratio, q_within=0.5, q_total=60, r=None):
    if r is None: r = random
    # 辺生成：各成分を木で繋いでから少しだけ追加辺
    edges = set()
    for comp in comps:
        for i in range(1, len(comp)):
            u = r.choice(comp[:i]); v = comp[i]
            if u > v: u, v = v, u
            edges.add((u, v))
        extra = max(0, int(len(comp) * extra_edges_ratio))
        for _ in range(extra):
            u, v = r.sample(comp, 2)
            if u > v: u, v = v, u
            edges.add((u, v))

    # DSUで答えを作る
    parent = list(range(n+1))
    size = [1]*(n+1)
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]
            x=parent[x]
        return x
    def unite(a,b):
        ra, rb = find(a), find(b)
        if ra==rb: return
        if size[ra]<size[rb]: ra,rb=rb,ra
        parent[rb]=ra; size[ra]+=size[rb]
    for u,v in edges: unite(u,v)

    # クエリ生成：同成分/別成分を所定の比率で
    queries = []
    need_within = int(q_total*q_within)
    need_cross  = q_total - need_within

    # 事前に代表ノードセットを構築
    rep = {}
    for comp in comps:
        r0 = find(comp[0])
        rep.setdefault(r0, []).extend(comp)
    comp_lists = list(rep.values())

    # within
    while need_within>0:
        comp = r.choice(comp_lists)
        if len(comp) == 1: continue
        a, b = r.sample(comp, 2)
        queries.append((a,b)); need_within -= 1
    # cross
    if len(comp_lists) >= 2:
        while need_cross>0:
            c1, c2 = r.sample(comp_lists, 2)
            a = r.choice(c1); b = r.choice(c2)
            queries.append((a,b)); need_cross -= 1
    else:
        # 成分が1つしかない場合は within で埋める
        for _ in range(need_cross):
            comp = comp_lists[0]
            if len(comp) >= 2:
                a, b = r.sample(comp, 2)
                queries.append((a,b))

    # I/O 文字列
    lines = [f"{n} {len(edges)} {len(queries)}"]
    for u,v in sorted(edges): lines.append(f"{u} {v}")
    for a,b in queries: lines.append(f"{a} {b}")
    # 答え作成
    ans = []
    for a,b in queries:
        ans.append("1" if find(a)==find(b) else "0")
    return {"in": "\n".join(lines)+"\n", "out": "\n".join(ans)+"\n"}, edges, queries, ans.count("1"), ans.count("0")

def split_into_k(n, k, r):
    ids = list(range(1, n+1))
    r.shuffle(ids)
    parts = []
    base = 0
    for i in range(k):
        # 均等＋揺らぎ
        size = n//k + (1 if i < n%k else 0)
        parts.append(ids[base:base+size])
        base += size
    return parts

def gen_one(r, i):
    n = r.randint(12, 60)

    # test1: 複数成分（YES/NOが半々程度）
    k = r.randint(2, min(5, n))
    comps = split_into_k(n, k, r)
    t1, E1, Q1, yes1, no1 = build_case(n, comps, extra_edges_ratio=0.6, q_within=0.5, q_total=r.randint(40,80), r=r)

    # test2: 同じ成分分割だが within を多め（YESが多め）
    t2, E2, Q2, yes2, no2 = build_case(n, comps, extra_edges_ratio=1.0, q_within=0.8, q_total=r.randint(30,60), r=r)

    return {
        "id": new_id(i),
        "version": "1.0",
        "lang": "ja",
        "task_family": "union_find_connectivity",
        "answer_type": "lines",
        "task": "uf_connect",
        "statement_ja": "無向グラフ G(V,E) と Q 個の質問 (a,b) が与えられる。Union-Find を用いて、a と b が同じ連結成分かを判定せよ（同じなら 1、異なるなら 0）。",
        "io_spec": {"input": "n m Q\\n(u v)×m\\n(a b)×Q（すべて 1-indexed）", "output": "各クエリに対する 1/0（改行区切り）"},
        "instance": {"seed": i, "template_id": "UF_T1", "params": {"n": n}},
        "tests": [t1, t2],
        "reference": {"py": "ref/py/uf_connect.py"},
        "hints": [
            {"level": 1, "text": "辺をすべて unite してから same(a,b) を判定する。"},
            {"level": 2, "text": "経路圧縮 + サイズ（またはランク）併合で高速化。"},
            {"level": 3, "text": "入力は 1-indexed。0-index と取り違えないこと。"}
        ],
        "distractors": [
            {"code": "NO_PATH_COMPRESSION", "desc": "経路圧縮なしで find が遅い"},
            {"code": "UNION_BY_RANK_BUG", "desc": "小を大にぶら下げる条件を逆にしてしまう"},
            {"code": "INDEX_BASE_MISMATCH", "desc": "1-indexed/0-indexed の取り違え"},
            {"code": "DELAY_UNION", "desc": "クエリ処理後に union してしまう順序ミス"}
        ],
        "witness": {
            "yes_count_t1": yes1, "no_count_t1": no1,
            "yes_count_t2": yes2, "no_count_t2": no2
        },
        "difficulty": {"score": 0.35, "basis": "DSU basics with path compression"},
        "tags": ["dsu", "graph", "beginner"],
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
    print(f"generated {n} UF items for {TODAY}")

if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv)>1 else 30
    main(n)
