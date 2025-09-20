import glob, json, math
from collections import deque

def load(p):
    with open(p,"r",encoding="utf-8-sig") as f: return json.load(f)

def check_gcd(j,p,errs):
    import math
    for t in j["tests"]:
        a,b = map(int, t["in"].strip().split())
        if t["out"].strip()!=str(math.gcd(a,b)):
            errs.append(f"{p}: gcd wrong")

def parse_bs(s):
    L=s.strip().splitlines()
    n=int(L[0]); arr=list(map(int,L[1].split())); x=int(L[2])
    return n,arr,x

def check_bs(j,p,errs):
    import bisect
    outs=set()
    for t in j["tests"]:
        n,arr,x=parse_bs(t["in"])
        if n!=len(arr): errs.append(f"{p}: n!=len(arr)")
        if any(arr[i]>arr[i+1] for i in range(len(arr)-1)): errs.append(f"{p}: not sorted")
        i=bisect.bisect_left(arr,x); out="1" if i<n and arr[i]==x else "0"; outs.add(out)
        if t["out"].strip()!=out: errs.append(f"{p}: wrong result")
    if len(outs)==1: errs.append(f"{p}: tests lack both outcomes")

def parse_bfs_input(s: str):
    it = iter(s.strip().split())
    n=int(next(it)); m=int(next(it)); s0=int(next(it)); t0=int(next(it))
    edges=[]
    for _ in range(m):
        u=int(next(it)); v=int(next(it)); edges.append((u,v))
    return n,edges,s0,t0

def bfs_len(n, edges, s, t):
    g=[[] for _ in range(n+1)]
    for u,v in edges:
        g[u].append(v); g[v].append(u)
    dist=[-1]*(n+1); q=deque([s]); dist[s]=0
    while q:
        v=q.popleft()
        for to in g[v]:
            if dist[to]==-1:
                dist[to]=dist[v]+1
                q.append(to)
    return dist[t]

def check_bfs(j,p,errs):
    has_unreach=False; has_reach=False
    for t in j["tests"]:
        n,edges,s0,t0 = parse_bfs_input(t["in"])
        d = bfs_len(n,edges,s0,t0)
        if str(d)!=t["out"].strip():
            errs.append(f"{p}: wrong BFS distance")
        if d==-1: has_unreach=True
        else: has_reach=True
    if not (has_unreach and has_reach):
        errs.append(f"{p}: BFS tests should include both reachable and unreachable")

def main():
    errs=[]
    for p in glob.glob("data/json/*.json"):
        j=load(p); task=j.get("task","")
        if task=="gcd": check_gcd(j,p,errs)
        elif task.startswith("binary_search"): check_bs(j,p,errs)
        elif task.startswith("bfs_"): check_bfs(j,p,errs)
    if errs: print("LINTER: FAIL\n"+"\n".join(errs))
    else: print("LINTER: OK")

if __name__=="__main__": main()
