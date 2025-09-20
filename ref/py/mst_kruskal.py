import sys
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
def solve(data: str) -> str:
    it=iter(data.strip().split())
    n=int(next(it)); m=int(next(it))
    es=[]
    for _ in range(m):
        u=int(next(it)); v=int(next(it)); w=int(next(it))
        es.append((w,u,v))
    es.sort()
    dsu=DSU(n); total=0; used=0
    for w,u,v in es:
        if dsu.unite(u,v):
            total+=w; used+=1
            if used==n-1: break
    return f"{total}\n" if used==n-1 else "-1\n"
if __name__=="__main__":
    print(solve(sys.stdin.read()), end="")
