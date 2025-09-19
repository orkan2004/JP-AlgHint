import sys, math
def solve(data: str) -> str:
    a,b = map(int, data.strip().split())
    return str(math.gcd(a,b))
if __name__ == "__main__":
    print(solve(sys.stdin.read()))
