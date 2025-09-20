import sys

def solve(data: str) -> str:
    it = iter(data.strip().split())
    n = int(next(it)); W = int(next(it))
    w = []; v = []
    for _ in range(n):
        w.append(int(next(it))); v.append(int(next(it)))

    # 0/1 knap DP（容量基準 O(nW)）
    dp = [0] * (W + 1)
    for i in range(n):
        wi, vi = w[i], v[i]
        for cap in range(W, wi - 1, -1):
            cand = dp[cap - wi] + vi
            if cand > dp[cap]:
                dp[cap] = cand
    return f"{dp[W]}\n"

if __name__ == "__main__":
    print(solve(sys.stdin.read()), end="")
