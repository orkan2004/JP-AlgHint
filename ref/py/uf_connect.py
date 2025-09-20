import sys

class DSU:
    def __init__(self, n):
        self.p = list(range(n+1))
        self.sz = [1]*(n+1)
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x
    def unite(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb: return False
        if self.sz[ra] < self.sz[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        self.sz[ra] += self.sz[rb]
        return True
    def same(self, a, b):
        return self.find(a) == self.find(b)

def solve(data: str) -> str:
    it = iter(data.strip().split())
    n = int(next(it)); m = int(next(it)); q = int(next(it))
    dsu = DSU(n)
    for _ in range(m):
        u = int(next(it)); v = int(next(it))
        dsu.unite(u, v)
    out = []
    for _ in range(q):
        a = int(next(it)); b = int(next(it))
        out.append("1" if dsu.same(a, b) else "0")
    return "\n".join(out) + "\n"

if __name__ == "__main__":
    print(solve(sys.stdin.read()), end="")
