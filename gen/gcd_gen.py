import os, json, math, random, time
from pathlib import Path

TODAY = time.strftime("%Y%m%d")  # 例: 20250919

def new_id(seq:int): 
    return f"GCD_{TODAY}_{seq:05d}"

def make_item(a:int,b:int,seq:int)->dict:
    g = math.gcd(a,b)
    return {
      "id": new_id(seq),
      "task": "gcd",
      "statement_ja": "整数 a, b が与えられる。a と b の最大公約数を求めよ。",
      "io_spec": {"input":"a b","output":"gcd(a,b)"},
      "instance": {"seed": seq, "template_id":"GCD_T1", "params":{"a":a,"b":b}},
      "tests": [{"in": f"{a} {b}\n", "out": f"{g}\n"}],
      "reference": {"py":"ref/py/gcd.py"},
      "hints": [
        {"level":1,"text":"ユークリッドの互除法を思い出そう。"},
        {"level":2,"text":"gcd(a,b)=gcd(b, a mod b) をb=0まで繰り返す。"},
        {"level":3,"text":"while b: a,b=b,a%b。最後のaが答え。"}
      ],
      "distractors":[{"code":"MOD_NEGATIVE","desc":"負の剰余の扱いを誤る"}],
      "witness":{"opt_value": g},
      "difficulty":{"score":0.2,"basis":"ループ回数が小さい"},
      "tags":["number","math","beginner"],
      "license":"CC BY-SA 4.0 (texts) / MIT (code)"
    }

def main(n=30, low=2, high=10**6):
    Path("data/json").mkdir(parents=True, exist_ok=True)
    r = random.Random(31415)
    for i in range(1, n+1):
        a = r.randrange(low, high)
        b = r.randrange(low, high)
        item = make_item(a,b,i)
        path = Path("data/json") / f"{item['id']}.json"
        with open(path, "w", encoding="utf-8") as f:  # BOMなし
            json.dump(item, f, ensure_ascii=False, indent=2)
    print(f"generated {n} items for {TODAY}")

if __name__=="__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv)>1 else 30
    main(n)
