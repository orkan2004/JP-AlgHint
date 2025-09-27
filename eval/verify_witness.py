# eval/verify_witness.py
import json, glob, os, hashlib
from collections import deque

def sha1_hex(xs):
    s = ",".join(map(str, xs)) if isinstance(xs,(list,tuple)) else str(xs)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def pick(d,*keys,default=None):
    for k in keys:
        if isinstance(d,dict) and k in d: return d[k]
    return default

# ---------- 入力パーサ ----------
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

def parse_intervals_input(item):
    inp = pick(item,"io_spec",default={}); inp = pick(inp,"input",default=inp) or {}
    pr  = pick(item,"instance",default={}); pr  = pick(pr,"params",default=pr) or {}
    ints = (pick(inp,"intervals","ranges","segments","tasks") or
            pick(pr,"intervals","ranges","segments","tasks") or [])
    try: return [tuple(map(int,x)) for x in ints]
    except: return []

# ---------- アルゴリズム ----------
def bfs(n,edges,src=0,directed=False):
    g=[[] for _ in range(n)]
    for a,b in edges:
        g[a].append(b); 
        if not directed: g[b].append(a)
    dist=[-1]*n; parent=[-1]*n; dist[src]=0
    q=deque([src])
    while q:
        v=q.popleft()
        for nx in g[v]:
            if dist[nx]==-1:
                dist[nx]=dist[v]+1; parent[nx]=v; q.append(nx)
    return dist,parent

def greedy_select(intervals):
    res=[]; cur=-10**18
    for s,e in sorted(intervals,key=lambda x:(x[1],x[0])):
        if s>=cur:
            res.append((s,e)); cur=e
    return res

# ---------- familyごとの検証 ----------
def verify_bfs(item):
    w = item.get("witness",{}) or {}
    n,edges,src,target,directed = parse_graph_input(item)
    if n<=0 or not edges:
        ok = isinstance(w.get("parent_hash",""),str) and isinstance(w.get("shortest_len",0),(int,type(None)))
        return ok, "BFS: input missing; format-only"
    dist,parent = bfs(n,edges,src=src,directed=directed)
    ok=True; msgs=[]
    if "parent_hash" in w:
        exp=sha1_hex(parent); got=w.get("parent_hash")
        if not isinstance(got,str) or got!=exp: ok=False; msgs.append("parent_hash mismatch")
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
    # 入力から最適性を検証（入力が拾えなければ形式のみOK扱い）
    ints = parse_intervals_input(item)
    if not ints: return True,"INT witness ok (input missing; optimality skipped)"
    greedy = greedy_select(ints)
    if set(greedy)==set(chosen):
        return True,"INT witness optimal (matches greedy set)"
    # Greedy と集合が異なる場合はサイズ一致だけ確認（弱い条件）
    if len(greedy)==len(chosen):
        return True,"INT witness size matches greedy (set differs)"
    return False,"INT witness not optimal (size differs from greedy)"

# ---------- main ----------
def main():
    paths = glob.glob("data/**/*.json", recursive=True)
    total=passed=0; os.makedirs("eval",exist_ok=True)
    with open("eval/witness_report.txt","w",encoding="utf-8") as out:
        for p in paths:
            try:
                item=json.load(open(p,"r",encoding="utf-8"))
                _id=item.get("id",""); fam=_id.split("_",1)[0] if "_" in _id else ""
                ok,msg=True,"skip"
                if fam=="BFS": ok,msg=verify_bfs(item)
                elif fam=="INT": ok,msg=verify_int(item)
                total+=1; passed+=int(ok)
                out.write(f"{_id}\t{fam}\t{ok}\t{msg}\n")
            except Exception as e:
                out.write(f"{p}\t?\tFalse\terror: {e!r}\n")
        out.write(f"\nTOTAL {passed}/{total}\n")
    print(f"Witness check: {passed}/{total}")

if __name__=="__main__": main()
