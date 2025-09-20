import sys

def solve(data: str) -> str:
    it = iter(data.strip().split())
    n = int(next(it)); q = int(next(it))
    a = [int(next(it)) for _ in range(n)]
    pref = [0]*(n+1)
    for i in range(n):
        pref[i+1] = pref[i] + a[i]
    out = []
    for _ in range(q):
        l = int(next(it)); r = int(next(it))  # 1-indexed, inclusive
        out.append(str(pref[r] - pref[l-1]))
    return "\n".join(out) + "\n"

if __name__ == "__main__":
    print(solve(sys.stdin.read()), end="")
