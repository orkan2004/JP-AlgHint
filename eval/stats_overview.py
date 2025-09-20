import glob, json, statistics as st
from collections import Counter, defaultdict
def load(p): 
    with open(p,"r",encoding="utf-8-sig") as f: return json.load(f)
by_task=Counter(); tags=Counter(); diffs=defaultdict(list); outs=Counter()
for p in glob.glob("data/json/*.json"):
    j=load(p); by_task[j["task"]]+=1
    for t in j.get("tags",[]): tags[t]+=1
    d=j.get("difficulty",{}).get("score"); 
    if d is not None: diffs[j["task"]].append(float(d))
    if j["task"].startswith("binary_search"):
        for t in j["tests"]: outs[t["out"].strip()]+=1
print("=== counts by task ==="); [print(k,v) for k,v in by_task.items()]
print("\n=== top tags ==="); [print(k,v) for k,v in tags.most_common(10)]
print("\n=== difficulty mean by task ==="); [print(k, round(st.mean(v),3)) for k,v in diffs.items()]
if outs:
    total=sum(outs.values()); print("\n=== BS output ratio ===")
    for k in ("1","0"): print(k, outs[k], f"{outs[k]/total:.1%}")
