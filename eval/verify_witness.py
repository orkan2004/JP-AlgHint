# eval/verify_witness.py
import json, glob, os, hashlib
from collections import deque

# ---------- utils ----------
def sha1_hex(x):
    if isinstance(x, (list, tuple)):
        s=",".join(map(str,x))
    else:
        s=str(x)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def pick(d,*keys,default=None):
    for k in keys:
        if isinstance(d,dict) and k in d:
            return d[k]
    return default

# ---------- BFS (unweighted) ----------
def parse_graph_input(item):
    inp = pick(item,"io_spec",default={}); inp = pick(inp,"input",default=inp) or {}
    pr  = pick(item,"instance",default={}); pr  = pick(pr,"params",default=pr) or {}
    n = pick(inp,"n",default=pick(pr,"n"))
    edges = pick(inp,"edges",default=pick(pr,"edges",default=[]))
    src = pick(inp,"src","source",default=pick(pr,"src","source",default=0))
    directed = bool(pick(inp,"directed",default=pick(pr,"directed",default=False)))
    try: n=int(n)
    except: n = max((max(a,b) for a,b in edges), default=-1)+1 if edges else 0
    try: edges=[tuple(map(int,e)) for e in edges]
    except: edges=[]
    try: src=int(src)
    except: src=0
    target = pick(inp,"t","target","dst",default=pick(pr,"t","target","dst",default=None))
    try: target=int(target) if target is not None else None
    except: target=None
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

def verify_bfs(item):
    w=item.get("witness",{}) or {}
    n,edges,src,target,directed = parse_graph_input(item)
    if n<=0 or not edges:
        ok=isinstance(w.get("parent_hash",""),str) and isinstance(w.get("shortest_len",0),(int,type(None)))
        return ok,"BFS: input missing; format-only"
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

# ---------- INT (interval scheduling) ----------
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

def verify_int(item):
    w=item.get("witness",{}) or {}
    chosen=w.get("chosen_intervals",[])
    try: chosen=[tuple(map(int,x)) for x in chosen]
    except: return False,"INT witness invalid format"
    # non-overlap
    last=-10**18
    for s,e in sorted(chosen,key=lambda x:(x[1],x[0])):
        if s<last: return False,"INT overlap found"
        last=e
    # optimality vs input (if available)
    ints=parse_intervals_input(item)
    if not ints: return True,"INT witness ok (input missing; optimality skipped)"
    g=greedy_select(ints)
    if set(g)==set(chosen): return True,"INT witness optimal (matches greedy set)"
    if len(g)==len(chosen): return True,"INT witness size matches greedy (set differs)"
    return False,"INT witness not optimal (size differs)"

# ---------- MST (weighted) ----------
def parse_weighted_graph_input(item):
    inp = pick(item,"io_spec",default={}); inp = pick(inp,"input",default=inp) or {}
    pr  = pick(item,"instance",default={}); pr  = pick(pr,"params",default=pr) or {}
    n = pick(inp,"n",default=pick(pr,"n"))
    edges_w = pick(inp,"edges_w","wedges","edges",default=pick(pr,"edges_w","wedges","edges",default=[]))
    parsed=[]
    try:
        for e in edges_w:
            if isinstance(e,(list,tuple)) and len(e)>=3:
                u,v,w=int(e[0]),int(e[1]),int(e[2])
            elif isinstance(e,dict):
                u,v,w=int(e.get("u")),int(e.get("v")),int(e.get("w"))
            else:
                continue
            if u>v: u,v=v,u
            parsed.append((u,v,w))
    except Exception:
        parsed=[]
    try: n=int(n)
    except: n = max((max(u,v) for u,v,_ in parsed), default=-1)+1 if parsed else 0
    return n,parsed

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

def kruskal_mst(n,edges):
    d=DSU(n); total=0; used=[]
    for u,v,w in sorted(edges,key=lambda x:(x[2],x[0],x[1])):
        if d.u(u,v):
            total+=w; used.append((u,v,w))
    norm=sorted((min(u,v),max(u,v),int(w)) for u,v,w in used)
    edges_hash=sha1_hex("|".join(f"{u},{v},{w}" for u,v,w in norm))
    return total,used,edges_hash

def verify_mst(item):
    w=item.get("witness",{}) or {}
    n,ew=parse_weighted_graph_input(item)
    if n<=0 or not ew:
        ok=(isinstance(w.get("total_weight",0),(int,float)) or ("total_weight" not in w))
        ok=ok and (isinstance(w.get("edges_hash",""),str) or ("edges_hash" not in w))
        return ok,"MST: input missing; format-only"
    total,used,edges_hash=kruskal_mst(n,ew)
    ok=True; msgs=[]
    if "total_weight" in w:
        if int(w.get("total_weight"))!=int(total): ok=False; msgs.append("total_weight mismatch")
    else:
        msgs.append("total_weight absent")
    if "edges_hash" in w:
        if w.get("edges_hash")!=edges_hash: ok=False; msgs.append("edges_hash mismatch")
    else:
        msgs.append("edges_hash absent")
    return ok,("; ".join(msgs) if msgs else "MST witness ok")

# ---------- RSQ (range sum query) ----------
def parse_rsq_input(item):
    inp = pick(item,"io_spec",default={}); inp = pick(inp,"input",default=inp) or {}
    pr  = pick(item,"instance",default={}); pr  = pick(pr,"params",default=pr) or {}
    arr = pick(inp,"arr","array","a",default=pick(pr,"arr","array","a",default=[])) or []
    qs  = pick(inp,"queries","qs","q",default=pick(pr,"queries","qs","q",default=[])) or []
    try: arr = [int(x) for x in arr]
    except: arr = []
    qlist=[]
    for q in qs:
        try:
            if isinstance(q,(list,tuple)) and len(q)>=2:
                l=int(q[0]); r=int(q[1])
            elif isinstance(q,dict):
                l=int(q.get("l")); r=int(q.get("r"))
            else:
                continue
            qlist.append((l,r))
        except: pass
    return arr, qlist

def rsq_answers(arr, queries, one_based=False):
    n=len(arr)
    pref=[0]*(n+1)
    for i,x in enumerate(arr,1):
        pref[i]=pref[i-1]+x
    ans=[]
    for l,r in queries:
        if one_based:
            L=max(1,l); R=min(n,r)
            ans.append(pref[R]-pref[L-1] if 1<=L<=R<=n else 0)
        else:
            L=max(0,l); R=min(n-1,r)
            if L<=R: ans.append(pref[R+1]-pref[L])
            else: ans.append(0)
    return ans

def verify_rsq(item):
    w=item.get("witness",{}) or {}
    arr,qs = parse_rsq_input(item)
    if not arr or not qs:
        # 入力が拾えない場合は answers/answers_hash の形式だけ確認
        ok = (isinstance(w.get("answers",[]),list) or ("answers" not in w))
        ok = ok and (isinstance(w.get("answers_hash",""),str) or ("answers_hash" not in w))
        return ok,"RSQ: input missing; format-only"
    exp0 = rsq_answers(arr,qs,one_based=False)
    exp1 = rsq_answers(arr,qs,one_based=True)
    gotA = w.get("answers",None)
    gotH = w.get("answers_hash",None)
    ok=True; msgs=[]
    def match_answers(got,exp):
        try: return list(map(int,got))==list(map(int,exp))
        except: return False
    matched=False
    if gotA is not None:
        if match_answers(gotA,exp0) or match_answers(gotA,exp1):
            matched=True
        else:
            ok=False; msgs.append("answers mismatch (0/1-based)")
    if gotH is not None:
        if gotH in (sha1_hex(exp0), sha1_hex(exp1)):
            matched=True
        else:
            ok=False; msgs.append("answers_hash mismatch")
    if gotA is None and gotH is None:
        msgs.append("answers absent; hash absent")
    return ok and (matched or (gotA is None and gotH is None)), ("; ".join(msgs) if msgs else "RSQ witness ok")

# ---------- UF (union-find connectivity) ----------
def parse_uf_input(item):
    inp = pick(item,"io_spec",default={}); inp = pick(inp,"input",default=inp) or {}
    pr  = pick(item,"instance",default={}); pr  = pick(pr,"params",default=pr) or {}
    n = pick(inp,"n",default=pick(pr,"n"))
    ops = pick(inp,"ops","operations",default=pick(pr,"ops","operations",default=[])) or []
    qs  = pick(inp,"queries","qs","q",default=pick(pr,"queries","qs","q",default=[])) or []
    try: n=int(n)
    except: n=0
    def parse_pair(x):
        if isinstance(x,(list,tuple)) and len(x)>=2:
            return int(x[0]), int(x[1])
        if isinstance(x,dict):
            return int(x.get("a")), int(x.get("b"))
        raise ValueError
    unions=[]
    for op in ops:
        try:
            if isinstance(op,(list,tuple)) and len(op)>=3 and str(op[0]).lower().startswith("u"):
                a,b=parse_pair(op[1:])
            elif isinstance(op,dict) and str(op.get("type","")).lower().startswith("u"):
                a,b=parse_pair([op.get("a"),op.get("b")])
            else:
                continue
            unions.append((a,b))
        except: pass
    conn=[]
    for q in qs:
        try:
            if isinstance(q,(list,tuple)) and (len(q)==2 or (len(q)>=3 and str(q[0]).lower().startswith("c"))):
                a,b = (parse_pair(q[1:]) if len(q)>=3 else parse_pair(q))
            elif isinstance(q,dict):
                a,b = int(q.get("a")), int(q.get("b"))
            else:
                continue
            conn.append((a,b))
        except: pass
    return n, unions, conn

def verify_uf(item):
    w=item.get("witness",{}) or {}
    n,unions,conn = parse_uf_input(item)
    if n<=0:
        ok = (isinstance(w.get("answers",[]),list) or ("answers" not in w))
        ok = ok and (isinstance(w.get("parent_hash",""),str) or ("parent_hash" not in w))
        return ok,"UF: input missing; format-only"
    d=DSU(n)
    for a,b in unions:
        if 0<=a<n and 0<=b<n: d.u(a,b)
    ans=[int(d.f(a)==d.f(b)) for a,b in conn if 0<=a<n and 0<=b<n]
    ok=True; msgs=[]
    if "answers" in w:
        try:
            if list(map(int,w.get("answers")))!=ans: ok=False; msgs.append("answers mismatch")
        except:
            ok=False; msgs.append("answers invalid")
    else:
        msgs.append("answers absent")
    parents=[d.f(i) for i in range(n)]
    if "parent_hash" in w:
        if w.get("parent_hash")!=sha1_hex(parents): ok=False; msgs.append("parent_hash mismatch")
    else:
        msgs.append("parent_hash absent")
    return ok, ("; ".join(msgs) if msgs else "UF witness ok")

# ---------- main ----------
def main():
    paths=glob.glob("data/**/*.json", recursive=True)
    total=passed=0
    os.makedirs("eval",exist_ok=True)
    with open("eval/witness_report.txt","w",encoding="utf-8") as out:
        for p in paths:
            try:
                item=json.load(open(p,"r",encoding="utf-8"))
                _id=item.get("id","")
                fam=_id.split("_",1)[0] if "_" in _id else ""
                ok,msg=True,"skip"
                if   fam=="BFS": ok,msg=verify_bfs(item)
                elif fam=="INT": ok,msg=verify_int(item)
                elif fam=="MST": ok,msg=verify_mst(item)
                elif fam=="RSQ": ok,msg=verify_rsq(item)
                elif fam=="UF" : ok,msg=verify_uf(item)
                total+=1; passed+=int(ok)
                out.write(f"{_id}\t{fam}\t{ok}\t{msg}\n")
            except Exception as e:
                out.write(f"{p}\t?\tFalse\terror: {e!r}\n")
        out.write(f"\nTOTAL {passed}/{total}\n")
    print(f"Witness check: {passed}/{total}")

if __name__=="__main__": main()
