import glob, json, math
def load(p): 
    with open(p,"r",encoding="utf-8-sig") as f: return json.load(f)
def check_gcd(j,p,errs):
    for t in j["tests"]:
        a,b = map(int, t["in"].strip().split()); g = math.gcd(a,b)
        if t["out"].strip()!=str(g): errs.append(f"{p}: gcd wrong")
def parse_bs(s):
    L=s.strip().splitlines(); n=int(L[0]); arr=list(map(int,L[1].split())); x=int(L[2]); return n,arr,x
def check_bs(j,p,errs):
    outs=set()
    for t in j["tests"]:
        n,arr,x=parse_bs(t["in"])
        if n!=len(arr): errs.append(f"{p}: n!=len(arr)")
        if any(arr[i]>arr[i+1] for i in range(len(arr)-1)): errs.append(f"{p}: not sorted")
        import bisect; i=bisect.bisect_left(arr,x); out="1" if i<n and arr[i]==x else "0"; outs.add(out)
        if t["out"].strip()!=out: errs.append(f"{p}: wrong result")
    if len(outs)==1: errs.append(f"{p}: tests lack both outcomes")
def main():
    errs=[]
    for p in glob.glob("data/json/*.json"):
        j=load(p); task=j.get("task","")
        if task=="gcd": check_gcd(j,p,errs)
        elif task.startswith("binary_search"): check_bs(j,p,errs)
    if errs: print("LINTER: FAIL\n"+"\n".join(errs))
    else: print("LINTER: OK")
if __name__=="__main__": main()
