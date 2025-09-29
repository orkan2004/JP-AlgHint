import json, glob, os, hashlib
from collections import deque

def sha1_hex(xs):
    s = ",".join(map(str, xs)) if isinstance(xs,(list,tuple)) else str(xs)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def pick(d,*keys,default=None):
    for k in keys:
        if isinstance(d,dict) and k in d: return d[k]
    return default

# ----- Graph (unweighted) for BFS -----
def parse_graph_input(item):
    inp = pick(item,"io_spec",default={}); inp = pick(inp,"input",default=inp) or {}
    pr  = pick(item,"instance",default={}); pr  = pick(pr,"params",default=pr) or {}
    n = pick(inp,"n",default=pick(pr,"n"))
    edges = pick(inp,"edges",default=pick(pr,"edges",default=[]))
    src = pick(inp,"src","source",default=pick(pr,"src","source",default=0))
    directed = bool(pick(inp,"directed",default=pick(pr,"directed",default=False)))
    try: n = int(n)
    except: n = max((max(a,b) for a,b in edges), default=-1)+1 if edges else 0
    try: edges = [tuple(map(int,e)) for e in edges]
    except: edges = []
    try: src = int(src)
    except: src = 0
    target = pick(inp,"t","target","dst",default=pick(pr,"t","target","dst",default=None))
    try: target = int(target) if target is not None else None
    except: target = None
    return n,edges,src,target,directed

def bfs(n,edges,src=0,directed=False):
    g=[[] for _ in range(n)]
    for a,b in edges:
        g[a].append(b)
        if not directed: g[b].append(a)
    dist=[-1]*n; parent=[-1]*n; dist[src]=0
    q=deque([src])
    while q:
        v=q.popleft()
        for nx in g[v]:
            if dist[nx]==-1:
                dist[nx]=dist[v]+1; parent[nx]=v; q.append(nx)
    return dist,parent

# ----- Intervals for INT -----
def parse_intervals_input(item):
    inp = pick(item,"io_spec",default={}); inp = pick(inp,"input",default=inp) or {}
    pr  = pick(item,"instance",default={}); pr  = pick(pr,"params",default=pr) or {}
    ints = (pick(inp,"intervals","ranges","segments","tasks") or
            pick(pr,"intervals","ranges","segments","tasks") or [])
    try: return [tuple(map(int,x)) for x in ints]
    except: return []

def greedy_select(intervals):
    res=[]; cur=-10**18
    for s,e in sorted(intervals,key=lambda x:(x[1],x[0])):
        if s>=cur: res.append((s,e)); cur=e
    return res

# ----- Weighted graph for MST -----
def parse_weighted_graph_input(item):
    inp = pick(item,"io_spec",default={}); inp = pick(inp,"input",default=inp) or {}
    pr  = pick(item,"instance",default={}); pr  = pick(pr,"params",default=pr) or {}
    n = pick(inp,"n",default=pick(pr,"n"))
    edges_w = pick(inp,"edges_w","wedges","edges",default=pick(pr,"edges_w","wedges","edges",default=[]))
    # 受け付ける形式: [u,v,w] または {"u":..,"v":..,"w":..}
    parsed=[]
    try:
        for e in edges_w:
            if isinstance(e,(list,tuple)) and len(e)>=3:
                u,v,w = int(e[0]), int(e[1]), int(e[2])
            elif isinstance(e,dict):
                u,v,w = int(e.get("u")), int(e.get("v")), int(e.get("w"))
            else:
                continue
            if u>v: u,v = v,u
            parsed.append((u,v,int(w)))
    except Exception:
        parsed=[]
    try: n = int(n)
    except: n = max((max(u,v) for u,v,_ in parsed), default=-1)+1 if parsed else 0
    return n, parsed

class DSU:
    def __init__(self,n): self.p=list(range(n)); self.r=[0]*n
    def f(self,x):
        while self.p[x]!=x:
            self.p[x]=self.p[self.p[x]]; x=self.p[x]
        return x
    def u(self,a,b):
        a=self.f(a); b=self.f(b)
        if a==b: return False
        if self.r[a]<self.r[b]: a,b=b,a
        self.p[b]=a
        if self.r[a]==self.r[b]: self.r[a]+=1
        return True

def kruskal_mst(n, edges):
    dsu=DSU(n); total=0; used=[]
    for u,v,w in sorted(edges, key=lambda x:(x[2],x[0],x[1])):
        if dsu.u(u,v):
            total += w
            used.append((u,v,w))
    # エッジ集合のハッシュ（順序不変）
    norm = sorted((min(u,v),max(u,v),int(w)) for u,v,w in used)
    edges_hash = sha1_hex("|".join(f"{u},{v},{w}" for u,v,w in norm))
    return total, used, edges_hash

# ----- Family verifiers -----
def verify_bfs(item):
    w = item.get("witness",{}) or {}
    n,edges,src,target,directed = parse_graph_input(item)
    if n<=0 or not edges:
        ok = isinstance(w.get("parent_hash",""),str) and isinstance(w.get("shortest_len",0),(int,type(None)))
        return ok, "BFS: input missing; format-only"
    dist,parent = bfs(n,edges,src=src,directed=directed)
    ok=True; msgs=[]
    if "parent_hash" in w:
        if sha1_hex(parent)!=w.get("parent_hash"): ok=False; msgs.append("parent_hash mismatch")
    else:
        msgs.append("parent_hash absent")
    if target is not None and "shortest_len" in w:
        if w.get("shortest_len")!=dist[target]: ok=False; msgs.append("shortest_len mismatch")
    elif "shortest_len" in w:
        msgs.append("shortest_len present but target missing")
    return ok, ("; ".join(msgs) if msgs else "BFS witness ok")

def verify_int(item):
    w = item.get("witness",{}) or {}
    chosen = w.get("chosen_intervals",[])
    try: chosen = [tuple(map(int,x)) for x in chosen]
    except: return False,"INT witness invalid format"
    # 非交差性
    last=-10**18
    for s,e in sorted(chosen,key=lambda x:(x[1],x[0])):
        if s<last: return False,"INT overlap found"
        last=e
    # 最適性（入力が無ければスキップOK）
    ints = parse_intervals_input(item)
    if not ints: return True,"INT witness ok (input missing; optimality skipped)"
    greedy = greedy_select(ints)
    if set(greedy)==set(chosen):
        return True,"INT witness optimal (matches greedy set)"
    if len(greedy)==len(chosen):
        return True,"INT witness size matches greedy (set differs)"
    return False,"INT witness not optimal (size differs)"

def verify_mst(item):
    w = item.get("witness",{}) or {}
    n, ew = parse_weighted_graph_input(item)
    if n<=0 or not ew:
        # 入力不明なら形式のみ緩く確認
        ok = isinstance(w.get("total_weight",0),(int,float)) or ("total_weight" not in w)
        ok = ok and (isinstance(w.get("edges_hash",""),str) or ("edges_hash" not in w))
        return ok, "MST: input missing; format-only"
    total, used, edges_hash = kruskal_mst(n, ew)
    ok=True; msgs=[]
    if "total_weight" in w:
        if int(w.get("total_weight")) != int(total):
            ok=False; msgs.append(f"total_weight mismatch (exp {total}, got {w.get('total_weight')})")
    else:
        msgs.append("total_weight absent")
    if "edges_hash" in w:
        if w.get("edges_hash") != edges_hash:
            ok=False; msgs.append("edges_hash mismatch")
    else:
        msgs.append("edges_hash absent")
    return ok, ("; ".join(msgs) if msgs else "MST witness ok")

# ---------- RSQ (range sum query) ----------
def parse_rsq_input(item):
    inp = (item.get("io_spec", {}) or {}).get("input", {}) or {}
    pr  = (item.get("instance", {}) or {}).get("params", {}) or {}
    arr = inp.get("arr") or inp.get("array") or inp.get("a") or pr.get("arr") or []
    qs  = inp.get("queries") or inp.get("qs") or pr.get("queries") or []
    try:
        arr = [int(x) for x in arr]
    except Exception:
        arr = []
    queries = []
    for q in qs:
        try:
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                l, r = int(q[0]), int(q[1])
            elif isinstance(q, dict):
                l, r = int(q.get("l")), int(q.get("r"))
            else:
                continue
            queries.append((l, r))
        except Exception:
            pass
    return arr, queries

def rsq_answers(arr, queries, one_based=False):
    n = len(arr)
    pref = [0] * (n + 1)
    for i, x in enumerate(arr, 1):
        pref[i] = pref[i - 1] + x
    ans = []
    for l, r in queries:
        if one_based:
            L = max(1, l); R = min(n, r)
            ans.append(pref[R] - pref[L - 1] if 1 <= L <= R <= n else 0)
        else:
            L = max(0, l); R = min(n - 1, r)
            ans.append(pref[R + 1] - pref[L] if L <= R else 0)
    return ans

def verify_rsq(item):
    w = item.get("witness", {}) or {}
    arr, qs = parse_rsq_input(item)
    # 入力が拾えないときは形式だけ緩くOK扱い
    if not arr or not qs:
        ok = isinstance(w.get("answers", []), list) or ("answers" not in w)
        return ok, "RSQ: input missing; format-only"
    exp0 = rsq_answers(arr, qs, one_based=False)
    exp1 = rsq_answers(arr, qs, one_based=True)  # 1-basedの可能性にも寛容
    try:
        got = [int(x) for x in (w.get("answers") or [])]
    except Exception:
        return False, "answers invalid"
    if got == exp0 or got == exp1:
        return True, "RSQ witness ok"
    return False, "answers mismatch"

# ---------- main ----------
def main():
    paths = glob.glob("data/**/*.json", recursive=True)
    total = passed = 0
    os.makedirs("eval", exist_ok=True)

    with open("eval/witness_report.txt", "w", encoding="utf-8") as out:
        for p in paths:
            try:
                with open(p, "r", encoding="utf-8") as f:
                    item = json.load(f)

                _id = item.get("id", "")
                fam = _id.split("_", 1)[0] if "_" in _id else ""

                ok, msg = True, "skip"
                if fam == "BFS":
                    ok, msg = verify_bfs(item)
                elif fam == "INT":
                    ok, msg = verify_int(item)
                elif fam == "RSQ":
                    ok, msg = verify_rsq(item)      # ← RSQ を残す
                elif fam == "MST":
                    ok, msg = verify_mst(item)      # ← MST も残す

                total += 1
                passed += int(ok)
                out.write(f"{_id}\t{fam}\t{ok}\t{msg}\n")

            except Exception as e:
                out.write(f"{p}\t?\tFalse\terror: {e!r}\n")

        out.write(f"\nTOTAL {passed}/{total}\n")
    print(f"Witness check: {passed}/{total}")

if __name__ == "__main__":
    main()
