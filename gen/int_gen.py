import json, random, time
from pathlib import Path
TODAY=time.strftime("%Y%m%d")
def new_id(i): return f"INT_{TODAY}_{i:05d}"
def opt(seg):
    seg=sorted([(s,t,i) for i,(s,t) in enumerate(seg)], key=lambda x:(x[1],x[0]))
    cur=-10**18; chosen=[]
    for s,t,i in seg:
        if s>=cur: chosen.append(i); cur=t
    return len(chosen)
def mk_case(seg):
    s=[f"{len(seg)}"]+[f"{a} {b}" for a,b in seg]; s="\n".join(s)+"\n"
    return {"in":s, "out":f"{opt(seg)}\n"}
def gen_one(r,i):
    n=r.randint(8,40); seg=[(s:=r.randint(0,900), s+r.randint(1,200)) for _ in range(n)]
    t1=mk_case(seg)
    seg2=list(seg)
    if len(seg2)>=2: seg2[-2]=(min(seg2[-2][1]-1, seg2[-2][0]), seg2[-1][1])  # 同終了時刻
    t2=mk_case(seg2)
    return {
      "id": new_id(i), "version":"1.0", "lang":"ja",
      "task_family":"interval_scheduling", "answer_type":"int",
      "task":"interval_scheduling",
      "statement_ja":"開始時刻 s_i, 終了時刻 t_i の n 個の仕事から、互いに重ならない最大数を選べ。",
      "io_spec":{"input":"n\\n(s t)×n","output":"選べる最大個数"},
      "instance":{"seed":i,"template_id":"INT_T1","params":{"n":n}},
      "tests":[t1,t2], "reference":{"py":"ref/py/int_sched.py"},
      "hints":[
        {"level":1,"text":"終了時刻が早い仕事から選ぶ貪欲法。"},
        {"level":2,"text":"終了時刻で昇順ソートし、可能なら採用して終了時刻を更新。"},
        {"level":3,"text":"同タイのとき開始が早い順でも最適性は保たれる。"}
      ],
      "distractors":[
        {"code":"TIE_BREAK_WRONG","desc":"終了時刻同点の処理を誤る"},
        {"code":"END_EXCLUSIVE_CONFUSION","desc":"重なり判定で >= と > を取り違え"},
        {"code":"LOWER_UPPER_SWAP","desc":"開始・終了の大小を取り違え"}
      ],
      "witness":{},
      "difficulty":{"score":0.35,"basis":"greedy with tie-break"},
      "tags":["greedy","simulation","beginner"],
      "license":"CC BY-SA 4.0 (texts) / MIT (code)"
    }
def main(n=30):
    Path("data/json").mkdir(parents=True, exist_ok=True); r=random.Random(20240920)
    for i in range(1,n+1):
        item=gen_one(r,i); path=Path("data/json")/f"{item['id']}.json"
        with open(path,"w",encoding="utf-8") as f: json.dump(item,f,ensure_ascii=False,indent=2)
    print(f"generated {n} INT items for {TODAY}")
if __name__=="__main__":
    import sys; n=int(sys.argv[1]) if len(sys.argv)>1 else 30; main(n)
