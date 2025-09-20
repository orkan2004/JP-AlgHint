import json, random, time
from pathlib import Path

TODAY = time.strftime("%Y%m%d")
def new_id(i): return f"MST_{TODAY}_{i:05d}"

class DSU:
    def __init__(self, n):
        self.p=list(range(n+1)); self.sz=[1]*(n+1)
    def find(self,x):
        while self.p[x]!=x:
            self.p[x]=self.p[self.p[x]]; x=self.p[x]
        return x
    def unite(self,a,b):
        a=self.find(a); b=self.find(b)
        if a==b: return False
        if self.sz[a]<self.sz[b]: a,b=b,a
        self.p[b]=a; self.sz[a]+=self.sz[b]; return True

def kruskal(n, edges):
    es = [(w,u,v,i) for i,(u,v,w) in enumerate(edges)]
    es.sort()
    dsu=DSU(n); total=0; used=[]
    for w,u,v,i in es:
        if dsu.unite(u,v):
            total+=w; used.append(i)
            if len(used)==n-1: break
    return (total if len(used)==n-1 else -1), used

def connected_base(n, r):
    edges=set()
    for v in range(2,n+1):
        u=r.randint(1,v-1)
        if u>v: u,v=v,u
        edges.add((u,v))
    extra=r.randint(n,2*n)
    for _ in range(extra):
        u,v=r.sample(range(1,n+1),2)
        if u>v: u,v=v,u
        edges.add((u,v))
    return list(edges)

def weightify(pairs, r, tie=False):
    E=[]
    for u,v in pairs:
        if tie and r.random()<0.35: w=r.randint(50,60)
        else: w=r.randint(1,1000)
        E.append((u,v,w))
    return E

def build_input(n, edges):
    lines=[f"{n} {len(edges)}"]+[f"{u} {v} {w}" for u,v,w in edges]
    return "\n".join(lines)+"\n"

def gen_one(r,i):
    n=r.randint(12,50)
    base=connected_base(n,r)
    E1=weightify(base,r,False); w1,ce1=kruskal(n,E1)
    E2=weightify(base,r,True);  w2,ce2=kruskal(n,E2)
    assert w1!=-1 and w2!=-1
    return {
        "id": new_id(i), "version":"1.0","lang":"ja",
        "task_family":"mst_kruskal","answer_type":"int","task":"mst_kruskal",
        "statement_ja":"重み付き無向グラフの最小全域木の重み合計を求めよ。連結でない場合は -1。",
        "io_spec":{"input":"n m\\n(u v w)×m（1-indexed）","output":"MST重み合計または -1"},
        "instance":{"seed":i,"template_id":"MST_T1","params":{"n":n}},
        "tests":[{"in":build_input(n,E1),"out":f"{w1}\n"},{"in":build_input(n,E2),"out":f"{w2}\n"}],
        "reference":{"py":"ref/py/mst_kruskal.py"},
        "hints":[
            {"level":1,"text":"辺を重み昇順に並べ、サイクルを作らないものだけ採用（Kruskal）。"},
            {"level":2,"text":"サイクル判定にUnion-Findを使う。採用数が n-1 に達したら終了。"},
            {"level":3,"text":"重みが同じでも動くように比較は w のみ。"}
        ],
        "distractors":[
            {"code":"WRONG_SORT_KEY","desc":"w以外でソート"},
            {"code":"CYCLE_FILTER_MISS","desc":"サイクル検出を忘れる"},
            {"code":"UNION_ORDER_BUG","desc":"併合の大小関係を誤る"}
        ],
        "witness":{"mst_weight_t1":w1,"chosen_edges_t1":ce1,"mst_weight_t2":w2,"chosen_edges_t2":ce2},
        "difficulty":{"score":0.45,"basis":"Kruskal + DSU"},
        "tags":["graph","mst","dsu","intermediate"],
        "license":"CC BY-SA 4.0 (texts) / MIT (code)"
    }

def main(n=30):
    r=random.Random(20240920)
    Path("data/json").mkdir(parents=True, exist_ok=True)
    for i in range(1,n+1):
        item=gen_one(r,i)
        path=Path("data/json")/f"{item['id']}.json"
        with open(path,"w",encoding="utf-8") as f:
            json.dump(item,f,ensure_ascii=False,indent=2)
    print(f"generated {n} MST items for {TODAY}")
if __name__=="__main__":
    import sys
    n=int(sys.argv[1]) if len(sys.argv)>1 else 30
    main(n)
