import sys, bisect

def solve(data: str) -> str:
    it = iter(data.strip().splitlines())
    n = int(next(it))
    arr = list(map(int, next(it).split()))
    x = int(next(it))
    i = bisect.bisect_left(arr, x)
    return "1" if i < n and arr[i] == x else "0"

if __name__ == "__main__":
    print(solve(sys.stdin.read()))
