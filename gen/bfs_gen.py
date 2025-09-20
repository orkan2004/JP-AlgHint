import json, random, time
from pathlib import Path
from collections import deque

TODAY = time.strftime("%Y%m%d")
def new_id(i): return f"BFS_{TODAY}_{i:05d}"

def bfs_len(n, edges, s, t):
    g = [[] for _ in range(n + 1)]
    for u, v in edges:
        g[u].append(v); g[v].append(u)
    dist = [-1] * (n + 1)
    q = deque([s]); dist[s] = 0
    while q:
        v = q.popleft()
        if v == t: break
        for to in g[v]:
            if dist[to] == -1:
                dist[to] = dist[v] + 1
                q.append(to)
    return dist[t]

def build_input(n, edges, s, t):
    lines = [f"{n} {len(edges)} {s} {t}"]
    for u, v in edges:
        lines.append(f"{u} {v}")
    return "\n".join(lines) + "\n"

def connected_graph(n, r):
    # ランダム木 + 追加辺
    E = set()
    for v in range(2, n + 1):
        u = r.randint(1, v - 1)
        if u > v: u, v = v, u
        E.add((u, v))
    extra = r.randint(n, 2 * n)
    for _ in range(extra):
        u, v = r.sample(range(1, n + 1), 2)
        if u > v: u, v = v, u
        if u != v: E.add((u, v))
    return E

def two_components(n, r):
    # 2連結成分を作る（到達不能ケース用）
    split = r.randint(2, n - 2)
    A = list(range(1, split + 1))
    B = list(range(split + 1, n + 1))
    E = set()

    def add_tree(nodes):
        for i in range(1, len(nodes)):
            u = r.choice(nodes[:i]); v = nodes[i]
            if u > v: u, v = v, u
            E.add((u, v))

    def add_extra(nodes):
        k = r.randint(len(nodes), 2 * len(nodes))
        for _ in range(k):
            u, v = r.sample(nodes, 2)
            if u > v: u, v = v, u
            E.add((u, v))

    add_tree(A); add_tree(B)
    add_extra(A); add_extra(B)
    s = r.choice(A); t = r.choice(B)
    return E, s, t

def gen_one(r, i):
    n = r.randint(12, 50)

    # test1: 到達可能
    E1 = connected_graph(n, r)
    s1, t1 = r.sample(range(1, n + 1), 2)
    while s1 == t1:
        s1, t1 = r.sample(range(1, n + 1), 2)
    d1 = bfs_len(n, E1, s1, t1)
    if d1 == -1:
        # まれに分断されたら辺を1本足して繋ぐ
        u, v = r.sample(range(1, n + 1), 2)
        if u > v: u, v = v, u
        E1.add((u, v))
        d1 = bfs_len(n, E1, s1, t1)
    assert d1 != -1
    tcase1 = {"in": build_input(n, E1, s1, t1), "out": f"{d1}\n"}

    # test2: 到達不能
    E2, s2, t2 = two_components(n, r)
    d2 = bfs_len(n, E2, s2, t2)
    assert d2 == -1
    tcase2 = {"in": build_input(n, E2, s2, t2), "out": "-1\n"}

    return {
        "id": new_id(i),
        "version": "1.0",
        "lang": "ja",
        "task_family": "bfs_shortest",
        "answer_type": "int",
        "task": "bfs_shortest",
        "statement_ja": "無向グラフが与えられる。s から t への最短距離（辺数）を出力せよ。到達不能なら -1。",
        "io_spec": {"input": "n m s t\\n(u v)×m（1-indexed, 無向）", "output": "最短距離または -1"},
        "instance": {"seed": i, "template_id": "BFS_T1", "params": {"n": n}},
        "tests": [tcase1, tcase2],
        "reference": {"py": "ref/py/bfs_shortest.py"},
        "hints": [
            {"level": 1, "text": "無重みグラフの最短路は BFS で求まる。"},
            {"level": 2, "text": "dist 配列を -1 で初期化し、dist[s]=0。未訪問のみキューに入れる。"},
            {"level": 3, "text": "隣接 to の距離は dist[v]+1。t に到達したら距離が答え。"}
        ],
        "distractors": [
            {"code": "VISIT_MARK_LATE", "desc": "訪問印を遅く付けて多重プッシュ"},
            {"code": "OFF_BY_ONE", "desc": "距離 +1 や初期値の扱いを誤る"},
            {"code": "INDEX_BASE_MISMATCH", "desc": "1-indexed/0-indexed を取り違え"}
        ],
        "witness": {"shortest_len_t1": d1, "shortest_len_t2": d2},
        "difficulty": {"score": 0.4, "basis": "BFS on unweighted graph"},
        "tags": ["graph", "simulation", "beginner"],
        "license": "CC BY-SA 4.0 (texts) / MIT (code)"
    }

def main(n=30):
    r = random.Random(20240920)
    Path("data/json").mkdir(parents=True, exist_ok=True)
    for i in range(1, n + 1):
        item = gen_one(r, i)
        path = Path("data/json") / f"{item['id']}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(item, f, ensure_ascii=False, indent=2)
    print(f"generated {n} BFS items for {TODAY}")

if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    main(n)
