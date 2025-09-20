import sys
from collections import deque

def solve(data: str) -> str:
    it = iter(data.strip().split())
    n = int(next(it)); m = int(next(it)); s = int(next(it)); t = int(next(it))
    g = [[] for _ in range(n + 1)]
    for _ in range(m):
        u = int(next(it)); v = int(next(it))
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
    return f"{dist[t]}\n"

if __name__ == "__main__":
    print(solve(sys.stdin.read()), end="")
