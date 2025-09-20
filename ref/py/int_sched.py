import sys
def solve(data:str)->str:
    it=iter(data.strip().splitlines()); n=int(next(it)); seg=[]
    for _ in range(n): s,t=map(int,next(it).split()); seg.append((s,t))
    seg.sort(key=lambda x:(x[1],x[0])); cur=-10**18; cnt=0
    for s,t in seg:
        if s>=cur: cnt+=1; cur=t
    return str(cnt)
if __name__=="__main__": print(solve(sys.stdin.read()))
