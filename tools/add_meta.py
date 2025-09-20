import json, glob
for p in glob.glob("data/json/*.json"):
    with open(p,"r",encoding="utf-8-sig") as f: j=json.load(f)
    j.setdefault("version","1.0")
    j.setdefault("lang","ja")
    if j["id"].startswith("GCD_"):
        j.setdefault("task_family","gcd"); j.setdefault("answer_type","int")
    elif j["id"].startswith("BS_"):
        j.setdefault("task_family","binary_search"); j.setdefault("answer_type","bool")
    elif j["id"].startswith("INT_"):
        j.setdefault("task_family","interval_scheduling"); j.setdefault("answer_type","int")
    with open(p,"w",encoding="utf-8") as f: json.dump(j,f,ensure_ascii=False,indent=2)
print("patched meta fields")
